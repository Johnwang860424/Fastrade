from datetime import datetime
from dotenv import load_dotenv
import json
from mysql.connector.pooling import MySQLConnectionPool
import os
import requests
import pytz

load_dotenv(dotenv_path="backend\.env")

class CapitalReductionCrawler:
    tw_time = pytz.timezone('Asia/Taipei')
    tw_time = datetime.now(tw_time)
    listed_current_date = tw_time.strftime("%Y%m%d")
    OTC_current_date = tw_time.strftime("%Y/%m/%d")
    year = str(int(OTC_current_date[:4]) - 1911)
    OTC_current_date = OTC_current_date.replace(OTC_current_date[:4], year)
    
    def __init__(self, category: str) -> None:
        self.url = f"https://www.twse.com.tw/zh/exchangeReport/TWTAUU?   response=json&strDate={self.listed_current_date}&endDate={self.listed_current_date}" if category == "listed" else f"https://www.tpex.org.tw/web/stock/exright/revivt/revivt_result.php?l=zh-tw&d={self.OTC_current_date}&ed={self.OTC_current_date}"
        self.data = self.__get_reduction_data()
        
    def __get_reduction_data(self):
        try:
            response = requests.get(self.url)
            response.raise_for_status()
            response.encoding = "utf-8"
            return response.json()
        except Exception as e:
            print(e)
            
class AdjustPrice:
    connection = MySQLConnectionPool(user=os.getenv("SQL_USER"),
                            password=os.getenv("SQL_PASSWORD"),
                            host=os.getenv("SQL_HOST"),
                            port=os.getenv("SQL_PORT"),
                            database=os.getenv("SQL_DATABASE"),
                            pool_name = "crawler",
                            pool_size = 4)
    
    def __init__(self, data: dict) -> None:
        self.data = data
        self.new_data = self.data_transfer()
        
    def data_transfer(self):
        pass
    
    def insert_capital_reduction_value(self):
        stock_connection = self.connection.get_connection()
        try:
            with stock_connection.cursor(dictionary=True) as cursor:
                sql = """INSERT ignore INTO `Capital Reduction` VALUES (%s, %s, %s, %s)"""
                cursor.executemany(sql, self.new_data)
                stock_connection.commit()
                return cursor.rowcount
        except Exception as e:
            print(e)
        finally:
            stock_connection.close()
         
    def update_adjust_price(self):
        stock_connection = self.connection.get_connection()
        try:
            with stock_connection.cursor() as cursor:
                for item in self.new_data:
                    table_name = f'adj_historical_price{item[0]}'
                    mult = float(item[3]) / float(item[2])
                    sql = """UPDATE %s
                        SET open = open * %s, max = max * %s, min = min * %s, 
                            close = close * %s
                        WHERE date < '%s' """ % (table_name, mult, mult, mult, mult, item[1])
                    cursor.execute(sql)
                    
                stock_connection.commit()
                return cursor.rowcount
        except Exception as e:
            print(e)
            return False

class ListedStock(AdjustPrice):
    def __init__(self, data: dict) -> None:
        super().__init__(data)
    
    def data_transfer(self):
        new_data = []
        if self.data["stat"] == "OK":
            for item in self.data["data"]:
                item[0] = item[0].replace("/", "-")
                ad = str(int(item[0][0:3])+1911)
                item[0] = item[0].replace(item[0][0:3], ad)
                item[3] = item[3].replace(",", "")
                item[4] = item[4].replace(",", "")
                new_data.append((item[1], item[0], item[3], item[4]))
            return new_data
                
class OTCStock(AdjustPrice):
    def __init__(self, data: dict) -> None:
        super().__init__(data)

    def data_transfer(self):
        new_data = []
        if self.data["aaData"]:
            for item in self.data["aaData"]:
                item[0] = str(item[0] + 19110000)
                item[3] = item[3].replace(",", "")
                item[4] = item[4].replace(",", "")
                new_data.append((item[1], item[0], item[3], item[4]))
            return new_data
            
def lambda_handler(event, context):
    listed = CapitalReductionCrawler("listed").data
    OTC = CapitalReductionCrawler("OTC").data
    listed_data = ListedStock(listed)
    OTC_data = OTCStock(OTC)
    if listed_data.new_data:
        print(listed_data.insert_capital_reduction_value())
        print(listed_data.update_adjust_price())
    if OTC_data.new_data:
        print(OTC_data.insert_capital_reduction_value())
        print(OTC_data.update_adjust_price())
    # TODO implement
    return {
        'statusCode': 200,
        'body': json.dumps('Done')
    }

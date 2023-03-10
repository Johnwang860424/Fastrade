from datetime import datetime
from dotenv import load_dotenv
import json
from mysql.connector.pooling import MySQLConnectionPool
import os
import requests
import pytz

load_dotenv(dotenv_path="backend\.env")
        
class DividendCrawler:
    tw_time = pytz.timezone('Asia/Taipei')
    tw_time = datetime.now(tw_time)
    current_date = tw_time.date()
    def __init__(self, sybmol: str, stock_type: str) -> None:
        self.symbol = sybmol
        self.stock_type = stock_type
        self.url = f"https://tw.stock.yahoo.com/_td-stock/api/resource/StockServices.dividends;action=combineCashAndStock;sortBy=-date;date=;limit=1;symbol={self.symbol}.TW" if self.stock_type == "1" else f"https://tw.stock.yahoo.com/_td-stock/api/resource/StockServices.dividends;action=combineCashAndStock;sortBy=-date;date=;limit=1;symbol={self.symbol}.TWO"
        self.data = self.get_dividend_data()

    def get_dividend_data(self):
        try:
            response = requests.get(self.url)
            response.raise_for_status()
            response.encoding = "utf-8"
            result = response.json()
            if result["dividends"]:
                cash_data = result["dividends"][0]["exDividend"]
                stock_data = result["dividends"][0]["exRight"]
                if cash_data and self.current_date == datetime.strptime(cash_data["date"].split("T")[0], "%Y-%m-%d"):
                    cash_data["date"] = cash_data["date"].split("T")[0]
                    cash_data = dict(filter(lambda x: x[0] in ["cash", "date"], cash_data.items()))
                elif cash_data:
                    cash_data.clear()
                if stock_data and self.current_date == datetime.strptime(stock_data["date"].split("T")[0], "%Y-%m-%d"):
                    stock_data["date"] = stock_data["date"].split("T")[0]
                    stock_data = dict(filter(lambda x: x[0] in ["stock", "date"], stock_data.items()))
                elif stock_data:
                    stock_data.clear()
                return cash_data, stock_data
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
    
    def __init__(self, symbol: str, cash_dividend: dict, stock_dividend: dict) -> None:
        self.symbol = symbol
        self.cash_dividend = cash_dividend
        self.stock_dividend = stock_dividend
    
    def execute(self):
        if self.cash_dividend:
            close = self.get_cash_dividend_close()
            print(self.insert_cash_dividend())
            mult = 1 - (float(self.cash_dividend["cash"]) / float(close["close"]))
            print(self.update_adjust_price(self.cash_dividend["date"], mult))
        if self.stock_dividend:
            print(self.insert_stock_dividend())
            mult = 1 / (1 + float(self.stock_dividend["stock"]) / 10)
            print(self.update_adjust_price(self.stock_dividend["date"], mult))
    
    def get_cash_dividend_close(self) -> dict:
        stock_connection = self.connection.get_connection()
        try:
            with stock_connection.cursor(dictionary=True) as cursor:
                table = f'historical_price{self.symbol}'
                sql = f"""SELECT close
                            FROM {table}
                            WHERE date < %s AND close != 0
                            ORDER BY date DESC
                            LIMIT 1;"""
                cursor.execute(sql, (self.cash_dividend["date"], ))
                return cursor.fetchone()
        except Exception as e:      
            print(f"無法取得{self.symbol}股利變更日期", e)
        finally:
            stock_connection.close()
    
    def insert_cash_dividend(self):
        stock_connection = self.connection.get_connection()
        try:
            with stock_connection.cursor(dictionary=True) as cursor:
                sql = """INSERT ignore INTO `cash_dividend` VALUES (%s, %s, %s)"""
                cursor.execute(sql, (self.symbol, self.cash_dividend['date'], self.cash_dividend["cash"]))
                stock_connection.commit()
                return cursor.rowcount
        except Exception as e:
            print(e)
        finally:
            stock_connection.close()
        
    def insert_stock_dividend(self):
        stock_connection = self.connection.get_connection()
        try:
            with stock_connection.cursor(dictionary=True) as cursor:
                sql = """INSERT ignore INTO `stock_dividend` VALUES (%s, %s, %s)"""
                cursor.execute(sql, (self.symbol, self.stock_dividend["date"], self.stock_dividend["stock"]))
                stock_connection.commit()
                return cursor.rowcount
        except Exception as e:
            print(e)
        finally:
            stock_connection.close()
            
    def update_adjust_price(self, date, mult):
        stock_connection = self.connection.get_connection()
        try:
            with stock_connection.cursor() as cursor:
                table_name = f'adj_historical_price{self.symbol}'
                sql = """UPDATE %s
                    SET open = open * %s, max = max * %s, min = min * %s, 
                        close = close * %s
                    WHERE date < '%s' """ % (table_name, mult, mult, mult, mult, date)
                cursor.execute(sql)   
                stock_connection.commit()
                return cursor.rowcount
        except Exception as e:
            print(e)
            return False
        finally:
            stock_connection.close()

def lambda_handler(event, context):
    message = json.loads(event["Records"][0]["body"].replace("'", "\""))
    symbol = message["symbol"]
    stock_type = message["type"]
    dividend = DividendCrawler(symbol, stock_type)
    if dividend.data:
        cash_dividend, stock_dividend = dividend.data
        adj_data = AdjustPrice(symbol, cash_dividend, stock_dividend)
        adj_data.execute()
        
    # TODO implement
    return {
        'statusCode': 200,
        'body': json.dumps("Done")
    }
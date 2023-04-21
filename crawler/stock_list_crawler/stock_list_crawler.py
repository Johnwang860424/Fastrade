import boto3
from bs4 import BeautifulSoup
import datetime
from dotenv import load_dotenv
import json
from mysql.connector.pooling import MySQLConnectionPool
import os
import requests
import time

load_dotenv(dotenv_path="backend\.env")

listed_url = "https://isin.twse.com.tw/isin/class_main.jsp?owncode=&stockname=&isincode=&market=1&issuetype=1&industry_code=&Page=1&chklike=Y"
otc_url = "https://isin.twse.com.tw/isin/class_main.jsp?owncode=&stockname=&isincode=&market=2&issuetype=4&industry_code=&Page=1&chklike=Y"

connection = MySQLConnectionPool(user=os.getenv("SQL_USER"),
                                 password=os.getenv("SQL_PASSWORD"),
                                 host=os.getenv("SQL_HOST"),
                                 port=os.getenv("SQL_PORT"),
                                 database=os.getenv("SQL_DATABASE"),
                                 pool_name = "crawler",
                                 pool_size = 4)

CATEGORY_MAPPING = {
    "水泥工業": "01",
    "食品工業": "02",
    "塑膠工業": "03",
    "紡織纖維": "04",
    "電機機械": "05",
    "電器電纜": "06",
    "玻璃陶瓷": "08",
    "造紙工業": "09",
    "鋼鐵工業": "10",
    "橡膠工業": "11",
    "汽車工業": "12",
    "電子工業": "13",
    "建材營造業": "14",
    "航運業": "15",
    "觀光事業": "16",
    "金融保險業": "17",
    "貿易百貨業": "18",
    "綜合": "19",
    "其他業": "20",
    "化學工業": "21",
    "生技醫療業": "22",
    "油電燃氣業": "23",
    "半導體業": "24",
    "電腦及週邊設備業": "25",
    "光電業": "26",
    "通信網路業": "27",
    "電子零組件業": "28",
    "電子通路業": "29",
    "資訊服務業": "30",
    "其他電子業": "31",
    "文化創意業": "32",
    "農業科技業": "33",
    "電子商務": "34",
}


def switch_category(cat: str):
    return CATEGORY_MAPPING.get(cat, "")


def stock_list(url: str) -> list:
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    table = soup.find_all('table')[1]
    rows = table.find_all('tr')

    # Initialize an empty list to hold the data
    data = []
    # Iterate over the rows starting from the second row
    for row in rows[1:]:
        # Extract the cells from the row
        cells = row.find_all('td')
        date_object = datetime.datetime.strptime(cells[7].text.strip(), '%Y/%m/%d').date()
        current_year = datetime.datetime.now().year
        if date_object.year == current_year:
            # Extract the data from the cells and convert it to the desired format
            symbol = cells[2].text.strip()
            name = cells[3].text.strip()
            market = "1" if cells[4].text.strip() == "上市" else "2"
            industry = switch_category(cells[6].text.strip())
            date = date_object.strftime('%Y-%m-%d')
            # Append the data to the list
            data.append((symbol, name, market, industry, date))
    return data


def insert_stock(data: list):
    stock_connection = connection.get_connection()
    try:
        with stock_connection.cursor() as cursor:
            sql = """INSERT INTO `stock_list`(`symbol`, `name`, `type`, `category`, `issuing date`) VALUES (%s, %s, %s, %s, %s) AS list
                     ON DUPLICATE KEY UPDATE `name` = list.`name`,
                                             `type` = list.`type`,
                                             `category` = list.`category`"""
            cursor.executemany(sql, data)
            stock_connection.commit()
        return cursor.rowcount
    except Exception as e:
        print(e)
        return e
    finally:
        stock_connection.close()
       
       
def lambda_handler(event, context):
    listed = stock_list(listed_url)
    otc = stock_list(otc_url)
    # TODO implement
    listed_symbols = [symbol[0] for symbol in listed]
    otc_symbols = [symbol[0] for symbol in otc]
    combined_symbols = listed_symbols + otc_symbols
    try:
        print(insert_stock(listed))
        print(insert_stock(otc))
    except Exception:
        time.sleep(6)
        print(insert_stock(listed))
        print(insert_stock(otc))
    sqs = boto3.client('sqs')  #client is required to interact with 
    sqs.send_message(
       QueueUrl="https://sqs.ap-northeast-1.amazonaws.com/558915030770/stock_list",

       MessageBody=json.dumps(combined_symbols)
    )
    return {
        'statusCode': 200,
        'body': json.dumps('Done')
    }
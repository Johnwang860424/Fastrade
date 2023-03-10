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

def switch_category(cat: str):
    if cat == "水泥工業":
        return "01"
    elif cat == "食品工業":
        return "02"
    elif cat == "塑膠工業":
        return "03"
    elif cat == "紡織纖維":
        return "04"
    elif cat == "電機機械":
        return "05"
    elif cat == "電器電纜":
        return "06"
    elif cat == "玻璃陶瓷":
        return "08"
    elif cat == "造紙工業":
        return "09"
    elif cat == "鋼鐵工業":
        return "10"
    elif cat == "橡膠工業":
        return "11"
    elif cat == "汽車工業":
        return "12"
    elif cat == "電子工業":
        return "13"
    elif cat == "建材營造業":
        return "14"
    elif cat == "航運業":
        return "15"
    elif cat == "觀光事業":
        return "16"
    elif cat == "金融保險業":
        return "17"
    elif cat == "貿易百貨業":
        return "18"
    elif cat == "綜合":
        return "19"
    elif cat == "其他業":
        return "20"
    elif cat == "化學工業":
        return "21"
    elif cat == "生技醫療業":
        return "22"
    elif cat == "油電燃氣業":
        return "23"
    elif cat == "半導體業":
        return "24"
    elif cat == "電腦及週邊設備業":
        return "25"
    elif cat == "光電業":
        return "26"
    elif cat == "通信網路業":
        return "27"
    elif cat == "電子零組件業":
        return "28"
    elif cat == "電子通路業":
        return "29"
    elif cat == "資訊服務業":
        return "30"
    elif cat == "其他電子業":
        return "31"
    elif cat == "文化創意業":
        return "32"
    elif cat == "農業科技業":
        return "33"
    elif cat == "電子商務":
        return "34"

        
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
import boto3
from datetime import datetime
from dotenv import load_dotenv
import itertools
import json
from mysql.connector.pooling import MySQLConnectionPool
import os
import pytz

load_dotenv(dotenv_path="backend\.env")

connection = MySQLConnectionPool(user=os.getenv("SQL_USER"),
                                 password=os.getenv("SQL_PASSWORD"),
                                 host=os.getenv("SQL_HOST"),
                                 port=os.getenv("SQL_PORT"),
                                 database=os.getenv("SQL_DATABASE"),
                                 pool_name = "crawler",
                                 pool_size = 4)

sqs = boto3.client('sqs')
listed_queue_url = 'https://sqs.ap-northeast-1.amazonaws.com/558915030770/listed_price_crawler.fifo'
otc_queue_url = 'https://sqs.ap-northeast-1.amazonaws.com/558915030770/OTC_price_crawler.fifo'
tw_time = pytz.timezone('Asia/Taipei')
tw_time = datetime.now(tw_time)

listed_current_date = tw_time.strftime("%Y%m%d")
OTC_current_date = tw_time.strftime("%Y/%m")
year = str(int(OTC_current_date[:4]) - 1911)
OTC_current_date = OTC_current_date.replace(OTC_current_date[:4], year)

def get_stock_list(stock_type: str="%") -> list:
    """取得上市/櫃股票清單
    """
    stock_connection = connection.get_connection()
    try:
        with stock_connection.cursor() as cursor:
            query = ("""SELECT symbol from `stock_list` WHERE type LIKE %s""")
            cursor.execute(query, (f"%{stock_type}%", ))
            return [item[0] for item in cursor.fetchall()]
    except Exception as e:
        print(e)
    finally:
        stock_connection.close()

def lambda_handler(event, context):
    sqs = boto3.client('sqs')
    listed_stock_list = get_stock_list("1")
    OTC_stock_list = get_stock_list("2")
    for listed_stock, OTC_stock in itertools.zip_longest(listed_stock_list, OTC_stock_list):
        try:
            listed_params = {"response":"json", "date": listed_current_date, "stockNo": listed_stock}
            otc_params = {"d": OTC_current_date, "stkno": OTC_stock}
            if listed_stock and OTC_stock:
                print("上市",listed_stock,"上櫃",OTC_stock)
                sqs.send_message(QueueUrl=listed_queue_url, MessageBody=json.dumps(listed_params), MessageGroupId=listed_stock)
                sqs.send_message(QueueUrl=otc_queue_url, MessageBody=json.dumps(otc_params), MessageGroupId=OTC_stock)
            elif listed_stock and not OTC_stock:
                print("上市",listed_stock)
                sqs.send_message(QueueUrl=listed_queue_url, MessageBody=json.dumps(listed_params), MessageGroupId=listed_stock)
        except Exception as e:
            print(e)
    # TODO implement
    return {
        'statusCode': 200,
        'body': json.dumps('Hello from Lambda!')
    }
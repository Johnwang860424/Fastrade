import boto3
from dotenv import load_dotenv
import json
from mysql.connector.pooling import MySQLConnectionPool
import os

load_dotenv(dotenv_path="backend\.env")

connection = MySQLConnectionPool(user=os.getenv("SQL_USER"),
                                 password=os.getenv("SQL_PASSWORD"),
                                 host=os.getenv("SQL_HOST"),
                                 port=os.getenv("SQL_PORT"),
                                 database=os.getenv("SQL_DATABASE"),
                                 pool_name="crawler",
                                 pool_size=4)
sqs = boto3.client('sqs')
queue_url = 'https://sqs.ap-northeast-1.amazonaws.com/558915030770/dividend_stock_list.fifo'


def get_stock_list():
    stock_connection = connection.get_connection()
    try:
        with stock_connection.cursor() as cursor:
            cursor.execute("SELECT symbol FROM stock_list")
            result = cursor.fetchall()
            return [symbol[0] for symbol in result]
    except Exception as e:
        print(e)
    finally:
        stock_connection.close()


def lambda_handler(event, context):
    symbol_list = get_stock_list()
    for symbol in symbol_list:
        sqs.send_message(QueueUrl=queue_url, MessageBody=json.dumps(
            symbol), MessageGroupId=symbol)
    print(symbol_list)

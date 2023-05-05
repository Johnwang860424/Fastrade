import boto3
from dotenv import load_dotenv
import json
from mysql.connector.pooling import MySQLConnectionPool
import os

load_dotenv(dotenv_path="backend\.env")

connection = MySQLConnectionPool(
    user=os.getenv("SQL_USER"),
    password=os.getenv("SQL_PASSWORD"),
    host=os.getenv("SQL_HOST"),
    port=os.getenv("SQL_PORT"),
    database=os.getenv("SQL_DATABASE"),
    pool_name="crawler",
    pool_size=4,
)


def get_stock_list():
    try:
        stock_connection = connection.get_connection()
        with stock_connection.cursor(dictionary=True) as cursor:
            stock_list_query = """SELECT symbol, name, type
                                    FROM `stock_list`"""
            cursor.execute(stock_list_query)
            return cursor.fetchall()
    except Exception as e:
        print(e)
    finally:
        stock_connection.close()


def lambda_handler(event, context):
    # TODO implement
    stock_list = get_stock_list()

    sqs = boto3.client("sqs")
    sqs.send_message(
        QueueUrl="https://sqs.ap-northeast-1.amazonaws.com/558915030770/stock_list_redis",
        MessageBody=json.dumps(stock_list),
    )
    return {"statusCode": 200, "body": json.dumps("Hello from Lambda!")}

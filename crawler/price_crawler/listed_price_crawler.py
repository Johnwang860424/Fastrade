import boto3
from dotenv import load_dotenv
import json
from mysql.connector.pooling import MySQLConnectionPool
import os
import requests
import time

load_dotenv(dotenv_path="backend\.env")

connection = MySQLConnectionPool(user=os.getenv("SQL_USER"),
                                 password=os.getenv("SQL_PASSWORD"),
                                 host=os.getenv("SQL_HOST"),
                                 port=os.getenv("SQL_PORT"),
                                 database=os.getenv("SQL_DATABASE"),
                                 pool_name="crawler",
                                 pool_size=4)

sqs = boto3.client('sqs')
queue_name = 'listed_price_crawler.fifo'
queue_url = sqs.get_queue_url(QueueName=queue_name).get('QueueUrl')


def insert_current_price(symbol, data: list[tuple]):
    stock_connection = connection.get_connection()
    try:
        with stock_connection as connect:
            sql = f"""INSERT IGNORE INTO historical_price{symbol} VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)"""
            connect.cursor().executemany(sql, data)
            connect.commit()
    except Exception as e:
        print(symbol)
        print(e)


def insert_adj_price(symbol, data: list[tuple]):
    stock_connection = connection.get_connection()
    try:
        with stock_connection as connect:
            sql = f"""INSERT IGNORE INTO adj_historical_price{symbol} VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)"""
            connect.cursor().executemany(sql, data)
            connect.commit()
    except Exception as e:
        print(symbol)
        print(e)


def listed_price_crawler(request_body) -> list:
    url = f"https://www.twse.com.tw/rwd/zh/afterTrading/STOCK_DAY?date={request_body['date']}&stockNo={request_body['stockNo']}&response=json"
    res = requests.get(url)
    if "data" in res.json():
        data = res.json()["data"][-5:]
        for i, item in enumerate(data):
            item[0] = item[0].replace("/", "-")
            ad = str(int(item[0][0:3])+1911)
            item[0] = item[0].replace(item[0][0:3], ad)
            item[1] = item[1].replace(",", "")
            item[2] = item[2].replace(",", "")
            item[3] = item[3].replace(",", "")
            item[4] = item[4].replace(",", "")
            item[5] = item[5].replace(",", "")
            item[6] = item[6].replace(",", "")
            item[7] = item[7].replace("+", "").replace("X", "")
            item[-1] = item[-1].replace(",", "")
            data[i] = tuple(item)
        return data


def lambda_handler(event, context):
    messages = event['Records']
    for message in messages:
        try:
            records = json.loads(message['body'].replace("'", "\""))
            print(records['stockNo'])
            data = listed_price_crawler(records)
            insert_current_price(records['stockNo'], data)
            insert_adj_price(records['stockNo'], data)
        except Exception as e:
            print(e)
        finally:
            # Delete the message after processing it
            sqs.delete_message(
                QueueUrl=queue_url,
                ReceiptHandle=message['receiptHandle']
            )
            time.sleep(4)

    # TODO implement
    return {
        'statusCode': 200,
        'body': json.dumps('Hello from Lambda!')
    }

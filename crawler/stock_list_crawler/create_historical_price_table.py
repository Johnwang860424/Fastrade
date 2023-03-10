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
                                 pool_name = "crawler",
                                 pool_size = 4)
                      
def create_table(symbol: str):
    stock_connection = connection.get_connection()
    table = f'historical_price{symbol}'
    try:
        with stock_connection.cursor() as cursor:
            create_table_sql  = (f"""CREATE TABLE if not exists {table}(`date` DATE,
                                                        `trading_volume` BIGINT,
                                                        `trading_money` BIGINT,
                                                        `open` DECIMAL(7,2),
                                                        `max` DECIMAL(7,2),
                                                        `min` DECIMAL(7,2),
                                                        `close` DECIMAL(7,2),
                                                        `spread` DECIMAL(6,2),
                                                        `transaction` INT,
                                                        PRIMARY KEY(`date`));""")
            cursor.execute(create_table_sql)
            
            create_index_sql = f"""CREATE INDEX symbol_date_index ON {table} (date, open, min, max, close);"""
            
            cursor.execute(create_index_sql)
    except Exception as e:
        print(e)
    finally:
        stock_connection.close()

def create_adj_table(symbol: str):
    stock_connection = connection.get_connection()
    table = f'adhistorical_price{symbol}'
    try:
        with stock_connection.cursor() as cursor:
            create_table_sql  = (f"""CREATE TABLE if not exists {table}(`date` DATE,
                                                        `trading_volume` BIGINT,
                                                        `trading_money` BIGINT,
                                                        `open` DECIMAL(7,2),
                                                        `max` DECIMAL(7,2),
                                                        `min` DECIMAL(7,2),
                                                        `close` DECIMAL(7,2),
                                                        `spread` DECIMAL(6,2),
                                                        `transaction` INT,
                                                        PRIMARY KEY(`date`));""")
            cursor.execute(create_table_sql)
            
            create_index_sql = f"""CREATE INDEX symbol_date_index ON {table} (date, open, min, max, close);"""
            
            cursor.execute(create_index_sql)
    except Exception as e:
        print(e)
    finally:
        stock_connection.close()

def lambda_handler(event, context):
    sqs = boto3.client('sqs')
    queue_url = 'https://sqs.ap-northeast-1.amazonaws.com/558915030770/stock_list'
    # TODO implement
    records = event['Records'][0]['body']
    try:
        symbols = json.loads(records)
        for symbol in symbols:
            print(symbol)
            create_table(symbol)
            create_adj_table(symbol)
    except Exception as e:
        print(e)
from dotenv import load_dotenv
from mysql.connector.pooling import MySQLConnectionPool
import os

load_dotenv()

connection = MySQLConnectionPool(user=os.getenv("SQL_USER"),
                                 password=os.getenv("SQL_PASSWORD"),
                                 host=os.getenv("SQL_HOST"),
                                 port=os.getenv("SQL_PORT"),
                                 database=os.getenv("SQL_DATABASE"),
                                 pool_name = "api",
                                 pool_size=10,
                                 connect_timeout=60)

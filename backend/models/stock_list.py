from .config import connection
import redis
import json


class StockList:
    def __init__(self, stock_type: str | None):
        self.type = stock_type

    def get_all_stock_list():
        try:
            stock_connection = connection.get_connection()
            with stock_connection.cursor(dictionary=True) as cursor:
                stock_list_query = """SELECT symbol, name
                                        FROM `stock_list`"""
                cursor.execute(stock_list_query)
                return cursor.fetchall()
        except Exception as e:
            print(e)
            return False
        finally:
            stock_connection.close()

    def get_specified_stock_list(self):
        try:
            stock_connection = connection.get_connection()
            with stock_connection.cursor(dictionary=True) as cursor:
                stock_list_query = """SELECT symbol, name
                                        FROM stock_list
                                        WHERE type = %s"""
                cursor.execute(stock_list_query, (self.type,))
                return cursor.fetchall()
        except Exception as e:
            print(e)
            return False
        finally:
            stock_connection.close()

    def get_redis_stock_list(self):
        database = redis.Redis(
            host="stocklist-001.cfrhde.0001.apne1.cache.amazonaws.com", port=6379
        )
        keys = database.keys("*")
        keys = [item.decode("utf-8") for item in keys]
        if not self and "all_stock_list" in keys:
            value = database.get("all_stock_list")
            stock_list = json.loads(value)
            return stock_list
        elif self.type == "1" and "listed_stock_list" in keys:
            value = database.get("listed_stock_list")
            stock_list = json.loads(value)
            return stock_list
        elif self.type == "2" and "OTC_stock_list" in keys:
            value = database.get("OTC_stock_list")
            stock_list = json.loads(value)
            return stock_list
        return False

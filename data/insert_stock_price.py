from config import connection
import finmind

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

def get_price_stock_list() -> list:
    stock_connection = connection.get_connection()
    try:
        with stock_connection.cursor() as cursor:
            query = ("""select distinct(symbol) from historical_price""")
            cursor.execute(query)
            return [item[0] for item in cursor.fetchall()]
    except Exception:
        print(Exception)
    finally:
        stock_connection.close()
price_stock_list = get_price_stock_list()

def check(stock_list: list, price_stock_list: list):
    discrepancy = []
    for i in stock_list():
        if i not in price_stock_list:
            discrepancy.append(i)
    return discrepancy

lack_stock = check(get_stock_list, price_stock_list)

def insert_historical_price(stock_list: list):
    stock_finmind = finmind.StockFinMind()
    # 股價日成交資訊
    for item in stock_list:
        stock_deal_info = stock_finmind.get_stock_deal_info(item, "2000-01-01", "2023-01-17")
        result = [tuple(row.values()) for row in stock_deal_info]
        stock_connection = connection.get_connection()
        try:
            with stock_connection.cursor() as cursor:
                sql = """INSERT INTO `historical_price` VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""
                cursor.executemany(sql, result)
                stock_connection.commit()
        except Exception as e:
            print(e)
        finally:
            stock_connection.close()

insert_historical_price(lack_stock)


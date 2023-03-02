from .config import connection

class StockList:
    def __init__(self, stock_type: str):
        self.type = stock_type
    
    def get_all_stock_list():
        try:
            stock_connection = connection.get_connection()
            with stock_connection.cursor(dictionary=True) as cursor:
                stock_list_query = ("""SELECT symbol, name
                                        FROM `stock_list`""")
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
                stock_list_query = ("""SELECT symbol, name
                                        FROM stock_list
                                        WHERE type = %s""")
                cursor.execute(stock_list_query, (self.type,))
                return cursor.fetchall()
        except Exception as e:
            print(e)
            return False
        finally:
            stock_connection.close()
    
from .config import connection


class StockPrice:
    def __init__(self, symbol: str, start_date: str, end_date: str):
        self.symbol = symbol
        self.start_date = start_date
        self.end_date = end_date

    def get_original_price(self) -> list | None:
        try:
            stock_connection = connection.get_connection()
            with stock_connection.cursor(dictionary=True) as cursor:
                table = f'historical_price{self.symbol}'
                stock_price_query = (
                    f"""SELECT date, open, min, max, close FROM {table} WHERE date between %s and %s""")
                cursor.execute(stock_price_query,
                               (self.start_date, self.end_date))
                stock_price = cursor.fetchall()
        except Exception as e:
            print(e)
            return False
        finally:
            stock_connection.close()
        return [row for row in stock_price if row["open"] or row["min"] or row["max"] or row["close"] != 0.0]

    def get_adjusted_price(self) -> list | None:
        try:
            stock_connection = connection.get_connection()
            with stock_connection.cursor(dictionary=True) as cursor:
                table = f'adj_historical_price{self.symbol}'
                stock_price_query = (
                    f"""SELECT date, open, min, max, close FROM {table} WHERE date between %s and %s""")
                cursor.execute(stock_price_query,
                               (self.start_date, self.end_date))
                stock_price = cursor.fetchall()
        except Exception as e:
            print(e)
            return False
        finally:
            stock_connection.close()
        return [row for row in stock_price if row["open"] or row["min"] or row["max"] or row["close"] != 0.0]

from .config import connection
from datetime import datetime


class StrategyData:
    def __init__(self, symbol: str):
        self.symbol = symbol

    def get_ma_data(self, start_date, end_date, long_term_ma) -> list | None:
        long_term = long_term_ma * 4
        target_date = datetime.strptime(start_date, '%Y-%m-%d').date()
        try:
            stock_connection = connection.get_connection()
            with stock_connection.cursor(dictionary=True) as cursor:
                table = f'adj_historical_price{self.symbol}'
                stock_list_query = (f"""SELECT date, close FROM               
                                    {table} 
                                    WHERE close != 0.00
                                    AND date 
                                    BETWEEN DATE_SUB(%s, INTERVAL %s DAY) AND %s""")
                cursor.execute(stock_list_query, (start_date, long_term,
                                                  end_date))
                data = cursor.fetchall()
                new_data = []
                for i, item in enumerate(data):
                    date = item['date']
                    close = item['close']
                    if item['date'] >= target_date:
                        if i - long_term_ma + 1 <= 0:
                            new_data.append((date, close))
                        else:
                            for item in data[i-long_term_ma+1:]:
                                new_data.append((item['date'], item['close']))
                            break
                return new_data
        except Exception as e:
            print(e)
            return False
        finally:
            stock_connection.close()

    def get_kd_data(self, end_date) -> list | None:
        try:
            stock_connection = connection.get_connection()
            with stock_connection.cursor(dictionary=True) as cursor:
                table = f'adj_historical_price{self.symbol}'
                stock_list_query = (f"""SELECT date, open, max, min, close
                                    FROM {table} 
                                    WHERE close != 0.00
                                    AND date <= %s""")
                cursor.execute(stock_list_query, (end_date,))
                return cursor.fetchall()
        except Exception as e:
            print(e)
            return False
        finally:
            stock_connection.close()

    def get_macd_data(self, end_date) -> list | None:
        try:
            stock_connection = connection.get_connection()
            with stock_connection.cursor(dictionary=True) as cursor:
                table = f'adj_historical_price{self.symbol}'
                stock_list_query = (f"""SELECT date, close
                                    FROM {table} 
                                    WHERE close != 0.00
                                    AND date <= %s""")
                cursor.execute(stock_list_query, (end_date,))
                return cursor.fetchall()
        except Exception as e:
            print(e)
            return False
        finally:
            stock_connection.close()

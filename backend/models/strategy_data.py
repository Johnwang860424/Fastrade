from abc import ABC, abstractmethod
from .config import connection
from datetime import datetime


class StrategyData(ABC):
    def __init__(self):
        self.data = None

    def get_data(self):
        if self.data is None:
            self.data = self._get_raw_data()
        return self.data

    @abstractmethod
    def _get_raw_data(self):
        pass


class MAStrategyData(StrategyData):
    def __init__(self, symbol: str, start_date: str, end_date: str, long_term_ma: int):
        super().__init__()
        self.symbol = symbol
        self.start_date = start_date
        self.end_date = end_date
        self.long_term_ma = long_term_ma

    def _get_raw_data(self):
        long_term = self.long_term_ma * 4
        target_date = datetime.strptime(self.start_date, "%Y-%m-%d").date()
        try:
            stock_connection = connection.get_connection()
            with stock_connection.cursor(dictionary=True) as cursor:
                table = f"adj_historical_price{self.symbol}"
                stock_list_query = f"""SELECT date, open, max, min, close 
                                    FROM {table} 
                                    WHERE close != 0.00
                                    AND date 
                                    BETWEEN DATE_SUB(%s, INTERVAL %s DAY) AND %s"""
                cursor.execute(
                    stock_list_query, (self.start_date, long_term, self.end_date)
                )
                data = cursor.fetchall()
                new_data = []
                for i, item in enumerate(data):
                    if item["date"] >= target_date and i >= self.long_term_ma - 1:
                        new_data.extend(data[i - self.long_term_ma + 1 :])
                        break
                return new_data
        except Exception as e:
            print(e)
            return False
        finally:
            stock_connection.close()


class KDStrategyData(StrategyData):
    def __init__(self, symbol: str, end_date: str):
        super().__init__()
        self.symbol = symbol
        self.end_date = end_date

    def _get_raw_data(self):
        try:
            stock_connection = connection.get_connection()
            with stock_connection.cursor(dictionary=True) as cursor:
                table = f"adj_historical_price{self.symbol}"
                stock_list_query = f"""SELECT date, open, max, min, close
                                    FROM {table} 
                                    WHERE close != 0.00
                                    AND date <= %s"""
                cursor.execute(stock_list_query, (self.end_date,))
                return cursor.fetchall()
        except Exception as e:
            print(e)
            return False
        finally:
            stock_connection.close()


class MACDStrategyData(StrategyData):
    def __init__(self, symbol: str, end_date: str):
        super().__init__()
        self.symbol = symbol
        self.end_date = end_date

    def _get_raw_data(self):
        try:
            stock_connection = connection.get_connection()
            with stock_connection.cursor(dictionary=True) as cursor:
                table = f"adj_historical_price{self.symbol}"
                stock_list_query = f"""SELECT date, close
                                    FROM {table} 
                                    WHERE close != 0.00
                                    AND date <= %s"""
                cursor.execute(stock_list_query, (self.end_date,))
                return cursor.fetchall()
        except Exception as e:
            print(e)
            return False
        finally:
            stock_connection.close()

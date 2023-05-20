from abc import ABC, abstractmethod
from datetime import datetime
import pandas as pd
from .strategy_data import StrategyData


class StockStrategy(ABC):
    @abstractmethod
    def calculate(self, data: StrategyData) -> tuple[int, dict] | None:
        pass


class MAStockStrategy(StockStrategy):
    def __init__(self, short_term: int, long_term: int):
        self.short_term = short_term
        self.long_term = long_term

    def calculate(self, data):
        data = data.get_data()
        if data:
            df = pd.DataFrame(data)
            # calculate short-term and long-term moving averages
            df["short_term_ma"] = df["close"].rolling(self.short_term).mean()
            df["long_term_ma"] = df["close"].rolling(self.long_term).mean()
            # Drop rows with missing values
            df.dropna(inplace=True)
            # Reset the index
            df.reset_index(drop=True, inplace=True)
            data_set = {}
            positive = []
            negative = []
            for index in df.index:
                # calculate the crossover point
                if (
                    index > 0
                    and df["short_term_ma"][index - 1] < df["long_term_ma"][index - 1]
                    and df["short_term_ma"][index] > df["long_term_ma"][index]
                ):
                    positive.append((df["date"][index], df["close"][index]))
                elif (
                    index > 0
                    and df["short_term_ma"][index - 1] > df["long_term_ma"][index - 1]
                    and df["short_term_ma"][index] < df["long_term_ma"][index]
                ):
                    negative.append((df["date"][index], df["close"][index]))
            data_set["positive"], data_set["negative"] = positive, negative
            total_days = len(df)
            return total_days, data_set
        return None


class KDStockStrategy(StockStrategy):
    def __init__(self, start_date: str, day: int, window: int):
        self.start_date = start_date
        self.day = day
        self.window = window

    def calculate(self, data):
        data = data.get_data()
        if data:
            df = pd.DataFrame(data)
            start_date = datetime.strptime(self.start_date, "%Y-%m-%d").date()
            # calculate the highest price and lowest price in the past window days
            df = pd.DataFrame(data, columns=["date", "open", "max", "min", "close"])
            lowest_low = df["min"].rolling(window=self.day, min_periods=1).min()
            highest_high = df["max"].rolling(window=self.day, min_periods=1).max()
            rsv = (
                (df["close"].astype(float) - lowest_low)
                / (highest_high - lowest_low)
                * 100
            )
            smooth_factor = 1 / self.window

            # calculate K value
            K = rsv[0]

            def KValue(rsv):
                nonlocal K
                K = (1 - smooth_factor) * K + smooth_factor * rsv
                return K

            # calculate D value
            D = rsv[0]

            def DValue(k):
                nonlocal D
                D = (1 - smooth_factor) * D + smooth_factor * k
                return D

            # 將計算結果加入到DataFrame中
            df["k"] = rsv.apply(KValue)
            df["d"] = df["k"].apply(DValue)
            df["rsv"] = rsv
            # 設
            df = df.loc[df["date"] >= start_date]
            df.reset_index(inplace=True)
            data_set = {}
            positive = []
            negative = []

            for index in df.index:
                # calculate the crossover point
                if (
                    index > 0
                    and df["k"][index - 1] < df["d"][index - 1]
                    and df["k"][index] > df["d"][index]
                ):
                    positive.append((df["date"][index], df["close"][index]))
                elif (
                    index > 0
                    and df["k"][index - 1] > df["d"][index - 1]
                    and df["k"][index] < df["d"][index]
                ):
                    negative.append((df["date"][index], df["close"][index]))
            data_set["positive"], data_set["negative"] = positive, negative
            total_days = len(df)
            return total_days, data_set
        return None


class MACDStockStrategy(StockStrategy):
    def __init__(self, start_date: str, short_term: int, long_term: int, signal: int):
        self.start_date = start_date
        self.short_term = short_term
        self.long_term = long_term
        self.signal = signal

    def calculate(self, data):
        data = data.get_data()
        if data:
            df = pd.DataFrame(data, columns=["date", "close"])
            start_date = datetime.strptime(self.start_date, "%Y-%m-%d").date()
            # calculate short-term and long-term exponential moving averages
            short_ema = df[["close"]].ewm(span=self.short_term, adjust=False).mean()
            long_ema = df[["close"]].ewm(span=self.long_term, adjust=False).mean()
            dif = short_ema - long_ema  # 快線 DIF(差離值)
            dem = dif.ewm(span=self.signal, adjust=False).mean()  # 慢線 DEM(平均值)
            histogram = dif - dem  # MACD 柱狀圖
            # 設定為符合的日期
            histogram = histogram.loc[df["date"] >= start_date]
            histogram.reset_index(inplace=True)
            df = df.loc[df["date"] >= start_date]
            df.reset_index(inplace=True)
            data_set = {}
            positive = []
            negative = []
            for index in df.index:
                # calculate the crossover point
                if (
                    index > 0
                    and histogram["close"][index - 1] < 0
                    and histogram["close"][index] > 0
                ):
                    positive.append((df["date"][index], df["close"][index]))
                elif (
                    index > 0
                    and histogram["close"][index - 1] > 0
                    and histogram["close"][index] < 0
                ):
                    negative.append((df["date"][index], df["close"][index]))
            data_set["positive"], data_set["negative"] = positive, negative
            total_days = len(df)
            return total_days, data_set
        return None

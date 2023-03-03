from datetime import datetime
from strategy_data import StrategyData, MAStrategyData
import numpy as np
import pandas as pd

class StockStrategy:
    def __init__(self, strategy_data: StrategyData) -> None:
        self.strategy_data = strategy_data
        
    def calculate(self):
        pass
    
class MAStrategy(StockStrategy):
    def __init__(self, strategy_data: StrategyData, term: int) -> None:
        super().__init__(strategy_data)
        self.term = term
        
    def calculate(self):
        data_array = np.array(self.strategy_data.get_data(), dtype=[('date', 'datetime64[D]'), ('open', 'f8'), ('max', 'f8'), ('min', 'f8'), ('close', 'f8')])
        # calculate short-term and long-term moving averages
        ma = np.convolve(data_array['close'], np.ones(self.term)/self.term, mode='valid')
        ma_dict = {str(date): close for date, close in zip(data_array['date'][self.term-1:], ma)}
        return ma_dict
    
a = MAStrategyData('2330', '2019-01-01', '2020-01-01', 20)
b = MAStrategy(a, 10)

print(b.calculate())
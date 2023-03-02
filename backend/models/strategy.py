from datetime import datetime
from .strategy_data import StrategyData
import numpy as np
import pandas as pd

def buy_ma(symbol: str, start_date: str, end_date: str, initial_money: int, 
           short_term_ma: int, long_term_ma: int) -> dict:
    # Convert data to numpy array for easier calculation
    data = StrategyData(symbol).get_ma_data(start_date, end_date, long_term_ma)
    if data:
        data_array = np.array(data, dtype=[('date', 'datetime64[D]'), ('close', 'f8')])
        initial_money = initial_money * 10000
        buy = []
        sell = []
        holding = False
        num_trades = 0
        num_wins = 0
        num_losses = 0
        total_profit = 0
        win_profit = 0
        loss_profit = 0
        balance = initial_money

        # calculate short-term and long-term moving averages
        short_ma = np.convolve(data_array['close'], np.ones(short_term_ma)/short_term_ma, mode='valid')
        # 講短天期ma變成跟長天期ma一樣長
        short_ma = short_ma[long_term_ma - short_term_ma:]
        long_ma = np.convolve(data_array['close'], np.ones(long_term_ma)/long_term_ma, mode='valid')

        for i in range(len(short_ma)):
            # Buy signal: short-term moving average crosses above long-term moving average
            if i > 0 and short_ma[i-1] < long_ma[i-1] and short_ma[i] > long_ma[i] and not holding:
                buy.append((data_array['date'][i+long_term_ma-1], data_array['close'][i+long_term_ma-1]))
                holding = True
            # Sell signal: short-term moving average crosses below long-term moving average
            elif short_ma[i] < long_ma[i] and holding:
                sell.append((data_array['date'][i+long_term_ma-1], data_array['close'][i+long_term_ma-1]))
                holding = False
                num_trades += 1
                per_roi = sell[-1][1] / buy[-1][1] - 1
                profit = per_roi * balance
                total_profit += profit
                balance += profit
                if profit > 0:
                    num_wins += 1
                    win_profit += profit
                else:
                    num_losses += 1
                    loss_profit += profit

        # Calculate metrics
        total_days = len(short_ma)
        win_rate = num_wins / num_trades * 100 if num_trades > 0 else 0 # 計算勝率(%)
        roi = (balance - initial_money) / initial_money * 100 # 計算報酬率(%)，即總盈虧/初始資金
        # 計算平均獲利虧損比 aka 賺賠比
        if num_losses and num_wins > 0:
            average_risk_reward_ratio = (abs(win_profit / num_wins)) / (abs(loss_profit / num_losses)) 
        elif num_losses == 0 and num_wins > 0:
            average_risk_reward_ratio = "無限大"
        else:
            average_risk_reward_ratio = 0
        # 計算獲利因子
        if loss_profit < 0:
            profit_factor = abs(win_profit) / abs(loss_profit)
        elif loss_profit == 0 and win_profit > 0:
            profit_factor = "無限大"
        else:
            profit_factor = 0

        metrics = {
            'total_days': total_days,
            'total_trades': num_trades,
            'num_wins': num_wins,
            'num_losses': num_losses,
            'win_rate': f"{round(win_rate, 2)}%",
            'roi': f"{round(roi, 2)}%",
            'total_profit': int(total_profit),
            'average_risk_reward_ratio': round(average_risk_reward_ratio, 2),
            'profit_factor': round(profit_factor, 2),
        }
        return metrics
    return None


def sell_ma(symbol: str, start_date: str, end_date: str, initial_money: int, 
           short_term_ma: int, long_term_ma: int) -> dict:
    # Convert data to numpy array for easier calculation
    data = StrategyData(symbol).get_ma_data(start_date, end_date, long_term_ma)
    if data:
        data_array = np.array(data, dtype=[('date', 'datetime64[D]'), ('close', 'f8')])
        initial_money = initial_money * 10000
        buy = []
        sell = []
        holding = False
        num_trades = 0
        num_wins = 0
        num_losses = 0
        total_profit = 0
        win_profit = 0
        loss_profit = 0
        balance = initial_money
        
        # calculate short-term and long-term moving averages
        short_ma = np.convolve(data_array['close'], np.ones(short_term_ma)/short_term_ma, mode='valid')
        # 講短天期ma變成跟長天期ma一樣長
        short_ma = short_ma[long_term_ma - short_term_ma:]

        long_ma = np.convolve(data_array['close'], np.ones(long_term_ma)/long_term_ma, mode='valid')
        
        for i in range(len(short_ma)):
            # Sell signal: short-term moving average crosses below long-term moving average
            if i > 0 and short_ma[i-1] > long_ma[i-1] and short_ma[i] < long_ma[i] and not holding:
                sell.append((data_array['date'][i+long_term_ma-1], data_array['close'][i+long_term_ma-1]))
                holding = True
            # Buy signal: short-term moving average crosses above long-term moving average
            elif short_ma[i] > long_ma[i] and holding:
                buy.append((data_array['date'][i+long_term_ma-1], data_array['close'][i+long_term_ma-1]))
                holding = False
                num_trades += 1
                per_roi = 1 - (buy[-1][1] / sell[-1][1])
                profit = per_roi * balance
                total_profit += profit
                balance += profit
                if profit > 0:
                    num_wins += 1
                    win_profit += profit
                else:
                    num_losses += 1
                    loss_profit += profit
                
        # Calculate metrics
        total_days = len(long_ma)
        win_rate = num_wins / num_trades * 100 if num_trades > 0 else 0 # 計算勝率(%)
        roi = (balance - initial_money) / initial_money * 100 # 計算報酬率(%)，即總盈虧/初始資金
        # 計算平均獲利虧損比 aka 賺賠比
        if num_losses and num_wins > 0:
            average_risk_reward_ratio = (abs(win_profit / num_wins)) / (abs(loss_profit / num_losses)) 
        elif num_losses == 0 and num_wins > 0:
            average_risk_reward_ratio = "無限大"
        else:
            average_risk_reward_ratio = 0
        # 計算獲利因子
        if loss_profit < 0:
            profit_factor = abs(win_profit) / abs(loss_profit)
        elif loss_profit == 0 and win_profit > 0:
            profit_factor = "無限大"
        else:
            profit_factor = 0

        # Format output as dictionary
        metrics = {
            'total_days': total_days,
            'total_trades': num_trades,
            'num_wins': num_wins,
            'num_losses': num_losses,
            'win_rate': f"{round(win_rate, 2)}%",
            'roi': f"{round(roi, 2)}%",
            'total_profit': int(total_profit),
            'average_risk_reward_ratio': round(average_risk_reward_ratio, 2),
            'profit_factor': round(profit_factor, 2),
        }
        return metrics


def buy_macd(symbol: str, start_date: str, end_date: str, initial_money: int, 
             short_term_macd: int, long_term_macd: int, signal_macd: int=9) -> dict:
    data = StrategyData(symbol).get_macd_data(end_date)
    if data:
        df = pd.DataFrame(data, columns=['date', 'close'])
        start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
        initial_money = initial_money * 10000
        buy = []
        sell = []
        holding = False
        num_trades = 0
        num_wins = 0
        num_losses = 0
        total_profit = 0
        win_profit = 0
        loss_profit = 0
        balance = initial_money
        
        # calculate short-term and long-term exponential moving averages
        short_ema = df[['close']].ewm(span=short_term_macd, adjust=False).mean()
        long_ema = df[['close']].ewm(span=long_term_macd, adjust=False).mean()
        dif = short_ema - long_ema # 快線 DIF(差離值)
        dem = dif.ewm(span=signal_macd, adjust=False).mean() # 慢線 DEM(平均值)
        histogram = dif - dem # MACD 柱狀圖
        # 設定為符合買進的日期
        new_data = df.loc[df['date'] >= start_date]
        new_histogram = histogram.loc[df['date'] >= start_date]

        for i in range(len(new_data)):
            # Buy signal (DIF > DEM and histogram > 0)
            if i > 0 and new_histogram['close'].iloc[i-1] <= 0 and new_histogram['close'].iloc[i] > 0 and not holding:
                buy.append((new_data['date'].iloc[i], new_data['close'].iloc[i]))
                holding = True
            # Sell signal (DIF < DEM and histogram < 0)
            elif new_histogram['close'].iloc[i] < 0 and holding:
                sell.append((new_data['date'].iloc[i], new_data['close'].iloc[i]))
                holding = False
                num_trades += 1
                per_roi = sell[-1][1] / buy[-1][1] - 1
                profit = per_roi * balance
                total_profit += profit
                balance += profit
                if profit > 0:
                    num_wins += 1
                    win_profit += profit
                else:
                    num_losses += 1
                    loss_profit += profit

        # Calculate metrics
        total_days = len(new_data)
        win_rate = num_wins / num_trades * 100 if num_trades > 0 else 0 # 計算勝率(%)
        roi = (balance - initial_money) / initial_money * 100 # 計算報酬率(%)，即總盈虧/初始資金
        # 計算平均獲利虧損比 aka 賺賠比
        if num_losses and num_wins > 0:
            average_risk_reward_ratio = (abs(win_profit / num_wins)) / (abs(loss_profit / num_losses)) 
        elif num_losses == 0:
            average_risk_reward_ratio = "無限大"
        else:
            average_risk_reward_ratio = 0
        if loss_profit < 0:
            profit_factor = abs(win_profit) / abs(loss_profit)
        elif loss_profit == 0 and win_profit > 0:
            profit_factor = "無限大"
        else:
            profit_factor = 0
        metrics = {
            'total_days': total_days,
            'total_trades': num_trades,
            'num_wins': num_wins,
            'num_losses': num_losses,
            'win_rate': f"{round(win_rate, 2)}%",
            'roi': f"{round(roi, 2)}%",
            'total_profit': int(total_profit),
            'average_risk_reward_ratio': round(average_risk_reward_ratio, 2),
            'profit_factor': round(profit_factor, 2),
        }
        return metrics


def sell_macd(symbol: str, start_date: str, end_date: str, initial_money: int, 
             short_term_macd: int, long_term_macd: int, signal_macd: int=9) -> dict:
    data = StrategyData(symbol).get_macd_data(end_date)
    if data:
        df = pd.DataFrame(data, columns=['date', 'close'])
        start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
        initial_money = initial_money * 10000
        buy = []
        sell = []
        holding = False
        num_trades = 0
        num_wins = 0
        num_losses = 0
        total_profit = 0
        win_profit = 0
        loss_profit = 0
        balance = initial_money
        
        # calculate short-term and long-term exponential moving averages
        short_ema = df[['close']].ewm(span=short_term_macd, adjust=False).mean()
        long_ema = df[['close']].ewm(span=long_term_macd, adjust=False).mean()
        dif = short_ema - long_ema # 快線 DIF(差離值)
        dem = dif.ewm(span=signal_macd, adjust=False).mean() # 慢線 DEM(平均值)
        histogram = dif - dem # MACD 柱狀圖
        # 設定為符合賣出的日期
        new_data = df.loc[df['date'] >= start_date]
        new_histogram = histogram.loc[df['date'] >= start_date]

        for i in range(len(new_data)):
            # Sell signal (DIF < DEM and histogram < 0)
            if i > 0 and new_histogram['close'].iloc[i-1] >= 0 and new_histogram['close'].iloc[i] < 0 and not holding:
                sell.append((new_data['date'].iloc[i], new_data['close'].iloc[i]))
                holding = True
            elif new_histogram['close'].iloc[i] > 0 and holding:
                buy.append((new_data['date'].iloc[i], new_data['close'].iloc[i]))
                holding = False
                num_trades += 1
                per_roi = 1 - (buy[-1][1] / sell[-1][1])
                profit = per_roi * balance
                total_profit += profit
                balance += profit
                if profit > 0:
                    num_wins += 1
                    win_profit += profit
                else:
                    num_losses += 1
                    loss_profit += profit
                    
        # Calculate metrics
        total_days = len(new_data)
        win_rate = num_wins / num_trades * 100 if num_trades > 0 else 0 # 計算勝率(%)

        roi = (balance - initial_money) / initial_money * 100 # 計算報酬率(%)，即總盈虧/初始資金
        # 計算平均獲利虧損比 aka 賺賠比
        if num_losses and num_wins > 0:
            average_risk_reward_ratio = (abs(win_profit / num_wins)) / (abs(loss_profit / num_losses)) 
        elif num_losses == 0:
            average_risk_reward_ratio = "無限大"
        else:
            average_risk_reward_ratio = 0
        if loss_profit < 0:
            profit_factor = abs(win_profit) / abs(loss_profit)
        elif loss_profit == 0 and win_profit > 0:
            profit_factor = "無限大"
        else:
            profit_factor = 0

        metrics = {
            'total_days': total_days,
            'total_trades': num_trades,
            'num_wins': num_wins,
            'num_losses': num_losses,
            'win_rate': f"{round(win_rate, 2)}%",
            'roi': f"{round(roi, 2)}%",
            'total_profit': int(total_profit),
            'average_risk_reward_ratio': round(average_risk_reward_ratio, 2),
            'profit_factor': round(profit_factor, 2),
        }
        return metrics

def buy_kd(symbol: str, start_date: str, end_date: str, initial_money: int,     
           day: int, window: int) -> dict:
    data = StrategyData(symbol).get_kd_data(end_date)
    if data:
        start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
        initial_money = initial_money * 10000
        buy = []
        sell = []
        holding = False
        num_trades = 0
        num_wins = 0
        num_losses = 0
        total_profit = 0
        win_profit = 0
        loss_profit = 0
        balance = initial_money
        
        df = pd.DataFrame(data, columns=['date', 'open', 'max', 'min', 'close'])
        lowest_low = df['min'].rolling(window=day, min_periods=1).min()
        highest_high = df['max'].rolling(window=day, min_periods=1).max()
        rsv = (df['close'].astype(float) - lowest_low) / (highest_high - lowest_low) * 100
        smooth_factor = 1/window
        
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
        df['k'] = rsv.apply(KValue)
        df['d'] = df['k'].apply(DValue)
        df['rsv'] = rsv
        new_data = df.loc[df['date'] >= start_date]

        for i in range(len(new_data)):
            # Buy signal (K value > D value)
            if i > 0 and new_data.iloc[i]['k'] > new_data.iloc[i]['d'] and new_data.iloc[i-1]['k'] < new_data.iloc[i-1]['d'] and not holding:
                buy.append((new_data.iloc[i]['date'], new_data.iloc[i]['close']))
                holding = True
            # Sell signal (K value < D value)
            elif new_data.iloc[i]['k'] < new_data.iloc[i]['d'] and new_data.iloc[i-1]['k'] > new_data.iloc[i-1]['d'] and holding:
                sell.append((new_data.iloc[i]['date'], new_data.iloc[i]['close']))
                holding = False
                num_trades += 1
                per_roi = sell[-1][1] / buy[-1][1] - 1
                profit = per_roi * balance
                total_profit += profit
                balance += profit
                if profit > 0:
                    num_wins += 1
                    win_profit += profit
                else:
                    num_losses += 1
                    loss_profit += profit

        # Calculate metrics
        total_days = len(new_data)
        win_rate = num_wins / num_trades * 100 if num_trades > 0 else 0 # 計算勝率(%)
        roi = (balance - initial_money) / initial_money * 100 # 計算報酬率(%)，即總盈虧/初始資金
        # 計算平均獲利虧損比 aka 賺賠比
        if num_losses and num_wins > 0:
            average_risk_reward_ratio = (abs(win_profit / num_wins)) / (abs(loss_profit / num_losses)) 
        elif num_losses == 0:
            average_risk_reward_ratio = "無限大"
        else:
            average_risk_reward_ratio = 0
        if loss_profit < 0:
            profit_factor = abs(win_profit) / abs(loss_profit)
        elif loss_profit == 0 and win_profit > 0:
            profit_factor = "無限大"
        else:
            profit_factor = 0
        metrics = {
            'total_days': total_days,
            'total_trades': num_trades,
            'num_wins': num_wins,
            'num_losses': num_losses,
            'win_rate': f"{round(win_rate, 2)}%",
            'roi': f"{round(roi, 2)}%",
            'total_profit': int(total_profit),
            'average_risk_reward_ratio': round(average_risk_reward_ratio, 2),
            'profit_factor': round(profit_factor, 2),
        }
        return metrics

def sell_kd(symbol: str, start_date: str, end_date: str, initial_money: int,
            day: int, window: int) -> dict:
    data = StrategyData(symbol).get_kd_data(end_date)
    if data:
        start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
        initial_money = initial_money * 10000
        buy = []
        sell = []
        holding = False
        num_trades = 0
        num_wins = 0
        num_losses = 0
        total_profit = 0
        win_profit = 0
        loss_profit = 0
        balance = initial_money
        
        df = pd.DataFrame(data, columns=['date', 'open', 'max', 'min', 'close'])
        lowest_low = df['min'].rolling(window=day, min_periods=1).min()
        highest_high = df['max'].rolling(window=day, min_periods=1).max()
        rsv = (df['close'].astype(float) - lowest_low) / (highest_high - lowest_low) * 100
        smooth_factor = 1/window
        
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
        df['k'] = rsv.apply(KValue)
        df['d'] = df['k'].apply(DValue)
        df['rsv'] = rsv
        new_data = df.loc[df['date'] >= start_date]

        for i in range(len(new_data)):
            # Sell signal (K value < D value)
            if i > 0 and new_data.iloc[i]['k'] < new_data.iloc[i]['d'] and new_data.iloc[i-1]['k'] > new_data.iloc[i-1]['d'] and not holding:
                sell.append((new_data.iloc[i]['date'], new_data.iloc[i]['close']))
                holding = True
            # Buy signal (K value > D value)
            elif new_data.iloc[i]['k'] > new_data.iloc[i]['d'] and new_data.iloc[i-1]['k'] < new_data.iloc[i-1]['d'] and holding:
                buy.append((new_data.iloc[i]['date'], new_data.iloc[i]['close']))
                holding = False
                num_trades += 1
                per_roi = sell[-1][1] / buy[-1][1] - 1
                profit = per_roi * balance
                total_profit += profit
                balance += profit
                if profit > 0:
                    num_wins += 1
                    win_profit += profit
                else:
                    num_losses += 1
                    loss_profit += profit

        # Calculate metrics
        total_days = len(new_data)
        win_rate = num_wins / num_trades * 100 if num_trades > 0 else 0 # 計算勝率(%)
        roi = (balance - initial_money) / initial_money * 100 # 計算報酬率(%)，即總盈虧/初始資金
        # 計算平均獲利虧損比 aka 賺賠比
        if num_losses and num_wins > 0:
            average_risk_reward_ratio = (abs(win_profit / num_wins)) / (abs(loss_profit / num_losses)) 
        elif num_losses == 0:
            average_risk_reward_ratio = "無限大"
        else:
            average_risk_reward_ratio = 0
        if loss_profit < 0:
            profit_factor = abs(win_profit) / abs(loss_profit)
        elif loss_profit == 0 and win_profit > 0:
            profit_factor = "無限大"
        else:
            profit_factor = 0
        metrics = {
            'total_days': total_days,
            'total_trades': num_trades,
            'num_wins': num_wins,
            'num_losses': num_losses,
            'win_rate': f"{round(win_rate, 2)}%",
            'roi': f"{round(roi, 2)}%",
            'total_profit': int(total_profit),
            'average_risk_reward_ratio': round(average_risk_reward_ratio, 2),
            'profit_factor': round(profit_factor, 2),
        }
        return metrics

from .strategy_data import StrategyData
from .stock_strategy import StockStrategy


class StockAnalyzer:
    def __init__(
        self,
        transaction_type: str,
        initial_money: int,
        strategy: StockStrategy,
        data: StrategyData,
    ):
        self.transaction_type = transaction_type
        self.initial_money = initial_money
        self.strategy = strategy
        self.data = data

    @property
    def calculate_trading_metric(self):
        total_days, strategy = self.strategy.calculate(self.data)
        if (
            self.transaction_type == "buy"
            and strategy["positive"][0][0] > strategy["negative"][0][0]
        ):
            strategy["negative"].pop(0)
        elif (
            self.transaction_type == "sell"
            and strategy["positive"][0][0] < strategy["negative"][0][0]
        ):
            strategy["positive"].pop(0)

        initial_money = self.initial_money * 10000
        num_wins = 0
        num_losses = 0
        total_profit = 0
        win_profit = 0
        loss_profit = 0
        balance = initial_money
        for pos, neg in zip(strategy["positive"], strategy["negative"]):
            if self.transaction_type == "buy":
                per_roi = neg[1] / pos[1] - 1
            elif self.transaction_type == "sell":
                per_roi = 1 - (pos[1] / neg[1])

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
        num_trades = min(len(strategy["positive"]), len(strategy["negative"]))
        win_rate = num_wins / num_trades * 100 if num_trades > 0 else 0  # 計算勝率(%)
        roi = (balance - initial_money) / initial_money * 100  # 計算報酬率(%)，即總盈虧/初始資金
        # 計算平均獲利虧損比 aka 賺賠比
        if num_losses and num_wins > 0:
            average_risk_reward_ratio = (abs(win_profit / num_wins)) / (
                abs(loss_profit / num_losses)
            )
        elif num_losses == 0:
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
            "total_days": total_days,
            "total_trades": num_trades,
            "num_wins": num_wins,
            "num_losses": num_losses,
            "win_rate": f"{round(win_rate, 2)}%",
            "roi": f"{round(roi, 2)}%",
            "total_profit": int(total_profit),
            "average_risk_reward_ratio": round(average_risk_reward_ratio, 2),
            "profit_factor": round(profit_factor, 2),
        }
        return metrics

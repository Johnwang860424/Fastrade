import models
from fastapi import HTTPException


def ma(transaction_type, short_term_ma, long_term_ma, start_date, end_date, initial_capital, symbol):
    if short_term_ma and long_term_ma:
        if short_term_ma >= long_term_ma:
            raise HTTPException(
                status_code=400, detail="long term ma must be greater than short term ma")
        elif transaction_type == "buy":
            return models.buy_ma(symbol, start_date, end_date, initial_capital, short_term_ma, long_term_ma)
        elif transaction_type == "sell":
            return models.sell_ma(symbol, start_date, end_date, initial_capital, short_term_ma, long_term_ma)
    else:
        raise HTTPException(
            status_code=400, detail="you must provide the argument for Simple Moving Average (SMA) line")


def macd(transaction_type, short_term_macd, long_term_macd, signal_dif, start_date, end_date, initial_capital, symbol):
    if short_term_macd and long_term_macd and signal_dif:
        if short_term_macd >= long_term_macd:
            raise HTTPException(
                status_code=400, detail="long term macd must be greater than short term macd")
        elif transaction_type == "buy":
            return models.buy_macd(symbol, start_date, end_date, initial_capital, short_term_macd, long_term_macd, signal_dif)
        elif transaction_type == "sell":
            return models.sell_macd(symbol, start_date, end_date, initial_capital, short_term_macd, long_term_macd, signal_dif)
    else:
        raise HTTPException(
            status_code=400, detail="you must provide the argument for Moving Average Convergence Divergence (MACD) line")


def kd(transaction_type, recent_days, k_d_argument, start_date, end_date, initial_capital, symbol):
    if recent_days and k_d_argument:
        if transaction_type == "buy":
            return models.buy_kd(symbol, start_date, end_date, initial_capital, recent_days, k_d_argument)
        elif transaction_type == "sell":
            return models.sell_kd(symbol, start_date, end_date, initial_capital, recent_days, k_d_argument)
    else:
        raise HTTPException(
            status_code=400, detail="you must provide the argument for KD line")

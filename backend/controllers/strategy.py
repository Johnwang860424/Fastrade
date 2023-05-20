import models
from fastapi import HTTPException


def ma(
    transaction_type,
    short_term_ma,
    long_term_ma,
    start_date,
    end_date,
    initial_capital,
    symbol,
):
    if short_term_ma and long_term_ma:
        if short_term_ma >= long_term_ma:
            raise HTTPException(
                status_code=400,
                detail="long term ma must be greater than short term ma",
            )
        data = models.strategy_data.MAStrategyData(
            symbol, start_date, end_date, long_term_ma
        )
        strategy = models.stock_strategy.MAStockStrategy(short_term_ma, long_term_ma)
        analyzer = models.stock_analyzer.StockAnalyzer(
            transaction_type, initial_capital, strategy, data
        )
        return analyzer.calculate_trading_metric

    else:
        raise HTTPException(
            status_code=400,
            detail="you must provide the argument for Simple Moving Average (SMA) line",
        )


def macd(
    transaction_type,
    short_term_macd,
    long_term_macd,
    signal_dif,
    start_date,
    end_date,
    initial_capital,
    symbol,
):
    if short_term_macd and long_term_macd and signal_dif:
        if short_term_macd >= long_term_macd:
            raise HTTPException(
                status_code=400,
                detail="long term macd must be greater than short term macd",
            )
        data = models.strategy_data.MACDStrategyData(symbol, end_date)
        strategy = models.stock_strategy.MACDStockStrategy(
            start_date, short_term_macd, long_term_macd, signal_dif
        )
        analyzer = models.stock_analyzer.StockAnalyzer(
            transaction_type, initial_capital, strategy, data
        )
        return analyzer.calculate_trading_metric
    else:
        raise HTTPException(
            status_code=400,
            detail="you must provide the argument for Moving Average Convergence Divergence (MACD) line",
        )


def kd(
    transaction_type,
    recent_days,
    k_d_argument,
    start_date,
    end_date,
    initial_capital,
    symbol,
):
    if recent_days and k_d_argument:
        data = models.strategy_data.KDStrategyData(symbol, end_date)
        strategy = models.stock_strategy.KDStockStrategy(
            start_date, recent_days, k_d_argument
        )
        analyzer = models.stock_analyzer.StockAnalyzer(
            transaction_type, initial_capital, strategy, data
        )
        return analyzer.calculate_trading_metric
    else:
        raise HTTPException(
            status_code=400, detail="you must provide the argument for KD line"
        )

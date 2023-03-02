import models

def get_price(symbol: str, start_date: str, end_date: str, price_type: str):
    price_list = models.StockPrice(symbol, start_date, end_date)
    if price_type == "origin":
        if price_list.get_original_price():
            return price_list.get_original_price()
        return False
    elif price_type == "adjust":
        if price_list.get_adjusted_price():
            return price_list.get_adjusted_price()
        return False
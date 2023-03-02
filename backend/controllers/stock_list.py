import models
import re

def get_stock_list(stock_type: str = None) -> (dict[str, list[dict[str, str]]]):
    if stock_type:
        stock_type = "1" if re.search(r"(?i)^(listed)$", stock_type) else "2"
        stock = models.StockList(stock_type)
        return stock.get_specified_stock_list()
    return models.StockList.get_all_stock_list()
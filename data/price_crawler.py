from config import connection
from datetime import datetime
from insert_stock_price import get_stock_list
import itertools
import pytz
import requests
import time

tw_time = pytz.timezone('Asia/Taipei')

tw_time = datetime.today()

listed_current_date = tw_time.strftime("%Y%m%d")
OTC_current_date = tw_time.strftime("%Y/%m")
year = str(int(OTC_current_date[:4]) - 1911)
OTC_current_date = OTC_current_date.replace(OTC_current_date[:4], year)

def insert_current_price(data: list[tuple]):
    stock_connection = connection.get_connection()
    try:
        with stock_connection as connect:
            sql = f"""INSERT IGNORE INTO historical_price{data[0][1]} VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""
            connect.cursor().executemany(sql, data)
            connect.commit()
    except Exception as e:
        print(e)

def listed_price_crawler(symbol: str) -> list:
    url = "https://www.twse.com.tw/zh/exchangeReport/STOCK_DAY"
    params = {"response":"json", "date": listed_current_date, "stockNo": symbol}
    res = requests.post(url, params=params)
    if "data" in res.json():
        data = res.json()["data"][-5:]
        for i, item in enumerate(data):
            item[0] = item[0].replace("/", "-")
            ad = str(int(item[0][0:3])+1911)
            item[0] = item[0].replace(item[0][0:3], ad)
            item[1] = item[1].replace(",", "")
            item[2] = item[2].replace(",", "")
            item[3] = item[3].replace(",", "")
            item[4] = item[4].replace(",", "")
            item[5] = item[5].replace(",", "")
            item[6] = item[6].replace(",", "")
            item[7] = item[7].replace("+", "").replace("X", "")
            item.insert(1, params["stockNo"])
            item[-1] = item[-1].replace(",", "")
            data[i] = tuple(item)
        return data
    
def OTC_price_crawler(symbol: str) -> list:
    url = "https://www.tpex.org.tw/web/stock/aftertrading/daily_trading_info/st43_result.php?l=zh-tw"
    params = {"d": OTC_current_date, "stkno": symbol}
    res = requests.post(url, params=params)
    if res.json()["aaData"]:
        data = res.json()["aaData"][-5:]
        for i, item in enumerate(data):
            item[0] = item[0].replace("/", "-")
            ad = str(int(item[0][0:3])+1911)
            item[0] = item[0].replace(item[0][0:3], ad)
            item[1] = int(item[1].replace(",", "")) * 1000
            item[2] = int(item[2].replace(",", "")) * 1000
            item[3] = item[3].replace(",", "")
            item[4] = item[4].replace(",", "")
            item[5] = item[5].replace(",", "")
            item[6] = item[6].replace(",", "")
            item[7] = item[7].replace("+", "")
            item.insert(1, params["stkno"])
            item[-1] = item[-1].replace(",", "")
            data[i] = tuple(item)
        return data

listed_stock_list = get_stock_list("1")
OTC_stock_list = get_stock_list("2")
try:
    for listed_stock, OTC_stock in itertools.zip_longest(listed_stock_list, OTC_stock_list):
        listed_stock_data = listed_price_crawler(listed_stock)
        insert_current_price(listed_stock_data)
        OTC_stock_data = OTC_price_crawler(OTC_stock)
        insert_current_price(OTC_stock_data)
        print(listed_stock, OTC_stock)
        time.sleep(6)
except Exception:
    time.sleep(6)
    for listed_stock, OTC_stock in itertools.zip_longest(listed_stock_list, OTC_stock_list):
        listed_stock_data = listed_price_crawler(listed_stock)
        insert_current_price(listed_stock_data)
        OTC_stock_data = OTC_price_crawler(OTC_stock)
        insert_current_price(OTC_stock_data)
        print(listed_stock, OTC_stock)
        time.sleep(6)

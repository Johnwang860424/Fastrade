from config import connection
from datetime import datetime
import pytz
import requests

tw_time = pytz.timezone('Asia/Taipei')

tw_time = datetime.now(tw_time)

listed_current_date = tw_time.strftime("%Y%m%d")
OTC_current_date = tw_time.strftime("%Y/%m/%d")
year = str(int(OTC_current_date[:4]) - 1911)
OTC_current_date = OTC_current_date.replace(OTC_current_date[:4], year)

listed_stock = f"https://www.twse.com.tw/exchangeReport/TWTB8U?response=json&strDate={listed_current_date}"

OTC_stock = f"https://www.tpex.org.tw/web/bulletin/parvaluechg/rslt_result.php?l=zh-tw&d={OTC_current_date}&ed={OTC_current_date}"

def insert_par_value(data: list[tuple]):
    stock_connection = connection.get_connection()
    try:
        with stock_connection.cursor(dictionary=True) as cursor:
            sql = """INSERT ignore INTO `par value after change` VALUES (%s, %s, %s, %s)"""
            cursor.executemany(sql, data)
            stock_connection.commit()
    except Exception as e:
        print(e)
    finally:
        stock_connection.close()

def get_stock_par_value(url) -> list[tuple]:
    res = requests.get(url)
    new_data = []
    if "data" in res.json():
        raw_data = res.json()["data"]   
        for item in raw_data:
            item[0] = item[0].replace("/", "-")
            ad = str(int(item[0][0:3])+1911)
            item[0] = item[0].replace(item[0][0:3], ad)
            item[3] = item[3].replace(",", "")
            item[4] = item[4].replace(",", "")
            new_data.append((item[1], item[0], item[3], item[4]))
        return new_data
    elif "aaData" in res.json():
        raw_data = res.json()["aaData"]
        for item in raw_data:
            item[0] = item[0] + 19110000
            item[3] = item[3].replace(",", "")
            item[4] = item[4].replace(",", "")
            new_data.append((item[1], item[0], item[3], item[4]))
        return new_data

new_data = get_stock_par_value(listed_stock) + get_stock_par_value(OTC_stock)
print(new_data)
insert_par_value(new_data)
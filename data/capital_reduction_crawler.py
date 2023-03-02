from config import connection
import requests
import time

def insert_par_value(data: list[tuple]):
    stock_connection = connection.get_connection()
    try:
        with stock_connection.cursor(dictionary=True) as cursor:
            sql = """INSERT ignore INTO `Capital Reduction` VALUES (%s, %s, %s, %s)"""
            cursor.executemany(sql, data)
            stock_connection.commit()
    except Exception as e:
        print(e)
    finally:
        stock_connection.close()

# 歷史股票減資恢復買賣參考價格
def get_data_for_reduction():
    try:
        new_data = []
        listed_stock = f"https://www.twse.com.tw/zh/exchangeReport/TWTAUU?response=json"
        listed_res = requests.get(listed_stock)
        raw_data = listed_res.json()["data"]   
        for item in raw_data:
            item[0] = item[0].replace("/", "-")
            ad = str(int(item[0][0:3])+1911)
            item[0] = item[0].replace(item[0][0:3], ad)
            item[3] = item[3].replace(",", "")
            item[4] = item[4].replace(",", "")
            new_data.append((item[1], item[0], item[3], item[4]))
        OTC_stock = "https://www.tpex.org.tw/web/stock/exright/revivt/revivt_result.php?l=zh-tw"
        OTC_res = requests.get(OTC_stock)
        raw_data = OTC_res.json()
        for item in raw_data["aaData"]:
            item[0] = item[0] + 19110000
            item[3] = item[3].replace(",", "")
            item[4] = item[4].replace(",", "")
            new_data.append((item[1], item[0], item[3], item[4]))
        insert_par_value(new_data)
    except:
        time.sleep(6)
        get_data_for_reduction()
        
get_data_for_reduction()
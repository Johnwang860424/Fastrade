from config import connection
from config import switch_category
import numpy as np
import pandas as pd
import requests
import time

listed_url = "https://isin.twse.com.tw/isin/class_main.jsp?owncode=&stockname=&isincode=&market=1&issuetype=1&industry_code=&Page=1&chklike=Y"
otc_url = "https://isin.twse.com.tw/isin/class_main.jsp?owncode=&stockname=&isincode=&market=2&issuetype=4&industry_code=&Page=1&chklike=Y"
            
def stock_list(url: str):
    stock_connection = connection.get_connection()
    try:
        with stock_connection.cursor() as cursor:
            response = requests.get(url)
            listed = pd.read_html(response.text)[0]
            # select the first row of the DataFrame listed and return it as a Series
            listed.columns = listed.iloc[0,:]
            # return a new DataFrame with only columns "有價證券代號","有價證券名稱","市場別","產業別","公開發行/上市(櫃)/發行日"
            listed = listed[["有價證券代號","有價證券名稱","市場別","產業別","公開發行/上市(櫃)/發行日"]]
            # select all the rows starting from the first row of the DataFrame listed and return them as a new DataFrame
            listed = listed.iloc[1:]
            # convert %Y/%m/%d to %Y-%m-%d
            listed["公開發行/上市(櫃)/發行日"] = pd.to_datetime(listed["公開發行/上市(櫃)/發行日"], format='%Y/%m/%d').dt.strftime('%Y-%m-%d')
            # replace "上市" to 1 and "上櫃" to 2
            listed["市場別"] = np.where(listed["市場別"] == "上市", "1", "2")
            # replace "產業別" to number
            listed["產業別"] = listed["產業別"].apply(switch_category)
            # Prepare the SQL statement
            sql = """INSERT INTO `stock_list`(`symbol`, `name`, `type`, `category`, `issuing date`) VALUES (%s, %s, %s, %s, %s) AS list
                     ON DUPLICATE KEY UPDATE `name` = list.`name`,
                                             `type` = list.`type`,
                                             `category` = list.`category`"""
            # Prepare the data
            data = [tuple(x) for x in listed.to_numpy()]
            # Execute the SQL statement with the data
            cursor.executemany(sql, data)
            stock_connection.commit()
        return cursor.rowcount
    except Exception as e:
        print(e)
        return e
    finally:
        stock_connection.close()

try:
    stock_list(listed_url)
    stock_list(otc_url)
except Exception:
    time.sleep(6)
    stock_list(listed_url)
    stock_list(otc_url)
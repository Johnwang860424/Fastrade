import aiohttp
import asyncio
import datetime
import pytz
from bs4 import BeautifulSoup

from config import connection
from insert_stock_price import get_stock_list

stock_connection = connection.get_connection()

async def get_dividend_change_date(symbol: str, date: str) -> dict:
    try:
        with stock_connection.cursor(dictionary=True) as cursor:
            table = f'historical_price{symbol}'
            sql = f"""SELECT MAX({table}.date) AS date
                      FROM {table}
                      WHERE date < %s
                      AND close != 0 LIMIT 1;"""
            cursor.execute(sql, (date, ))
            return cursor.fetchone()
    except Exception as e:      
        print(e)

async def insert_dividends(data_cash: list[tuple], data_stock: list[tuple]):
    try:
        with stock_connection.cursor(dictionary=True) as cursor:
            if data_cash:
                sql_cash = """INSERT INTO `cash_dividend`(`symbol`, `ex_div_date`, `cash_dividend`)
                            VALUES (%s, %s, %s)
                            ON DUPLICATE KEY UPDATE `symbol` = VALUES(`symbol`),
                                                    `ex_div_date` = VALUES(`ex_div_date`),
                                                    `cash_dividend` = VALUES(`cash_dividend`)"""
                cursor.executemany(sql_cash, data_cash)
            elif data_stock:
                sql_stock = """INSERT INTO `stock_dividend`(`symbol`, `ex_right_date`, `stock_dividend`)
                            VALUES (%s, %s, %s)
                            ON DUPLICATE KEY UPDATE `symbol` = VALUES(`symbol`),
                                                    `ex_right_date` = VALUES(`ex_right_date`),
                                                    `stock_dividend` = VALUES(`stock_dividend`)"""
                cursor.executemany(sql_stock, data_stock)
                stock_connection.commit()
    except Exception as e:
        print(e)

async def fetch(session, url):
    async with session.get(url) as response:
        return await response.text()

async def get_dividend_data(session, symbol):
    try:
        url = f"https://tw.stock.yahoo.com/quote/{symbol}/dividend"
        response_text = await fetch(session, url)
        soup = BeautifulSoup(response_text, "html.parser")
        ul = soup.find("ul", class_="M(0) P(0) List(n)")
        li = ul.find("li")
        cash_dividend_list = []
        stock_dividend_list = []
        if li:
            ex_div_date = li.find("div", class_="Fxg(1) Fxs(1) Fxb(0%) Ta(end) Mend($m-table-cell-space) Mend(0):lc Miw(108px)").text.replace("/", "-")
            ex_right_date = li.find_all("div", class_="Fxg(1) Fxs(1) Fxb(0%) Ta(end) Mend($m-table-cell-space) Mend(0):lc Miw(108px)")[1].text.replace("/", "-")
            cash_dividend = li.find("div", class_="Fxg(1) Fxs(1) Fxb(0%) Ta(end) Mend($m-table-cell-space) Mend(0):lc Miw(62px)").text
            stock_dividend = li.find_all("span")[1].text
            if ex_div_date[:4].isdigit() or ex_right_date[:4].isdigit():
                tw_time = pytz.timezone('Asia/Taipei')
                current_date = datetime.datetime.now(tw_time).strftime("%Y-%m-%d")
                if "-" not in [ex_div_date] and int(ex_div_date[:4]) >= 2000 and datetime.datetime.strptime(current_date, "%Y-%m-%d").date() > datetime.datetime.strptime(ex_div_date, "%Y-%m-%d").date():
                    new_ex_div_date = (await get_dividend_change_date(symbol, ex_div_date))["date"]
                    if new_ex_div_date:
                        data = (symbol, new_ex_div_date, cash_dividend)
                        cash_dividend_list.append(data)
                if "-" not in [ex_right_date] and int(ex_right_date[:4]) >= 2000 and datetime.datetime.strptime(current_date, "%Y-%m-%d").date() > datetime.datetime.strptime(ex_right_date, "%Y-%m-%d").date():
                    data = (symbol, ex_right_date, stock_dividend)
                    stock_dividend_list.append(data)
        await insert_dividends(cash_dividend_list, stock_dividend_list)
    except Exception as e:
        print(f"查無資料: {symbol}")
        print(e)

async def main():
    async with aiohttp.ClientSession() as session:
        stock_list = get_stock_list("%")
        tasks = [get_dividend_data(session, symbol) for symbol in stock_list]
        await asyncio.gather(*tasks)

if __name__ == '__main__':
    asyncio.run(main())
    print("Done!")
    stock_connection.close()

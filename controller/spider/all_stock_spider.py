# -*- coding: utf-8 -*-
# @Time : 2023/4/3 21:59
# @Author : JIQ
# @Email : jiq1314an@gmail.com

## 翻页爬取数据
import datetime
import time
import traceback

import numpy as np
import pandas as pd
import requests

from controller.spider.utils import data_transform_all_stock
from controller.sql_utils import get_conn, close_conn


def all_stock_crawl(max_page=2):
    ### 1. 准备工作
    headers = {
        # 浏览器伪装
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.0.0 Safari/537.36'
    }
    session = requests.Session()
    session.get("https://xueqiu.com/", headers=headers)
    ### 2. 开始爬取
    data_source = []
    for page in range(1, max_page + 1):
        url = f'https://stock.xueqiu.com/v5/stock/screener/quote/list.json?page={page}&size=30&order=desc&orderby=percent&order_by=percent&market=CN&type=sh_sz'
        response = session.get(url, headers=headers)
        json_data = response.json()

        data_df = data_transform_all_stock(json_data)

        data_source.append(data_df)

    return pd.concat(data_source, axis=0)


def insert_all_stock_info(data_source: pd.DataFrame):
    """
    插入所有股票信息数据
    """
    cursor = None
    conn = None
    try:
        # crawl_time = datetime.date.today()  # 获取抓取时间
        crawl_time = datetime.datetime.now() # 获取抓取时间【加上时分秒】

        print(f"{time.asctime()} 开始插入所有股票信息数据...")
        conn, cursor = get_conn()
        sql = "insert into all_stock_info values(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"

        for k, v in zip(data_source.index, data_source.values):
            # 为了区分热度，便于后面获取top10【30只股票之间相邻的股票时间设置相差1min】
            crawl_time += datetime.timedelta(minutes=1)
            # data_source.index 是一维数组，data_source.values 是二维数组

            # print(np.insert(v, [0, 0], [crawl_time, k]))
            cursor.execute(sql, list(np.insert(v, [0, 0], [crawl_time, k])))

        conn.commit()  # 提交事务update delete insert操作
        print(f"{time.asctime()} 插入所有股票信息数据完毕!!!")
    except:
        traceback.print_exc()
    finally:
        close_conn(conn, cursor)


def update_all_stock_info(data_source: pd.DataFrame):
    """
    更新all_stock_info表
    """
    cursor = None
    conn = None
    try:
        # symbol 相同 变更新数据，不同直接写入
        conn, cursor = get_conn()
        # sql = "insert into all_stock_info (update_time, symbol, name, current, chg, change, current_year_percent, volume , amount, turnover_rate, pe_ttm, dividend_yield, market_capital) values(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
        sq1_query = "select %s in (SELECT symbol from all_stock_info)"  # 对比是否存在相同的symbol
        sql_delete = "delete from all_stock_info where symbol = %s"

        print(f"{time.asctime()} 开始更新最新数据...")
        flag = False

        for s in data_source.index:
            cursor.execute(sq1_query, s)  # 传入新获取的symbol
            if cursor.fetchone()[0]:  # symbol 存在
                cursor.execute(sql_delete, s)
                conn.commit()  # 提交事务update delete insert操作
                flag = True  # 表示需要更新数据

        insert_all_stock_info(data_source)
        if flag:
            print(f"{time.asctime()} 存在重复数据，删除后更新最新数据，完毕!!!")
        else:
            print(f"{time.asctime()} 不存在重复数据，直接获取最新数据，完毕!!!")
    except:
        traceback.print_exc()
    finally:
        close_conn(conn, cursor)


if __name__ == "__main__":
    # Test
    max_page = 1
    data_source = all_stock_crawl(max_page)
    # insert_all_stock_info(data_source)
    update_all_stock_info(data_source)

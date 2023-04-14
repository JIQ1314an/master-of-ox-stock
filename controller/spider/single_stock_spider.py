# -*- coding: utf-8 -*-
# @Time : 2023/3/24 10:48
# @Author : JIQ
# @Email : jiq1314an@gmail.com
import datetime
import time
import json

import numpy as np
import pandas as pd
import pymysql
import requests
import traceback
import sys
from selenium.webdriver import Chrome, ChromeOptions
from selenium.webdriver.common.by import By

from controller.spider.all_stock_spider import all_stock_crawl, update_all_stock_info
from controller.spider.utils import date2timestamp, timestamp2date
from controller.sql_utils import get_conn, close_conn


def get_single_stock_info(ticker, begin, end):
    """根据ticker获取美股、A股、港股的历史价格信息【从雪球获取数据】"""
    url = f'https://stock.xueqiu.com/v5/stock/chart/kline.json'
    ploads = {'symbol': ticker.upper(), 'begin': date2timestamp(begin), 'end': date2timestamp(end),
              'period': 'day', 'type': 'before'}
    # 伪装
    headers = {
        # 浏览器伪装
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.0.0 Safari/537.36'
    }
    session = requests.Session()
    session.get("https://xueqiu.com/", headers=headers)
    r = session.get(url, headers=headers, params=ploads)  # 打印变量r显示响应码

    data = json.loads(r.text)  # r.json()
    df = pd.DataFrame(data['data']['item'], columns=data['data']['column'])

    if df.empty: return None

    df['date'] = df['timestamp'].apply(timestamp2date)
    return df


def get_single_stock_info_selected(ticker, begin, end, selected_cols):
    """仅选取个股的交易日，收盘价，涨跌幅，成交量四项信息"""
    df = get_single_stock_info(ticker, begin, end)

    if df is None: return None

    df_selected = df[selected_cols].copy()
    df_selected.rename(columns={'percent': 'change'}, inplace=True)
    df_selected['date'] = df_selected['date'].astype('datetime64')  # 改变数据类型
    df_selected.set_index('date', inplace=True)
    return df_selected


def get_baidu_hot():
    """
    return: 返回百度热搜
    """
    option = ChromeOptions()
    option.add_argument("--headless")  # 隐藏浏览器
    option.add_argument('--no-sandbox')  # linux上对应的驱动，需要禁用sandbox

    url = "https://top.baidu.com/board?tab=realtime"
    brower = Chrome(options=option)
    brower.get(url)
    # 找热搜标签
    # c1 = brower.find_elements_by_xpath()
    c1 = brower.find_elements(by=By.XPATH, value='//*[@id="sanRoot"]/main/div[2]/div/div[2]/div/div[2]/a/div[1]')
    c2 = brower.find_elements(by=By.XPATH, value='//*[@id="sanRoot"]/main/div[2]/div/div[2]/div/div[1]/div[2]')
    # print(c)
    context = [i.text + v.text for i, v in zip(c1, c2)]  # 获取标签内容
    #     print(context)
    return context


def update_hotsearch():
    """
    将疫情热搜插入数据库
    """
    cursor = None
    conn = None
    try:
        context = get_baidu_hot()
        print(f"{time.asctime()} 开始更新热搜数据")
        conn, cursor = get_conn()
        sq1 = "insert into hotsearch (dt, content) values (%s, %s)"
        ts = time.strftime("%Y-%m-%d %X")  # 年-月-日 时:分:秒
        for i in context:
            cursor.execute(sq1, (ts, i))  # 插入数据
        conn.commit()  # 提交事务保存数据
        print(f"{time.asctime()} 数据更新完毕")
    except:
        traceback.print_exc()
    finally:
        close_conn(conn, cursor)


def insert_single_stock_info(symbol: str, begin: str, end: str):
    """
    插入单股股票信息
    """
    cursor = None
    conn = None
    selected_cols = ['date', 'timestamp', 'open', 'high', 'low', 'volume', 'chg', 'percent',
                     'turnoverrate', 'amount', 'close']
    df = get_single_stock_info_selected(symbol, begin, end, selected_cols)

    if df is None: return print(f"{symbol}股票为新股票，获取不到历史信息!!!")

    try:
        print(f"{time.asctime()} 开始插入{symbol}单股股票信息...")
        conn, cursor = get_conn()
        sql = "insert into single_stock_info values(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"

        for v in df.values:
            # df.values 是二维数组
            features = list(v)
            features.insert(0, symbol)
            cursor.execute(sql, features)

        conn.commit()  # 提交事务update delete insert操作
        print(f"{time.asctime()} 插入{symbol}单股股票信息完毕!!!")
    except:
        traceback.print_exc()
    finally:
        close_conn(conn, cursor)


def update_single_stock_info(symbol: str):
    """
    更新single_stock_info表
    """
    cursor = None
    conn = None

    try:
        conn, cursor = get_conn()
        sq1_query = "select timestamp from single_stock_info where symbol = %s order by timestamp desc limit 1"  # 获取当前最大时间戳
        cursor.execute(sq1_query, symbol)
        query_res = cursor.fetchone()[0]

        end = time.strftime("%Y-%m-%d")  # 截止到当天

        if query_res < date2timestamp(end):  # cursor.fetchone()[0]等价fetchall()[0][0]
            print(f"{time.asctime()} 开始更新{symbol}最新数据...")
            begin = timestamp2date(query_res + 86400 * 1000)  # 获取上次爬取数据的时间后一天时间

            insert_single_stock_info(symbol, begin, end)

            print(f"{time.asctime()} 更新{symbol}最新数据完毕!!!")
        else:
            print(f"{time.asctime()} {symbol}已是最新数据! ")
    except:
        traceback.print_exc()
    finally:
        close_conn(conn, cursor)


def insert_or_update_single(data_source):
    begin = "2022-12-1"
    end = "2023-3-31"
    for symbol in data_source.index:
        conn, cursor = get_conn()
        sq1_query = "select %s in (select distinct(symbol) from single_stock_info)"  # 获取当前最大时间戳
        cursor.execute(sq1_query, symbol)

        if cursor.fetchone()[0]:
            update_single_stock_info(symbol)
        else:
            insert_single_stock_info(symbol, begin, end)


if __name__ == "__main__":
    max_page = 1
    data_source = all_stock_crawl(max_page)

    l = len(sys.argv)
    if l == 1:
        s = """
        请输入参数
        参数说明：
        up_single 更新单股数据信息
        up_hot 更新实时热搜
        up_all 更新所有股票信息
        """
        print(s)
    else:
        order = sys.argv[1]
        if order == 'up_single':
            insert_or_update_single(data_source)
        elif order == 'up_hot':
            update_hotsearch()
        elif order == 'up_all':
            update_all_stock_info(data_source)

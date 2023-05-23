# -*- coding: utf-8 -*-
# @Time : 2023/4/9 21:48
# @Author : JIQ
# @Email : jiq1314an@qq.com
import os

import pandas as pd

from controller.spider.utils import timestamp2date
from controller.sql_utils import query


def get_stock_basic_info():
    """
    :return: 返回最新所有股票的唯一标识 symbol 和 名称name
    """
    # 先获取最新的30个热门股票【因为一次爬取就是获取30只热门的股票】
    # sql = """
    # select name, symbol from
    # (select distinct name, symbol, update_time from all_stock_info order by update_time desc limit 30) t
    #  order by update_time asc limit 10
    # """
    sql = "select distinct name, symbol from all_stock_info order by update_time desc limit 30"
    basic_info = query(sql)
    # print(basic_info)
    return basic_info


def get_test_stock_basic_info(test_n=3):
    # 得到测试股票的symbol和name
    test_stock_symbols = ["SZ301136", "SZ300295", "SZ300113"]  # 根据测试r2从低到高
    sql = "select distinct name, symbol from all_stock_info where symbol in {}" \
        .format(tuple(set(test_stock_symbols)))
    test_stock_basic_info = query(sql)
    return test_stock_basic_info[:test_n]


def get_single_stock_info(symbol="SH603000", data_size=350):
    sql = f"select * from (select * from single_stock_info where symbol='{symbol}' " \
          f"order by timestamp desc limit {data_size}) t " \
          f"order by timestamp asc"
    # print(sql)
    single_stock_info = query(sql)
    # if len(single_stock_info) == 0:  # 说明此时没有股票对应的历史数据【一般情况是最新的股票】
    #     os.system("python {}/spider/run.py up_all".format(os.path.dirname(__file__)))
    col_names = ['symbol', 'timestamp', 'open', 'high', 'low', 'volume', 'chg',
                 'change', 'turnover_rate', 'amount', 'close']
    df = pd.DataFrame(single_stock_info, columns=col_names)
    # date handle
    df['symbol'] = df['timestamp'].apply(lambda t: timestamp2date(t))
    df.rename(columns={'symbol': 'date'}, inplace=True)
    df['date'] = df['date'].astype('datetime64')  # 改变数据类型
    df.set_index('date', inplace=True)

    df.drop_duplicates(inplace=True)
    return df


if __name__ == "__main__":
    # df = get_single_stock_info()
    # print(df)
    # df.to_csv("SH603000.csv", index=False)

    print(get_stock_basic_info()[-10:])

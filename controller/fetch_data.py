# -*- coding: utf-8 -*-
# @Time : 2023/4/9 21:48
# @Author : JIQ
# @Email : jiq1314an@qq.com
import pandas as pd

from controller.spider.utils import timestamp2date
from controller.sql_utils import query


def get_stock_basic_info():
    """
    :return: 返回所有股票的唯一标识 symbol 和 名称name
    """
    sql = "select distinct name, symbol from all_stock_info"
    basic_info = query(sql)
    # print(basic_info)
    return basic_info


def get_single_stock_info(symbol="SH603000"):
    sql = f"select * from single_stock_info where symbol='{symbol}'"
    # print(sql)
    single_stock_info = query(sql)
    col_names = ['symbol', 'timestamp', 'open', 'high', 'low', 'volume', 'chg',
                 'change', 'turnover_rate', 'amount', 'close']
    df = pd.DataFrame(single_stock_info, columns=col_names)
    # date handle
    df['symbol'] = df['timestamp'].apply(lambda t: timestamp2date(t))
    df.rename(columns={'symbol': 'date'}, inplace=True)
    df['date'] = df['date'].astype('datetime64')  # 改变数据类型
    df.set_index('date', inplace=True)
    return df


if __name__ == "__main__":
    print(get_single_stock_info())

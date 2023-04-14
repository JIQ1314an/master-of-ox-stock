# -*- coding: utf-8 -*-
# @Time : 2023/3/24 10:49
# @Author : JIQ
# @Email : jiq1314an@gmail.com
import numpy as np
import pandas as pd
import pymysql
import time
from datetime import datetime


def date2timestamp(date):
    timestamp = time.mktime(datetime.strptime(date, "%Y-%m-%d").timetuple())
    return int(1000 * timestamp)


def timestamp2date(timestamp):
    return datetime.fromtimestamp(timestamp / 1000).strftime('%Y-%m-%d')


def data_transform_all_stock(json_data):
    cols_en = ['symbol', 'name', 'current', 'chg', 'percent', 'current_year_percent',
               'volume', 'amount', 'turnover_rate', 'pe_ttm', 'dividend_yield', 'market_capital']
    cols_zh = ['股票代码', '股票名称', '当前价', '涨跌额', '涨跌幅', '年初至今',
               '成交量', '成交额', '换手率', '市盈率(TTM)', '股息率', '市值']
    row_data_list = json_data['data']['list']
    data_list = []
    for data in row_data_list:
        # 创建数据字典
        data_dict = {}
        # 根据特征值名称（英文）获取数据并修改列名
        for (col_en, col_zh) in zip(cols_en, cols_zh):
            data_dict[col_zh] = data[col_en]
        # csv_write.writerow(data_dict)
        # 将多条数据字典存到list中
        # print(data_dict['股票名称'], end='\t')
        data_list.append(data_dict)

    # dict转化为df类型
    data_df = pd.DataFrame(data_list).set_index('股票代码').replace(np.NaN, None)
    # print('\nTab size：', len(data_df))

    return data_df

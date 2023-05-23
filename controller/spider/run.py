# -*- coding: utf-8 -*-
# @Time : 2023/4/30 20:37
# @Author : JIQ
# @Email : jiq1314an@qq.com
import datetime
import sys

from controller.spider.all_stock_spider import all_stock_crawl, update_all_stock_info
from controller.spider.single_stock_spider import insert_or_update_single, update_hotsearch

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
            end = datetime.datetime.now().date().strftime('%Y-%m-%d')
            insert_or_update_single(data_source, begin="2021-12-1", end=end)
        elif order == 'up_hot':
            update_hotsearch()
        elif order == 'up_all':
            update_all_stock_info(data_source)

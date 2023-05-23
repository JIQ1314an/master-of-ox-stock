# -*- coding: utf-8 -*-
# @Time : 2023/4/19 22:33
# @Author : JIQ
# @Email : jiq1314an@qq.com

import json

import re
import chardet
import pandas as pd
import requests
from bs4 import BeautifulSoup
from controller.spider.utils import remove_child_content, get_detailed_news_url


class NewsSpider:
    def __init__(self, symbol):
        self.symbol = symbol

    def get_news_details(self, news_url: str):
        # 1.获取html数据
        headers = {  # 浏览器伪装
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.0.0 Safari/537.36'
        }
        response = requests.get(news_url, headers=headers)
        pattern = re.compile('<meta.*?charset=["\']*(.+?)["\'>]', flags=re.I)
        try:
            encoding = re.findall(pattern, response.text)[0]
        except:
            # 使用chardet检测编码格式
            encoding = chardet.detect(response.content)['encoding']

        if encoding.upper().startswith('GB'):
            encoding = 'GB18030'  # 字符数 GB2312 < GBK < GB18030

        # 2.解析处理
        soup = BeautifulSoup(response.content.decode(encoding, errors='ignore'), 'html.parser')  # 解析HTML页面
        expr = r'^(main-|text|post_body)|-content$'  # 查找所有以 "main" 开头或以 "context" 结尾的 div 标签
        main_divs = soup.find_all('div', {'class': re.compile(expr)})
        # print(main_divs)
        # main_divs = soup.find_all('div', class_=lambda x: x and ('main' in x or 'text' in x or x.endswith('content')))

        # 3.获取文本数据 【p标签下的文本数据均会匹配】
        text_set = set()  # 创建一个集合，用于存储已经提取的文本段落

        for main_div in main_divs:  # 提取每个 div 标签中的 p 标签内容
            # p_tags = main_div.find_all('p', recursive=False) # 查找 div 标签下第一层子节点中的 p 标签
            p_tags = main_div.select('p:not([class]):not([style])')  # 查找 不带修饰的 p 标签  :not([id])

            for p_tag in p_tags:  # 提取每个 p 标签中的文本内容
                # if p_tag.name != 'p': continue # 只提取p标签内容，超链接文本本身也是p标签
                text = p_tag.text.strip()  # p_tag.get_text().strip()
                if text in text_set:  # 如果集合中已经存在相同的文本，跳过不进行处理
                    continue
                # 对文本进行处理，比如去除多余的空格和换行符等等，之后加入集合中
                text_set.add(' '.join(text.split()))
                # text_set.add(text)

        # 4.再次对set中的数据进行包含关系的处理 如 {a, b} 若 a中包含b则剔除b，属于内容重复
        # print(text_set)
        return remove_child_content(text_set)

    def get_single_stock_news_info(self, page=1, count=20):
        """根据ticker获取美股、A股、港股单只股票的【资讯新闻信息】
        ticker: 股票的symbol
        count: 爬取资讯数量，最大20
        page：默认无上限，直到数据爬取完
        """
        global data
        url = f'https://xueqiu.com/statuses/stock_timeline.json'
        ploads = {'symbol_id': self.symbol.upper(), 'count': count, 'source': '自选股新闻', 'page': page}
        # 伪装
        headers = {
            # 浏览器伪装
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.0.0 Safari/537.36'
        }
        session = requests.Session()
        session.get("https://xueqiu.com/", headers=headers)
        r = session.get(url, headers=headers, params=ploads)  # 打印变量r显示响应码
        data = {}
        try:
            data = json.loads(r.text)  # r.json()
        except:
            print("error: ", r.text)
        return data

    def transform_news_data(self, data_source):
        result_list = []
        reserve_features = ['created_at', 'title', 'description']

        for context in data_source['list']:
            single_stock_news = {}
            for k in reserve_features[:-1]:
                single_stock_news[k] = context[k]

            # 最后一个特征description单独处理
            last_k = reserve_features[-1]
            detailed_news_url = get_detailed_news_url(context[last_k])  # 获取详情数据的url
            news_details_info = self.get_news_details(detailed_news_url)  # 得到详细新闻资讯

            if not news_details_info:  # 若为空，直接保存原资讯简明信息
                pattern = re.compile(r'<a.*?>.*?</a>')
                single_stock_news[last_k] = pattern.sub('', context[last_k])  # 移除超链接标签和其中的文本内容
            else:
                single_stock_news[last_k] = ' '.join(list(news_details_info))  # 拼接set里面的数据之后存入

            result_list.append(single_stock_news)

        return result_list


if __name__ == "__main__":
    symbol = 'SH600667'  # 'SH688535'
    crawl_page_num = 2

    ns = NewsSpider(symbol)
    # news_info = []

    # for p in range(1, crawl_page_num + 1):
    #     c = ns.get_single_stock_news_info(page=p)
    #     news_info.extend(ns.transform_news_data(c))
    #
    # df = pd.DataFrame(news_info)
    # print(df.head())

    c = ns.get_single_stock_news_info(page=1)
    latest_news = c['list'][0]['title']  # 获取最新的新闻
    print(latest_news)

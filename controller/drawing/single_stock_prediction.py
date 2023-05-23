# -*- coding: utf-8 -*-
# @Time : 2023/4/11 15:56
# @Author : JIQ
# @Email : jiq1314an@qq.com
import os
from collections import Counter
from datetime import datetime, timedelta

import jieba
import numpy as np
import pandas as pd
from PIL import Image
from pyecharts import options as opts
from pyecharts.charts import Line, Kline, Grid, WordCloud
from pyecharts.commons.utils import JsCode
from pyecharts.options import VisualMapOpts

from controller.drawing.utils import Tech
from controller.fetch_data import get_single_stock_info
from controller.spider.all_stock_spider import all_stock_crawl
from controller.spider.single_stock_news_spider import NewsSpider
from model.evaluate import eval_
from model.parser_conf import args
from model.utils import setup_seed


class PredVisualization:
    def __init__(self, name, symbol):
        self.name = name
        self.symbol = symbol
        self.stock_data = get_single_stock_info(symbol)
        self.x_data = sorted(self.stock_data.index.astype("str").to_list())
        # args.corpusFile = self.stock_data  # 及时修改源数据
        # print(args.corpusFile)
        self.true_data, self.pred_data, self.mse, self.r2, self.loss = eval_(symbol)

    def origin_close_line_show(self):
        flag = 0
        start_date = None
        end_date = None
        sh = self.stock_data.copy()
        macd, diff, dea = Tech(sh).macd()
        # print(macd > 0)
        # 判断牛市熊市
        sh['bull'] = macd > 0
        bar_data = []

        for date, is_bull in zip(self.x_data, sh.bull):
            if is_bull and flag == 0:
                start_date = date
                flag = 1
            elif is_bull:
                end_date = date
            else:
                if start_date == None or end_date == None: continue
                # print(start_date, end_date)
                bar_data.append(opts.MarkAreaItem(name="牛市", x=(start_date, end_date)))
                flag = 0
                start_date = None
                end_date = None

        if start_date != None and end_date != None:
            bar_data.append(opts.MarkAreaItem(name="牛市", x=(start_date, end_date)))
        # 不同点位设置不同颜色
        des = sh.close.describe()
        v1, v2, v3 = np.ceil(des['25%']), np.ceil(des['50%']), np.ceil(des['75%'])
        pieces = [{"min": v3, "color": "red"},
                  {"min": v2, "max": v3, "color": "blue"},
                  {"min": v1, "max": v2, "color": "black"},
                  {"max": v1, "color": "green"}, ]
        # 链式调用作用域()
        g = (
            Line(init_opts=opts.InitOpts(height="300px", ))  # 设置画布大小，px像素
                .add_xaxis(self.x_data)  # x数据

                .add_yaxis(
                series_name="",  # 序列名称
                y_axis=sh.close.values.tolist(),  # 添加y数据
                is_smooth=True,  # 平滑曲线
                is_symbol_show=False,  # 不显示折线的小圆圈
                label_opts=opts.LabelOpts(is_show=False),
                linestyle_opts=opts.LineStyleOpts(width=3),  # 线宽
                markpoint_opts=opts.MarkPointOpts(data=[  # 添加标记符
                    opts.MarkPointItem(type_='max', name='最大值'),
                    opts.MarkPointItem(type_='min', name='最小值'), ], symbol_size=[100, 30]),
                markline_opts=opts.MarkLineOpts(  # 添加均值辅助性
                    data=[opts.MarkLineItem(type_="average")], ))

                .set_global_opts(  # 全局参数设置
                title_opts=opts.TitleOpts(title='上证指数走势', subtitle='2022年-2023年', pos_left='left', pos_top="500px"),
                tooltip_opts=opts.TooltipOpts(trigger="axis", axis_pointer_type="cross"),
                toolbox_opts=opts.ToolboxOpts(is_show=True),
                # isualmap_opts=opts.VisualMapOpts(  # 视觉映射配置
                #     orient="horizontal", split_number=4,
                #     pos_left='center', is_piecewise=True,
                #     pieces=pieces, pos_top="440px"),
                yaxis_opts=opts.AxisOpts(min_=int(des['min']) - 2),

                datazoom_opts=[  # 设置zoom参数后即可缩放
                    opts.DataZoomOpts(
                        is_show=True,
                        type_="inside",
                        xaxis_index=[0],
                        range_start=0,
                        range_end=300,
                    ),
                    opts.DataZoomOpts(
                        is_show=True,
                        type_="slider",
                        pos_top="0",
                        xaxis_index=[0],
                        range_start=0,
                        range_end=300,
                    ),
                ],

            )
                .set_series_opts(
                markarea_opts=opts.MarkAreaOpts(  # 标记区域配置项
                    data=bar_data, ))

        )
        return g, pieces

    def real_pred_close_line_fitting(self):
        s = args.sequence_length
        # t = self.stock_data.index[0] # 起始日期
        line = Line()
        # line.add_xaxis([(t + timedelta(days=s * (i + 1))).date() for i in range(len(self.pred_data))])
        line.add_xaxis(self.x_data[-len(self.true_data):])
        line.add_yaxis("true close", self.true_data, is_smooth=True, linestyle_opts=opts.LineStyleOpts(width=4))
        line.add_yaxis("pred close", self.pred_data, is_smooth=True, linestyle_opts=opts.LineStyleOpts(width=4))

        line.set_series_opts(
            label_opts=opts.LabelOpts(is_show=False),
            markpoint_opts=opts.MarkPointOpts(
                data=[opts.MarkPointItem(type_="max", name="最大值"), opts.MarkPointItem(type_="min", name="最小值")]
            ),
            markline_opts=opts.MarkLineOpts(
                data=[opts.MarkLineItem(type_="average", name="平均值")]
            ),
        )

        line.set_global_opts(
            title_opts=opts.TitleOpts(title=f"{self.name} 真实值与预测值折线图", pos_top="0"),
            xaxis_opts=opts.AxisOpts(type_="category"),
            yaxis_opts=opts.AxisOpts(
                type_="value",
                axistick_opts=opts.AxisTickOpts(is_show=True),
                splitline_opts=opts.SplitLineOpts(is_show=True),
                min_=int(min(self.true_data + self.pred_data)) - 1,
                max_=int(max(self.true_data + self.pred_data)) + 1,
            ),
            tooltip_opts=opts.TooltipOpts(trigger="axis"),
            legend_opts=opts.LegendOpts(is_show=True, pos_top="15px"),
            graphic_opts=[
                opts.GraphicGroup(
                    graphic_item=opts.GraphicItem(
                        # 控制整体的位置
                        right="8%",
                        top="1%",
                    ),
                    children=[
                        # opts.GraphicText控制文字的显示
                        opts.GraphicText(
                            graphic_item=opts.GraphicItem(
                                left="center",
                                top="middle",
                                z=100,
                            ),
                            graphic_textstyle_opts=opts.GraphicTextStyleOpts(
                                # 可以通过jsCode添加js代码，也可以直接用字符串
                                text=f"R2: {round(self.r2, 2)}\nMSE: {round(self.mse, 4)}",
                                font="14px Microsoft YaHei",
                                graphic_basicstyle_opts=opts.GraphicBasicStyleOpts(
                                    fill="#333"
                                )
                            )
                        )
                    ]
                )
            ],

        )
        return line


def wordcloud_chart(name, symbol, latest_nums=10, html_save_path="../../view/templates/"):
    """默认获取最近10的新闻数据进行词云图展示
    :param name:
    :param symbol:
    :param latest_nums:
    :return:
    """
    # 1、获取数据
    ns = NewsSpider(symbol)
    news_info = []
    c = ns.get_single_stock_news_info(page=1)
    news_info.extend(ns.transform_news_data(c))
    df = pd.DataFrame(news_info).loc[:latest_nums, 'description']
    detailed_news = "".join(list(df))
    # print(detailed_news)

    # 2、读取停用词表
    cur_file_dir = os.path.dirname(__file__)  # drawing
    with open(os.path.join(cur_file_dir, "../../model/stopwords/中文停用词表.txt"), encoding="utf-8") as f:
        stop_words = f.readlines()
    stop_words = [i.replace('\n', '') for i in stop_words]
    # 3、定义词云图
    img_path = os.path.join(cur_file_dir, "../../view/static/img/mask_pic.png")  # 打开遮罩图片
    wordcloud = WordCloud()

    # 3、数据处理
    # 对新闻内容进行分词
    words_list = jieba.lcut(detailed_news)
    # 过滤停用词
    words_list = [word for word in words_list if word not in stop_words]
    # 计算每个词的出现次数
    word_counts = Counter(words_list)
    # 构建词云图所需的数据格式
    # wordcloud_data = [{"name": k, "value": v} for k, v in word_counts.items()]
    wordcloud_data = [(k, v) for k, v in word_counts.items()]

    # 4、绘图
    # 添加词云图数据
    wordcloud.add(series_name=symbol, data_pair=wordcloud_data, mask_image=img_path)
    # 设置词云图全局参数
    wordcloud.set_global_opts(title_opts=opts.TitleOpts(title=f"{name} 股票新闻对应词云图"),
                              legend_opts=opts.LegendOpts(pos_bottom="0", pos_left="20%"),
                              )

    # 渲染词云图并保存到文件
    wordcloud.render(os.path.join(cur_file_dir, html_save_path + "selected_stock_news_wordcloud.html"))

    return wordcloud


def prediction_graph_combination(name, symbol):
    setup_seed(args)  # 设定随机数
    # 1. 获取可视化对象
    pv = PredVisualization(name, symbol)

    # 2. 获取真实值与预测值拟合曲线图
    fit = pv.real_pred_close_line_fitting()

    # 3. 获取牛市区域的原收盘价可视化图
    show, pieces = pv.origin_close_line_show()

    # 4. 组合 将两个 Grid 组合起来
    grid_chart = Grid(init_opts=opts.InitOpts(width='1260px', height="1400px"))
    grid_chart.add(fit, grid_opts=opts.GridOpts(pos_left="15%", pos_right="8%", pos_top='50px', height='400px'))
    grid_chart.add(show, grid_opts=opts.GridOpts(pos_left="15%", pos_right="8%", pos_top='550px', height='400px'))
    wordcloud_chart(name, symbol)  # flush wordcloud graph
    return grid_chart


if __name__ == "__main__":
    name = "人民网"
    symbol = "SH603000"
    g = prediction_graph_combination(name, symbol)
    # g.render("stock_prediction.html")
    wordcloud_chart(name, symbol)

# -*- coding: utf-8 -*-
# @Time : 2023/4/19 22:06
# @Author : JIQ
# @Email : jiq1314an@qq.com
import os.path
import warnings

import numpy as np
import pandas as pd
from pyecharts.commons.utils import JsCode
from pyecharts.globals import ThemeType

from controller.fetch_data import get_single_stock_info
from controller.spider.all_stock_spider import all_stock_crawl
from controller.spider.single_stock_news_spider import NewsSpider
from controller.spider.utils import get_detailed_news_url
from pyecharts.charts import Pie, Bar, Scatter, WordCloud, Grid
from pyecharts import options as opts

warnings.filterwarnings("ignore")


class DataShow:
    """
    单独生成两个HTML界面，之后用iframe去拼接获取
    """
    cur_file_dir = os.path.dirname(__file__)

    def __init__(self, all_stock_info, stack_chart_data,
                 html_save_path=os.path.join(cur_file_dir, "../../view/templates/")):
        self.all_stock_info = all_stock_info  # 包括最后一列添加的最新的股票新闻信息
        self.stack_chart_data = stack_chart_data
        self.html_save_path = html_save_path

    def table_show(self):
        html = '''
        <!DOCTYPE html>
        <html>
        <head>
          <meta charset="GB18030">
          <title>Table Title</title>
        </head>
        <body>
        {table}
        </body>
        </html>
        '''
        table_html = self.all_stock_info.to_html(index=False, escape=False)
        table_html = table_html.replace('<th>', '<th style="text-align: center;">')  # 将表格的列名居中
        final_html = html.format(table=table_html)
        # write html to file
        # text_file = open(self.html_save_path + "all_stock_info_chart.html", "w")
        # text_file.write(final_html)
        # text_file.close()

    def graph_combine_show(self):
        sc = self.scatter_chart()
        pi = self.pie_chart()
        bh = self.barh_chart()
        st = self.stack_chart()
        sc.render(self.html_save_path + "scatter.html")
        pi.render(self.html_save_path + "pie.html")
        bh.render(self.html_save_path + "barh.html")
        st.render(self.html_save_path + "stack.html")

    def scatter_chart(self):
        names = list(self.all_stock_info['股票名称'])
        # pe_ratios = list(self.all_stock_info['市盈率(TTM)'])
        pe_ratios = [round(ttm, 3) for ttm in self.all_stock_info['市盈率(TTM)']]
        # 绘制散点图
        scatter = (
            Scatter()
                .add_xaxis(names)
                .add_yaxis("市盈率", pe_ratios, )  # label_opts=opts.LabelOpts(formatter="{c}")
                .set_global_opts(
                xaxis_opts=opts.AxisOpts(name_rotate=60, axislabel_opts={"rotate": 45}),
                title_opts=opts.TitleOpts(title="不同股票市盈率"),
                # tooltip_opts=opts.TooltipOpts(formatter="{b}:<br/>{a} {c}"),
                tooltip_opts=opts.TooltipOpts(formatter="{a}: {c}"),
                visualmap_opts=opts.VisualMapOpts(
                    type_="size",
                    max_=150,
                    min_=0,
                    orient="horizontal",
                    is_piecewise=True,
                    pos_bottom="0",
                    pos_left="35%",
                    pieces=[{"max": 0, "min": -1e5, "label": "< 0", "color": "orange"},
                        {"max": 50, "min": 0, "label": "0-50", "color": "green"},
                            {"max": 200, "min": 50, "label": "50-200", "color": "skyblue"},
                            {"max": 1000, "min": 1e5, "label": "> 200", "color": "red"}]
                ),

            )
        )
        # scatter.render("scatter.html")
        return scatter

    def pie_chart(self):
        # 配置图表
        pie = (
            Pie(init_opts=opts.InitOpts(theme=ThemeType.MACARONS))  # Dark不错  MACARON也不错
                .add("", self.all_stock_info[['股票名称', '成交量']].values)
                .set_global_opts(
                title_opts=opts.TitleOpts(title="不同股票成交量占比"),
                legend_opts=opts.LegendOpts(
                    orient="horizontal", pos_bottom="0", pos_left="2%"
                ),
            )
                .set_series_opts(label_opts=opts.LabelOpts(formatter="{b}: {c} ({d}%)"),
                                 )
        )

        # 渲染图表到HTML文件
        # pie.render("C:\\Users\\86131\\Desktop\\pie.html")
        return pie

    def barh_chart(self):
        # 绘制条形图
        barh = (
            Bar()
                .add_xaxis(list(self.all_stock_info['股票名称']))
                .add_yaxis("涨跌幅", list(self.all_stock_info['涨跌幅']), label_opts=opts.LabelOpts(formatter="{c}%"))
                .add_yaxis("涨跌额", list(self.all_stock_info['涨跌额']), label_opts=opts.LabelOpts(formatter="{c}"))
                .reversal_axis()
                .set_global_opts(
                title_opts=opts.TitleOpts(title="不同股票涨跌幅与涨跌额"),
                yaxis_opts=opts.AxisOpts(axislabel_opts=opts.LabelOpts(rotate=0))
            )
        )
        # barh.render("barh.html")
        return barh

    def stack_chart(self):
        y_len = 5
        time_legend = []

        max_page = 1
        show_size = 10
        data_source = all_stock_crawl(max_page).iloc[:show_size, :]
        for s in data_source.index:  # symbol
            single_stock_info = get_single_stock_info(s)
            time_legend = list(single_stock_info['turnover_rate'][-y_len:].index.astype("str"))
            if len(time_legend) == y_len: break
        # 将数据整理成 Pyecharts 可以识别的格式
        # x_data = ["day1", "day2", "day3", "day4", "day5"]
        temp_stock_data = pd.DataFrame.from_dict(self.stack_chart_data, orient='index')
        # print(temp_stock_data.index)
        # print(temp_stock_data.values) # 值不存在的为nan
        x_sname = list(temp_stock_data.index)
        values = [[i[j] for i in temp_stock_data.values] for j in range(y_len)]  # 按列取值
        y_data = [{"series_name": date, "y_axis": value} for date, value in zip(time_legend, values)]

        # 创建堆叠柱状图并设置属性
        bar_chart = Bar(init_opts=opts.InitOpts(theme=ThemeType.WESTEROS))  # WESTEROS
        bar_chart.set_global_opts(
            xaxis_opts=opts.AxisOpts(axislabel_opts=opts.LabelOpts(rotate=30)),
            yaxis_opts=opts.AxisOpts(name="换手率"),
            title_opts=opts.TitleOpts(title="不同股票的换手率"),
            # legend_opts=opts.LegendOpts(pos_bottom="0", pos_left="5%"),

        )

        # 将数据添加到堆叠柱状图中并绘制
        bar_chart.add_xaxis(x_sname)
        for item in y_data:
            bar_chart.add_yaxis(**item, stack="stack1")
        # bar_chart.render("C:\\Users\\86131\\Desktop\\stack.html")
        return bar_chart


def get_all_stock_info():
    max_page = 1
    show_size = 10
    save_root_path = os.path.join(os.path.dirname(__file__), "temp_save_data")
    data_source_fname = os.path.join(save_root_path, "data_source.csv")
    stack_chart_data_fname = os.path.join(save_root_path, "stack_chart_data.npy")

    if os.path.exists(data_source_fname) and os.path.exists(stack_chart_data_fname):
        data_source = pd.read_csv(data_source_fname)
        stack_chart_data = np.load(stack_chart_data_fname, allow_pickle=True).item()
        # test
        # stack_chart_data = {'N长青科技': [6.97, 5.24, 10.78, 13.21, 16.41],
        #                     '众智科技': [5.97, 5.24, 3.78, 3.21, 16.41],
        #                     '友讯达': [3.7, 5.24, 9.78, 2.21, 8.41],
        #                     '丰立智能': [4.56, 3.96, 17.93, 15.67, 38.48],
        #                     '飞力达': [3.78, 3.21, 3.41],
        #                     '迦南智能': [5.97, 5.24, 3.78, 3.21, 10.41],
        #                     '吉贝尔': [25.97, 25.24, 23.78, 23.21, 16.41],
        #                     '贝仕达克': [15.97, 15.24, 13.78, 13.21, 16.41],
        #                     '未来电器': [35.97, 33.78],
        #                     '煜邦电力': [13.78, 23.21, 26.41]}

        return data_source, stack_chart_data
    else:
        data_source = all_stock_crawl(max_page).iloc[:show_size, :]
        # print(data_source)

        stack_chart_data = {}
        show_size = 5
        all_stock_latest_news = []
        for n, s in zip(data_source['股票名称'], data_source.index):  # symbol
            single_stock_info = get_single_stock_info(s)
            stack_chart_data[n] = list(single_stock_info['turnover_rate'][-show_size:])  # 从后面取

            ns = NewsSpider(s)
            c = ns.get_single_stock_news_info(page=1)
            title = c['list'][0]['title']
            href = get_detailed_news_url(c['list'][0]['description'])  # 获取详情数据的url
            all_stock_latest_news.append(
                f'<a href={href}" style="text-decoration:none target="_blank"">{title}</a>')  # 获取最新的新闻

        data_source['最新新闻标题'] = all_stock_latest_news
        data_source.reset_index(drop=True, inplace=True)
        # 数据处理下，缺失值填充 —— 均值
        data_source.fillna(data_source.mean(), inplace=True)

        # 保存数据
        data_source.to_csv(data_source_fname, index=False)
        np.save(stack_chart_data_fname, stack_chart_data)  # 注意带上后缀名
        return data_source, stack_chart_data


if __name__ == "__main__":
    combined_data, stack_chart_data = get_all_stock_info()
    # print(combined_data)
    ds = DataShow(combined_data, stack_chart_data)
    # ds.table_show()
    # ds.graph_combine_show()
    ds.stack_chart()
    ds.pie_chart()

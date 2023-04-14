# -*- coding: utf-8 -*-
# @Time : 2023/4/7 21:56
# @Author : JIQ
# @Email : jiq1314an@qq.com
import numpy as np

np.seterr(divide='ignore', invalid='ignore')  # 忽略warning
from pyecharts.charts import Page, Kline, Bar, Grid, Line
from pyecharts import options as opts
import webbrowser as wb

from controller.drawing.utils import ma_line_add_yaxis, Tech


class AnalysisVisualization:
    """
    绘制单只股票可视化
    包括K均线、成交量、MACD、KDJ
    """

    def __init__(self, data, name, ticker):
        self.stock_name = name
        self.stock_code = ticker

        # other configuration
        extracted_features = ['open', 'close', 'low', 'high', 'volume', 'turnover_rate']  # 更新需要修改
        self.stock_data_extracted = data[extracted_features]

        self.range_start = 0
        self.range_end = 100
        self.xaxis_index = [0, 1, 2, 3]  # 设置第0轴和第1、2、3轴同时缩放，多轴联动
        # self.x_timestamp = [i.date() for i in self.stock_data_extracted.index]  # 横轴x序列
        self.x_timestamp = self.stock_data_extracted.index.astype("str").to_list()  # 横轴x序列

        self.macd_bar, self.macd_dif, self.macd_dea, = self.get_macd_index()

    def get_macd_index(self):
        fastperiod, slowperiod, signalperiod = 12, 26, 9
        macd_bar, macd_dif, macd_dea, = Tech(self.stock_data_extracted).macd(fastperiod, slowperiod, signalperiod)
        return macd_bar, macd_dif, macd_dea,

    def k_line_drawing(self):
        k_line = (
            Kline()
                .add_xaxis(self.x_timestamp)
                .add_yaxis("K线图", self.stock_data_extracted.iloc[:, :4].values.tolist())
                .set_global_opts(
                xaxis_opts=opts.AxisOpts(is_scale=True, is_show=False),
                # axis_opts=opts.AxisOpts(is_scale=True,min_=0), #y轴起始坐标可以设为0
                yaxis_opts=opts.AxisOpts(is_scale=True),  # y轴起始坐标可自动调整
                title_opts=opts.TitleOpts(title="价格", subtitle=self.stock_name + "\n" + self.stock_code,
                                          pos_top="150px"),
                axispointer_opts=opts.AxisPointerOpts(
                    is_show=True,
                    link=[{"xAxisIndex": "all"}],
                    label=opts.LabelOpts(background_color="#777"),
                ),
                datazoom_opts=[  # 设置zoom参数后即可缩放
                    opts.DataZoomOpts(
                        is_show=True,
                        type_="inside",
                        xaxis_index=self.xaxis_index,
                        range_start=self.range_start,
                        range_end=self.range_end,
                    ),
                    opts.DataZoomOpts(
                        is_show=True,
                        xaxis_index=self.xaxis_index,
                        type_="slider",
                        pos_top="90%",
                        range_start=self.range_start,
                        range_end=self.range_end,
                    ),
                ],

            )
        )
        return k_line

    def ma_line_drawing(self):
        ma_line = Line()
        ma_line.add_xaxis(xaxis_data=self.x_timestamp)
        window_nums = [5, 10, 30, 60]
        snames = ["MA5", "MA10", "MA30", "MA60"]
        close_df = self.stock_data_extracted[["close", 'high', 'low']]

        for sn, wn in zip(snames, window_nums):
            ma_line = ma_line_add_yaxis(ma_line, close_df, sn, wn)

        ma_line.set_global_opts(xaxis_opts=opts.AxisOpts(type_="category"))
        return ma_line

    def volume_bar_drawing(self):
        color = ['green' if self.stock_data_extracted.open[x] > self.stock_data_extracted.close[x] else 'red'
                 for x in range(0, len(self.stock_data_extracted))]

        y = self.stock_data_extracted["turnover_rate"]
        volume = self.stock_data_extracted["volume"].tolist()

        data_pair = []
        for k, v, c, vol in zip(self.x_timestamp, y, color, volume):
            data_pair.append(
                opts.BarItem(
                    name=k,
                    value=v,
                    itemstyle_opts=opts.ItemStyleOpts(color=c),
                    label_opts=opts.LabelOpts(formatter=f'{int(round(vol / 10 ** 6, 0))}',
                                              position='top', color='black'),
                ))

        turnover_rate_bar = (Bar()
                             .add_xaxis(self.x_timestamp)
                             .add_yaxis('转手率（%）', data_pair, label_opts=opts.LabelOpts(is_show=False))
                             .set_global_opts(title_opts=opts.TitleOpts(title="成交量（百万）\n与转手率（%）", pos_top="390px"),
                                              legend_opts=opts.LegendOpts(is_show=False),
                                              )
                             )
        # 修改标签 formatter 显示另一种数据
        # .set_series_opts(
        #     label_opts=opts.LabelOpts(formatter=f'{volume}'),
        # 将两组数据传递给 formatter 函数  formatter='{b}\n{c1} {c2}'
        # c1 表示第一组数据（换手率），c2 表示第二组数据（另一种数据）
        # b 表示 x 轴的数据（股票名称）
        # \n 表示换行符
        # 根据需求自行调整格式
        # 参考链接：https://echarts.apache.org/zh/option.html#series-bar.label.formatter
        # )

        return turnover_rate_bar

    def macd_bar_drawing(self):
        bar_red = np.where(self.macd_bar > 0, self.macd_bar, 0)  # 绘制BAR>0 柱状图
        bar_green = np.where(self.macd_bar < 0, self.macd_bar, 0)  # 绘制BAR<0 柱状图
        # print(bar_green)
        # 绘制的y对应值必须为整数,未必，需要为list对象
        macd_Bar = (
            Bar()
                .add_xaxis(self.x_timestamp)
                .add_yaxis("RMACD", list(bar_red), label_opts=opts.LabelOpts(is_show=False),
                           itemstyle_opts=opts.ItemStyleOpts(color="red"))  # 注意y不能是array对象
                .add_yaxis("GMACD", list(bar_green), label_opts=opts.LabelOpts(is_show=False),
                           itemstyle_opts=opts.ItemStyleOpts(color="green"))
        )

        return macd_Bar

    def macd_line_drawing(self):
        macd_line = (
            Line()
                .add_xaxis(xaxis_data=self.x_timestamp)
                .add_yaxis(
                series_name="DIF",
                y_axis=self.macd_dif,
                is_smooth=True,
                is_hover_animation=False,
                linestyle_opts=opts.LineStyleOpts(width=3, opacity=0.5),
                label_opts=opts.LabelOpts(is_show=False),
                itemstyle_opts=opts.ItemStyleOpts(color="red")

            )
                .add_yaxis(
                series_name="DEA",
                y_axis=self.macd_dea,
                is_smooth=True,
                is_hover_animation=False,
                linestyle_opts=opts.LineStyleOpts(width=3, opacity=0.5),
                label_opts=opts.LabelOpts(is_show=False),
                itemstyle_opts=opts.ItemStyleOpts(color="green")
            )

                .set_global_opts(title_opts=opts.TitleOpts(title="MACD", pos_top="675px"),
                                 legend_opts=opts.LegendOpts(is_show=True, pos_left="190px",
                                                             pos_bottom="725px"),
                                 xaxis_opts=opts.AxisOpts(is_show=True),
                                 )
        )
        return macd_line

    def kdj_line_drawing(self):
        N, M1, M2 = 9, 3, 3
        k, d, j = Tech(self.stock_data_extracted).kdj(N, M1, M2)

        kdj_line = (
            Line()
                .add_xaxis(xaxis_data=self.x_timestamp)
                .add_yaxis(
                series_name="K",
                y_axis=k,
                is_smooth=True,
                is_hover_animation=False,
                linestyle_opts=opts.LineStyleOpts(width=3, opacity=0.5),
                label_opts=opts.LabelOpts(is_show=False),
                itemstyle_opts=opts.ItemStyleOpts(color="blue")

            )
                .add_yaxis(
                series_name="D",
                y_axis=d,
                is_smooth=True,
                is_hover_animation=False,
                linestyle_opts=opts.LineStyleOpts(width=3, opacity=0.5, type_='dashed'),
                label_opts=opts.LabelOpts(is_show=False),
                itemstyle_opts=opts.ItemStyleOpts(color="green")
            )

                .add_yaxis(
                series_name="J",
                y_axis=j,
                is_smooth=True,
                is_hover_animation=False,
                linestyle_opts=opts.LineStyleOpts(width=3, opacity=0.5),
                label_opts=opts.LabelOpts(is_show=False),
                itemstyle_opts=opts.ItemStyleOpts(color="red")
            )

                .set_global_opts(title_opts=opts.TitleOpts(title="KDJ", pos_top="950px"),
                                 legend_opts=opts.LegendOpts(is_show=True, pos_left="190px",
                                                             pos_bottom="425px"))
        )

        return kdj_line


def analysis_graph_combination(data, name, ticker):
    av = AnalysisVisualization(data, name, ticker)
    # 1.将K线图和移动平均线显示在一个图内
    k_line = av.k_line_drawing()
    ma_line = av.ma_line_drawing()
    k_line.overlap(ma_line)

    # 2.获取成交量柱状图
    volume_bar = av.volume_bar_drawing()

    # 3.将macd线图和macd柱状图显示在一个图内
    macd_line = av.macd_line_drawing()
    macd_Bar = av.macd_bar_drawing()
    macd_line.overlap(macd_Bar)

    # 4.获取KDJ折线图
    kdj_line = av.kdj_line_drawing()

    # 5.组合【使用网格将多张图标组合到一起显示】
    # height='1300px'
    grid_chart = Grid(init_opts=opts.InitOpts(width='1260px', height="100%"))

    grid_chart.add(
        k_line,
        grid_opts=opts.GridOpts(pos_left="15%", pos_right="8%", pos_top='50px', height='260px'),
    )

    grid_chart.add(
        volume_bar,
        grid_opts=opts.GridOpts(pos_left="15%", pos_right="8%", pos_top='350px', height='120px'),
    )

    grid_chart.add(
        macd_line,
        grid_opts=opts.GridOpts(pos_left="15%", pos_right="8%", pos_top='550px', height='250px'),
    )

    grid_chart.add(
        kdj_line,
        grid_opts=opts.GridOpts(pos_left="15%", pos_right="8%", pos_top='850px', height='200px'),
    )

    # save_path = "C:/Users/86131/Desktop/html/kline_test.html"
    # grid_chart.render(save_path)
    # wb.open(save_path)
    return grid_chart

# -*- coding: utf-8 -*-
# @Time : 2023/4/11 15:56
# @Author : JIQ
# @Email : jiq1314an@qq.com
import numpy as np
from pyecharts import options as opts
from pyecharts.charts import Line, Kline, Grid
from pyecharts.commons.utils import JsCode
from pyecharts.options import VisualMapOpts

from controller.drawing.utils import Tech
from controller.fetch_data import get_single_stock_info
from model.evaluate import eval_
from model.parser_conf import args


class PredVisualization:
    def __init__(self, name, symbol):
        self.name = name
        self.symbol = symbol
        self.stock_data = get_single_stock_info(symbol)
        self.x_data = self.stock_data.index.astype("str").to_list()
        args.corpusFile = self.stock_data  # 及时修改源数据
        self.true_data, self.pred_data, self.mse, self.r2 = eval_()

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
                title_opts=opts.TitleOpts(title='上证指数走势', subtitle='2022年-2023年', pos_left='left'),
                tooltip_opts=opts.TooltipOpts(trigger="axis", axis_pointer_type="cross"),
                toolbox_opts=opts.ToolboxOpts(is_show=True),
                visualmap_opts=opts.VisualMapOpts(  # 视觉映射配置
                    orient="horizontal", split_number=4,
                    pos_left='center', is_piecewise=True,
                    pieces=pieces, pos_top="440px"),
                yaxis_opts=opts.AxisOpts(min_=des['min'] - 2),

                datazoom_opts=[  # 设置zoom参数后即可缩放
                    opts.DataZoomOpts(
                        is_show=True,
                        type_="inside",
                        xaxis_index=0,
                        range_start=0,
                        range_end=300,
                    ),
                    opts.DataZoomOpts(
                        is_show=True,
                        type_="slider",
                        pos_top="0",
                        xaxis_index=0,
                        range_start=0,
                        range_end=300,
                    ),
                ],

            )
                .set_series_opts(
                markarea_opts=opts.MarkAreaOpts(  # 标记区域配置项
                    data=bar_data, ))

        )
        return g

    def real_pred_close_line_fitting(self):
        line = Line()
        line.add_xaxis(range(len(self.true_data)))
        line.add_yaxis("true close", self.true_data, is_smooth=True,linestyle_opts=opts.LineStyleOpts(width=4))
        line.add_yaxis("pred close", self.pred_data, is_smooth=True,linestyle_opts=opts.LineStyleOpts(width=4))

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
            title_opts=opts.TitleOpts(title="股票真实值与预测值折线图", pos_top="500px"),
            xaxis_opts=opts.AxisOpts(type_="category"),
            yaxis_opts=opts.AxisOpts(
                type_="value",
                axistick_opts=opts.AxisTickOpts(is_show=True),
                splitline_opts=opts.SplitLineOpts(is_show=True),
                min_=int(min(self.true_data + self.pred_data)) - 1,
                max_=int(max(self.true_data + self.pred_data)) + 1,
            ),
            tooltip_opts=opts.TooltipOpts(trigger="axis"),
            legend_opts=opts.LegendOpts(is_show=True, pos_top="500px"),
            graphic_opts=[
                opts.GraphicGroup(
                    graphic_item=opts.GraphicItem(
                        # 控制整体的位置
                        right="8%",
                        top="39%",
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
                                text=f"MSE: {round(self.mse, 4)}\nR2: {round(self.r2, 2)}",
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


def prediction_graph_combination(name, symbol):
    # 1. 获取可视化对象
    pv = PredVisualization(name, symbol)

    # 2. 获取牛市区域的原收盘价可视化图
    show = pv.origin_close_line_show()


    # 3. 获取真实值与预测值拟合曲线图
    fit = pv.real_pred_close_line_fitting()

    # 4.组合【使用网格将多张图标组合到一起显示】
    # height='1300px'
    grid_chart = Grid(init_opts=opts.InitOpts(width='1260px', height="1300px"), )

    grid_chart.add(
        fit,
        grid_opts=opts.GridOpts(pos_left="15%", pos_right="8%", pos_top='50px', height='350px'),

    )
    grid_chart.add(
        show,
        grid_opts=opts.GridOpts(pos_left="15%", pos_right="8%", pos_top='600px', height='300px'),
    )

    return grid_chart


if __name__ == "__main__":
    name = "人民网"
    symbol = "SH603000"
    g = prediction_graph_combination(name, symbol)
    g.render("stock_prediction.html")

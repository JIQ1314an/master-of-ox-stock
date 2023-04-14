from pyecharts.charts import Line
from pyecharts import options as opts
from random import randrange

x_data = ["2022-01-01", "2022-01-02", "2022-01-03", "2022-01-04", "2022-01-05", "2022-01-06"]
true_data = [randrange(2300, 2500) for _ in range(6)]
pred_data = [randrange(2300, 2500) for _ in range(6)]

line = Line()
line.add_xaxis(x_data)
line.add_yaxis("真实值", true_data, is_smooth=True, linestyle_opts=opts.LineStyleOpts(width=4))
line.add_yaxis("预测值", pred_data, is_smooth=True, linestyle_opts=opts.LineStyleOpts(width=4))

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
    title_opts=opts.TitleOpts(title="股票真实值与预测值折线图"),
    xaxis_opts=opts.AxisOpts(type_="category"),
    yaxis_opts=opts.AxisOpts(
        type_="value",
        axistick_opts=opts.AxisTickOpts(is_show=True),
        splitline_opts=opts.SplitLineOpts(is_show=True),
        min_=min(true_data + pred_data) - 1,
        max_=max(true_data + pred_data) + 1,
    ),
    tooltip_opts=opts.TooltipOpts(trigger="axis"),
    legend_opts=opts.LegendOpts(is_show=True),
)


line.render("stock_values.html")

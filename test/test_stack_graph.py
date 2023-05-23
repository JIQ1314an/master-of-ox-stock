from pyecharts import options as opts
from pyecharts.charts import Bar

# 假设有两只股票 A 和 B，每只股票有三个交易日的换手率数据
stock_data = {
    "A": [0.2, 0.3, 0.4],
    "B": [0.1, 0.2, 0.3],
}

# 将数据整理成 Pyecharts 可以识别的格式
x_data = ["day1", "day2", "day3"]
y_data = [{"series_name": k,  "y_axis": v} for k, v in stock_data.items()]

# 创建堆叠柱状图并设置属性
bar_chart = Bar()
bar_chart.set_global_opts(
    xaxis_opts=opts.AxisOpts(axislabel_opts=opts.LabelOpts(rotate=15)),
    yaxis_opts=opts.AxisOpts(name="换手率"),
    title_opts=opts.TitleOpts(title="不同股票的换手率"),
    legend_opts=opts.LegendOpts(),
)

# 将数据添加到堆叠柱状图中并绘制
bar_chart.add_xaxis(x_data)
for item in y_data:
    bar_chart.add_yaxis(**item, stack="stack1")
bar_chart.render("stock_turnover.html")

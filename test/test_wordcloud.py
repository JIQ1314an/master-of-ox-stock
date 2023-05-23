# # # -*- coding: utf-8 -*-
# # # @Time : 2023/4/20 2:01
# # # @Author : JIQ
# # # @Email : jiq1314an@qq.com
# #
# import jieba
# from collections import Counter
# from pyecharts import options as opts
# from pyecharts.charts import WordCloud, Grid
#
# # 停用词表
# from pyecharts.globals import SymbolType
#
# stop_words = ["的", "了", "是", "在", "和", "对于", "等", "有", "就", "不", "而", "及", "及其", "等等", "之", "与", "也"]
#
# # 模拟股票新闻数据
# stock_news_data = {
#     "AAPL": "苹果公司发布了新款iPhone，备受关注。",
#     "GOOG": "谷歌公司宣布与微软公司达成合作协议。",
#     "AMZN": "亚马逊公司推出了新的物流解决方案，获得了市场的认可。",
# }
# #
# # 定义词云图
# wordcloud = WordCloud()
# grid = Grid(init_opts=opts.InitOpts(width="100%", height="1300px"))
# # 处理每个股票的新闻
# for i, (stock_code, news_content) in enumerate(stock_news_data.items()):
#     # 对新闻内容进行分词
#     words_list = jieba.lcut(news_content)
#
#     # 过滤停用词
#     words_list = [word for word in words_list if word not in stop_words]
#
#     # 计算每个词的出现次数
#     word_counts = Counter(words_list)
#
#     # 构建词云图所需的数据格式
#     wordcloud_data = [{"name": k, "value": v} for k, v in word_counts.items()]
# #
# #     # 添加词云图数据
# #     wordcloud.add(series_name=stock_code, data_pair=wordcloud_data)
#
#     # 创建一个子图
#     wordcloud = (
#         WordCloud()
#             .add("", wordcloud_data, word_size_range=[30, 100],
#                  shape=SymbolType.DIAMOND)
#             .set_global_opts(title_opts=opts.TitleOpts(title=stock_code))
#     )
#     # 将子图添加到网格布局中
#     grid.add(wordcloud, grid_opts=opts.GridOpts(pos_top="{}%".format(15 * i)))
# #
# # # 设置词云图全局参数
# # wordcloud.set_global_opts(title_opts=opts.TitleOpts(title="不同股票新闻对应词云图"))
# #
# # # 渲染词云图并保存到文件
# # wordcloud.render("news_wordcloud.html")
#
# # 渲染图表并保存到文件
# grid.render("wordcloud_subplot.html")


from pyecharts import options as opts
from pyecharts.charts import WordCloud, Page

# 第一个股票新闻词云图
words1 =[("词语1", 10), ("词语2", 20), ("词语3", 30)]
wordcloud1 = (
    WordCloud()
    .add("", words1, word_size_range=[20, 100], shape="circle")
    .set_global_opts(title_opts=opts.TitleOpts(title="股票A新闻词云图"))
)

words2 = [("词语4", 15), ("词语5", 25), ("词语6", 35)]
# 第二个股票新闻词云图
wordcloud2 = (
    WordCloud()
    .add("", words2, word_size_range=[20, 100], shape="circle")
    .set_global_opts(title_opts=opts.TitleOpts(title="股票B新闻词云图"))
)

# 布局两个图表
page = Page(layout=Page.SimplePageLayout)
page.add(wordcloud1)
page.add(wordcloud2)
page.render("wordcloud.html")



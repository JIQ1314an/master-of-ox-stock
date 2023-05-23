import argparse
import os
import sys

import pandas as pd

from controller.drawing.all_stock_analysis import get_all_stock_info, DataShow
from model.parser_conf import unknown

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from flask import Flask, render_template, jsonify, request, send_file

from controller import fetch_data
from controller.drawing.single_stock_analysis import analysis_graph_combination
from controller.drawing.single_stock_prediction import prediction_graph_combination
from controller.fetch_data import get_single_stock_info

app = Flask(__name__)

html_save_dir = os.path.join(os.path.dirname(__file__), "templates")


@app.route("/")
def index():
    return render_template("index.html")


# ============================================================
# 用户交互后，页面不变动的可以使用render_template或者send_file，若是需要页面变化，则使用send_file
@app.route("/all_stock_info_chart")
def all_stock_info_chart():
    combined_data, stack_chart_data = get_all_stock_info()
    # print(combined_data)
    ds = DataShow(combined_data, stack_chart_data)

    # 将生成的HTML字符串作为参数传入render_template函数
    table_html = ds.all_stock_info.to_html(index=False, escape=False).replace('<th>',
                                                                              '<th style="text-align: center;">')
    ds.graph_combine_show()  # flush static html
    return render_template('all_stock_info_chart.html', table_html=table_html)


@app.route("/barh_graph")
def barh_graph():
    # return render_template("barh.html")
    return send_file('templates/barh.html')


@app.route("/pie_graph")
def pie_graph():
    # return render_template("pie.html")
    return send_file('templates/pie.html')


@app.route("/scatter_graph")
def scatter_graph():
    # return render_template("scatter.html")
    return send_file('templates/scatter.html')


@app.route("/stack_graph")
def stack_graph():
    # return render_template("stack.html")
    return send_file('templates/stack.html')


# ============================================================

@app.route("/single_stock_analysis")
def single_stock_analysis():
    return render_template("single_stock_analysis.html")
    # return send_file('templates/sstock_analysis_drawing.html')


# ============================================================
@app.route("/single_stock_prediction")
def single_stock_prediction():
    return render_template("single_stock_prediction.html")
    # return send_file('templates/sstock_prediction_drawing.html')


@app.route("/selected_stock_news_wordcloud")
def selected_stock_news_wordcloud():
    return send_file("templates/selected_stock_news_wordcloud.html")  # 加快显示


# ============================================================


@app.route('/get_stock_basic_info')
def get_stock_basic_info():
    # 在从中取前top10【主要是之前在插入时先插入的top10的股票，所以这里需要取后10个】
    top_n = -10
    lastest_basic_info = fetch_data.get_stock_basic_info()[top_n:]  # 最先的topn【由于之前先写入的所有这里要取最下面的10个】
    test_basic_info = fetch_data.get_test_stock_basic_info()

    symbols = [s for _, s in test_basic_info]
    symbols.extend([s for _, s in lastest_basic_info])
    names = [n for n, _ in test_basic_info]
    names.extend([n for n, _ in lastest_basic_info])
    # 反转一下
    return jsonify({"symbol": symbols[::-1], "name": names[::-1]})


@app.route("/get_sstock_analysis_drawing", methods=['GET', 'POST'])
def get_sstock_analysis_drawing():
    # 获取选择框的值
    if request.method == 'POST':
        value = request.form['value']
        # print(value)
        symbol, name = value.split(" ")
    else:
        # 默认值
        symbol = "SH603000"
        name = "人民网"
    # print(name)
    data = get_single_stock_info(symbol)
    ssa = analysis_graph_combination(data, name, symbol)
    # return ssa.dump_options_with_quotes()  # 动态
    html_fname = "sstock_analysis_drawing.html"
    ssa.render(os.path.join(html_save_dir, html_fname))
    return render_template(html_fname)
    # return send_file("templates/"+ html_fname)


@app.route("/get_sstock_prediction_drawing", methods=['GET', 'POST'])
def get_sstock_prediction_drawing():
    # print(symbol, name)
    # 获取选择框的值
    if request.method == 'POST':
        value = request.form['value']
        # print(value)
        symbol, name = value.split(" ")
    else:
        # 默认值
        symbol = "SH603000"
        name = "人民网"
    # print(name)

    ssp = prediction_graph_combination(name, symbol)
    # return ssp.dump_options_with_quotes()

    html_fname = "sstock_prediction_drawing.html"
    ssp.render(os.path.join(html_save_dir, html_fname))
    return render_template(html_fname)
    # return send_file("templates/"+html_fname)


@app.route("/update_sstock_analysis")
def update_sstock_analysis():
    # return render_template("sstock_analysis_drawing.html")
    # 加载本地 HTML 文件 使用 send_file ，若是使用render_template 本地html变动页面不会刷新
    return send_file("templates/sstock_analysis_drawing.html")


@app.route("/update_sstock_prediction")
def update_sstock_prediction():
    # return render_template("sstock_prediction_drawing.html")
    return send_file("templates/sstock_prediction_drawing.html")


# @app.route("/get_select_stock_to_analysis", methods=["POST"])
# def get_select_stock_to_analysis():
#     selected_option = request.form.get('selected_option')
#     # is_button_clicked = request.form.get('isButtonClicked')
#     # print(selected_option)
#     if selected_option != None:
#         symbol, name = selected_option.split(" ")
#         return get_sstock_analysis_drawing(symbol, name)
#     else:
#         return None


if __name__ == '__main__':
    app.run(debug=True, extra_files=unknown)
    # app.run(host="127.0.0.1", port=5000, debug=True)

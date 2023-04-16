import argparse
import os
import sys

from model.parser_conf import unknown

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from flask import Flask, render_template, jsonify

from controller import fetch_data
from controller.drawing.single_stock_analysis import analysis_graph_combination
from controller.drawing.single_stock_prediction import prediction_graph_combination
from controller.fetch_data import get_single_stock_info

app = Flask(__name__)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/single_stock_analysis")
def single_stock_visual():
    return render_template("single_stock_analysis.html")


@app.route("/single_stock_prediction")
def single_stock_prediction():
    return render_template("single_stock_prediction.html")


@app.route('/get_stock_basic_info')
def get_stock_basic_info():
    basic_info = fetch_data.get_stock_basic_info()
    symbols = [s for _, s in basic_info]
    names = [n for n, _ in basic_info]
    return jsonify({"symbol": symbols, "name": names})


@app.route("/get_sstock_analysis_drawing")
def get_sstock_analysis_drawing():
    name = "人民网"
    symbol = "SH603000"
    data = get_single_stock_info(symbol)
    ssa = analysis_graph_combination(data, name, symbol)
    return ssa.dump_options_with_quotes()


@app.route("/get_sstock_prediction_drawing")
def get_sstock_prediction_drawing():
    name = "人民网"
    symbol = "SH603000"
    ssp = prediction_graph_combination(name, symbol)
    return ssp.dump_options_with_quotes()


if __name__ == '__main__':
    app.run(debug=True, extra_files=unknown)
    # app.run(host="127.0.0.1", port=5000, debug=True)
import os

import matplotlib.pyplot as plt
import numpy as np

from controller.fetch_data import get_single_stock_info
from model import my_loss
from model.lstm_model import lstm
from model.dataset import getData
from model.parser_conf import args, parser
from sklearn import metrics

import torch

from model import train
from model.utils import setup_seed, split_dataset


def eval_(symbol, val=False):
    criterion = my_loss.HuberLoss(delta=0.1)
    # model = torch.load(args.save_file)
    model = lstm(input_size=args.input_size, hidden_size=args.hidden_size, num_layers=args.layers,
                 output_size=1, batch_first=args.batch_first, bidirectional=args.bidirectional)
    model.to(args.device)
    root_dir = os.path.dirname(os.path.abspath(__file__))
    args.save_file = 'save/{}-stock.pkl'.format(symbol)
    model_path = os.path.join(root_dir, args.save_file)
    if not os.path.exists(model_path):  train.train_and_val(symbol)  # 文件不存在时，先训练在评测
    checkpoint = torch.load(model_path)
    model.load_state_dict(checkpoint['state_dict'])

    args.corpusFile = get_single_stock_info(symbol)

    preds = []
    labels = []
    # print("eval_中的corpusFile", args.corpusFile)
    close_max, close_min, train_loader, test_loader = getData(args.corpusFile, args.sequence_length, args.batch_size)
    if test_loader is None: return None
    if val:
        data_loader = split_dataset(test_loader, 0.5)[0]  # 验证集
    else:
        data_loader = split_dataset(test_loader, 0.5)[1]  # 测试集
    total_loss = 0
    for idx, (x, label) in enumerate(data_loader):
        if args.useGPU:
            x = x.squeeze(1).cuda()  # batch_size,seq_len,input_size
        else:
            x = x.squeeze(1)
        pred = model(x)
        list = pred.data.squeeze(1).tolist()
        if len(np.array(list).shape) == 3:
            preds.extend(list[-1])
        else:
            preds.extend(list)
        labels.extend(label.tolist())

        loss = criterion(pred, label)
        total_loss += loss.item()

    real_list, pred_list = [], []
    standard_p_list = []
    for i in range(len(preds)):
        p = [preds[i] if (type(preds[i]) is float) else preds[i][0]]
        standard_p_list.append(p[0])

        real_price_test = labels[i] * (close_max - close_min) + close_min
        pred_price_test = p[0] * (close_max - close_min) + close_min

        # print('预测值是%.2f,真实值是%.2f' % (pred_price_test, real_price_test))
        real_list.append(round(real_price_test, 2))
        pred_list.append(round(pred_price_test, 2))

    mse, r2 = measure(real_list, pred_list)
    # mse, r2 = measure(labels, standard_p_list)
    # drawing(labels, standard_p_list)

    return real_list, pred_list, mse, r2, total_loss


def measure(real_price, pred_price):
    mse = metrics.mean_squared_error(real_price, pred_price)
    r2 = metrics.r2_score(real_price, pred_price)
    # print("MSE:", mse)
    # print("R2:", r2)
    return mse, r2


def drawing(real_price, pred_price):
    plt.figure(figsize=(8, 5))
    plt.plot(real_price, label='real price')
    plt.plot(pred_price, label='pred price')
    plt.title('close price')
    plt.xlabel('date')
    plt.ylabel('price')
    plt.legend()
    plt.show()


if __name__ == "__main__":
    setup_seed(args)
    # 中科信息 三六五网 顺网科技 招标股份 拉卡拉 掌趣科技 万兴科技 新国都 联特科技 华谊兄弟
    symbols = ["SZ300678", "SZ300295", "SZ300113", "SZ301136", "SZ300773",
               "SZ300315", "SZ300624", "SZ300130", "SZ301205", "SZ300027"]
    # args.corpusFile = get_single_stock_info(symbol)
    # args.corpusFile = "data/SZ300033.csv"

    # SZ300773  单独评估
    real_list, pred_list, mse, r2, loss = eval_(symbols[2])
    print("r2", r2)
    print("mse", mse)
    print("loss", loss)

    # for i in range(0, len(symbols)):
    #     real_list, pred_list, mse, r2 = eval_(symbols[i])
    #     print("============={}============".format(symbols[i]))
    #     print("r2", r2)
    #     print("mse", mse)
    #     print("loss", total_loss)

import os

import matplotlib.pyplot as plt
import numpy as np

from model.LSTMModel import lstm
from model.dataset import getData
from model.parser_conf import args
from sklearn import metrics

import torch


def eval_():
    # model = torch.load(args.save_file)
    model = lstm(input_size=args.input_size, hidden_size=args.hidden_size, num_layers=args.layers,
                 output_size=1, batch_first=args.batch_first, bidirectional=args.bidirectional)
    model.to(args.device)
    root_dir = os.path.dirname(os.path.abspath(__file__))  # 不会因为函数的调用而改变路径
    checkpoint = torch.load(os.path.join(root_dir, args.save_file))
    model.load_state_dict(checkpoint['state_dict'])

    preds = []
    labels = []
    close_max, close_min, train_loader, test_loader = getData(args.corpusFile, args.sequence_length, args.batch_size)
    for idx, (x, label) in enumerate(test_loader):
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

    real_list, pred_list = [], []
    for i in range(len(preds)):
        p = [preds[i] if (type(preds[i]) is float) else preds[i][0]]

        real_price_test = labels[i] * (close_max - close_min) + close_min
        pred_price_test = p[0] * (close_max - close_min) + close_min

        # print('预测值是%.2f,真实值是%.2f' % (pred_price_test, real_price_test))
        real_list.append(round(real_price_test, 2))
        pred_list.append(round(pred_price_test, 2))

    mse, r2 = measure(real_list, pred_list)
    # drawing(real_list, pred_list)

    return real_list, pred_list, mse, r2


def measure(real_price, pred_price):
    mse = metrics.mean_squared_error(real_price, pred_price)
    r2 = metrics.r2_score(real_price, pred_price)
    print("RMSE:", mse)
    print("R2:", r2)
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
    eval_()

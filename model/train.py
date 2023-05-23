import os

import numpy as np
from sklearn import metrics
from torch.autograd import Variable
import torch.nn as nn
import torch
from torch.utils.tensorboard import SummaryWriter

from model import my_loss
from model.lstm_model import lstm
from controller.fetch_data import get_single_stock_info
from model import evaluate

from model.utils import setup_seed, split_dataset
from model.parser_conf import args, parser
from model.dataset import getData


def train_and_val(symbol):
    loss_writer = SummaryWriter(log_dir=args.loss_writer, flush_secs=120)
    r2_writer = SummaryWriter(log_dir=args.r2_writer, flush_secs=120)
    mse_writer = SummaryWriter(log_dir=args.mse_writer, flush_secs=120)

    args.corpusFile = get_single_stock_info(symbol)
    # print(args.corpusFile)

    model = lstm(input_size=args.input_size, hidden_size=args.hidden_size, num_layers=args.layers, output_size=1,
                 dropout=args.dropout, batch_first=args.batch_first, bidirectional=args.bidirectional)
    model.to(args.device)
    # criterion = nn.MSELoss()  # 定义损失函数
    # criterion = my_loss.MSLELoss()  # 均方对数误差
    criterion = my_loss.HuberLoss(delta=0.1)  # 平滑L1损失函数
    optimizer = torch.optim.Adam(model.parameters(), lr=args.lr)  # Adam梯度下降  学习率=0.001
    # optimizer = torch.optim.SGD(model.parameters(),lr = args.lr,momentum = 0.9)  # SGD梯度下降 初始学习率=0.1
    # print("train 中的corpusFile", args.corpusFile)
    close_max, close_min, train_loader, test_loader = getData(args.corpusFile, args.sequence_length, args.batch_size)
    if train_loader is None: return None
    better_loss = args.better_loss
    root_dir = os.path.dirname(os.path.abspath(__file__))
    args.save_file = 'save/{}-stock.pkl'.format(symbol)
    save_model_file = os.path.join(root_dir, args.save_file)

    for i in range(1, args.epochs + 1):
        train_total_loss = 0
        val_total_loss = 0
        adjust_learning_rate(optimizer, i)
        for idx, (data, label) in enumerate(train_loader):
            if args.useGPU:
                data1 = data.squeeze(1).cuda()
                pred = model(Variable(data1).cuda())
                # print(pred.shape)
                pred = pred[1, :, :]
                # print(pred)
                label = label.unsqueeze(1).cuda()
                # print(label.shape)
            else:
                data1 = data.squeeze(1)
                pred = model(Variable(data1))
                try:
                    pred = pred[1, :, :]
                except:
                    pass
                label = label.unsqueeze(1)
            loss = criterion(pred, label)
            optimizer.zero_grad()
            loss.backward()
            optimizer.step()
            train_total_loss += loss.item()
        # print(total_loss)

        if i % 10 == 0 and val_total_loss < better_loss:
            _, _, val_mse, val_r2, val_total_loss = evaluate.eval_(symbol, val=True)
            better_loss = val_total_loss
            # torch.save(model, args.save_file)

            loss_writer.add_scalars("Loss", {"train": train_total_loss, "val": val_total_loss}, i)
            r2_writer.add_scalar("R2", val_r2, i)
            mse_writer.add_scalar("MSE", val_mse, i)

            torch.save({'state_dict': model.state_dict()}, save_model_file)
            print('第%d epoch，当前train loss %.5f，val loss为 %.5f，保存模型' % (i, train_total_loss, better_loss))

    loss_writer.close()
    r2_writer.close()
    r2_writer.close()

    # torch.save(model, args.save_file)
    # torch.save({'state_dict': model.state_dict()}, save_model_file)


def adjust_learning_rate(optimizer, epoch):
    """Sets the learning rate to the initial LR decayed by 10 every 100 epochs"""
    lr = args.lr * (0.1 ** (epoch // 300))
    for param_group in optimizer.param_groups:
        param_group['lr'] = lr


if __name__ == "__main__":
    setup_seed(args)
    # 中科信息 三六五网 顺网科技 招标股份 拉卡拉 掌趣科技 万兴科技 新国都 联特科技 华谊兄弟
    symbols = ["SZ300678", "SZ300295", "SZ300113", "SZ301136", "SZ300773",
               "SZ300315", "SZ300624", "SZ300130", "SZ301205", "SZ300027"]
    # args.corpusFile = get_single_stock_info(symbol)
    # 单独训练  SZ300773
    # train_and_val(symbols[4])
    train_and_val(symbols[2])

    # 5月21
    # symbols = ["SH688361", "SZ301428", "SZ300686", "SZ301360", "SH688048",
    #            "SH688314", "SH688416", "SZ301368", "SZ300458", "SZ300042"]
    #
    # for i in range(0, len(symbols)):
    #     print("============={}============".format(symbols[i]))
    #     train_and_val(symbols[i])

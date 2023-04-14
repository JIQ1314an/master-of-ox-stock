import os

from torch.autograd import Variable
import torch.nn as nn
import torch
from LSTMModel import lstm
from controller.fetch_data import get_single_stock_info
from parser_conf import args
from dataset import getData


def train():
    model = lstm(input_size=args.input_size, hidden_size=args.hidden_size, num_layers=args.layers, output_size=1,
                 dropout=args.dropout, batch_first=args.batch_first, bidirectional=args.bidirectional)
    model.to(args.device)
    criterion = nn.MSELoss()  # 定义损失函数
    optimizer = torch.optim.Adam(model.parameters(), lr=args.lr)  # Adam梯度下降  学习率=0.001

    close_max, close_min, train_loader, test_loader = getData(args.corpusFile, args.sequence_length, args.batch_size)
    better_loss = args.better_loss
    root_dir = os.path.dirname(os.path.abspath(__file__))
    save_model_file = os.path.join(root_dir, args.save_file)

    for i in range(1, args.epochs + 1):
        total_loss = 0
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
            total_loss += loss.item()
        # print(total_loss)
        if i % 100 == 0 and total_loss < better_loss:
            better_loss = total_loss
            # torch.save(model, args.save_file)

            torch.save({'state_dict': model.state_dict()}, save_model_file)
            print('第%d epoch，当前loss为 %.5f，保存模型' % (i, better_loss))
    # torch.save(model, args.save_file)
    torch.save({'state_dict': model.state_dict()}, save_model_file)


if __name__ == "__main__":
    symbol = "SH603000"
    args.corpusFile = get_single_stock_info(symbol)
    train()

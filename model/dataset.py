import pandas as pd
from pandas import read_csv
import numpy as np
from torch.utils.data import DataLoader, Dataset
import torch
from torchvision import transforms

from controller.drawing.utils import Tech
from controller.fetch_data import get_single_stock_info
from model.parser_conf import args

#
from model.utils import setup_seed


def data_enhancement(df):
    data = df.copy()
    t = Tech(df)
    data['ma5'] = t.ma()
    data['ema5'] = t.ema()
    # data['macd'], data['diff'], data['dea'] = t.macd()
    # data['k'], data['d'], data['j'] = t.kdj()
    data['rsi6'], data['rsi12'], data['rsi24'] = t.rsi()
    data['ad'] = t.ad()
    data = data.iloc[5:, :]
    # kdj_n = 9
    # data = data.iloc[kdj_n - 1:, :]


    # 把close放最后一列
    d = data.pop('close')
    data.insert(len(data.columns), 'close', d)  # 在第最后列的位置，添加列名为close的列d (d是数据)
    return data


def getData(corpusFile, sequence_length, batchSize):
    # 数据预处理 ，去除id、股票代码、前一天的收盘价、交易日期等对训练无用的无效数据
    if type(corpusFile) == str: stock_data = read_csv(corpusFile)
    if type(corpusFile) == pd.DataFrame: stock_data = corpusFile.copy()
    # stock_data.drop('ts_code', axis=1, inplace=True)  # 删除第二列’股票代码‘
    # stock_data.drop('id', axis=1, inplace=True)  # 删除第一列’id‘
    # stock_data.drop('pre_close', axis=1, inplace=True)  # 删除列’pre_close‘
    # stock_data.drop('trade_date', axis=1, inplace=True)  # 删除列’trade_date‘

    stock_data.drop('timestamp', axis=1, inplace=True)  # 删除列’trade_date‘

    stock_data = data_enhancement(stock_data)
    # print(stock_data.info())

    close_max = stock_data['close'].max()  # 收盘价的最大值
    close_min = stock_data['close'].min()  # 收盘价的最小值
    df = stock_data.apply(lambda x: (x - min(x)) / (max(x) - min(x)))  # min-max标准化
    # df = stock_data

    # 构造X和Y
    # 根据前n天的数据，预测未来一天的收盘价(close)， 例如：根据3月1日、3月2日、3月3日、3月4日、3月5日的数据（每一天的数据包含8个特征），预测3月6日的收盘价。
    sequence = sequence_length
    X = []
    Y = []
    for i in range(df.shape[0] - sequence):
        X.append(np.array(df.iloc[i:(i + sequence), :-1].values, dtype=np.float32))  # 前sequence天数据
        Y.append(np.array(df.iloc[(i + sequence), -1], dtype=np.float32))  # 第sequence+1天标签

    # 构建batch
    total_len = len(Y)
    if total_len == 0: return None, None, None, None
    # print("total_len", total_len)
    train_len = int(args.train_ratio * total_len)

    train_X, train_y = X[:train_len], Y[:train_len]
    test_X, test_y = X[train_len:], Y[train_len:]
    train_loader = DataLoader(dataset=Mydataset(train_X, train_y, transform=transforms.ToTensor()),
                              batch_size=batchSize, shuffle=True)
    test_loader = DataLoader(dataset=Mydataset(test_X, test_y), batch_size=batchSize, shuffle=True)

    return close_max, close_min, train_loader, test_loader


class Mydataset(Dataset):
    def __init__(self, xx, yy, transform=None):
        self.x = xx
        self.y = yy
        self.tranform = transform

    def __getitem__(self, index):
        x1 = self.x[index]
        y1 = self.y[index]
        if self.tranform != None:
            return self.tranform(x1), y1
        return x1, y1

    def __len__(self):
        return len(self.x)


if __name__ == "__main__":
    setup_seed(args)
    symbol = "SH603000"
    args.corpusFile = get_single_stock_info(symbol)

    close_max, close_min, train_loader, test_loader = getData(args.corpusFile, args.sequence_length, args.batch_size)
    # X是一个tensor（包括batchsize个三维数组，一个三维数组包括seqence个特征序列，预测一个y）, y也是一个tensor
    # print([(X, y) for X,y in train_loader][0])
    print([(X, y) for X, y in train_loader])
    # print(len([(X, y) for X,y in train_loader][0][-1])) # 长度等于batch_size
    # print([(X, y) for X,y in test_loader])

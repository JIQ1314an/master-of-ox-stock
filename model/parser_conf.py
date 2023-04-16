import argparse
import torch

parser = argparse.ArgumentParser()

parser.add_argument('--corpusFile', default='data/SZ300033.csv')  # 也可以是df类型
parser.add_argument('--train_ratio', default=0.8, type=int)  # train set 比例

# TODO 常改动参数
parser.add_argument('--gpu', default=0, type=int)  # gpu 卡号
parser.add_argument('--epochs', default=3000, type=int)  # 训练轮数
parser.add_argument('--layers', default=2, type=int)  # LSTM层数
parser.add_argument('--input_size', default=8, type=int)  # 输入特征的维度dim
parser.add_argument('--hidden_size', default=32, type=int)  # 隐藏层的维度
parser.add_argument('--bidirectional', default=False, type=bool)  # 是否使用双向的
parser.add_argument('--lr', default=0.0001, type=float)  # learning rate 学习率
parser.add_argument('--sequence_length', default=5, type=int)  # sequence的长度，默认是用前五天的数据来预测下一天的收盘价
parser.add_argument('--batch_size', default=64, type=int)
parser.add_argument('--useGPU', default=False, type=bool)  # 是否使用GPU
parser.add_argument('--batch_first', default=True, type=bool) # 是否将batch_size放在第一维  [N, L, H_in] batch_size、seq_len、input_dim
parser.add_argument('--dropout', default=0.1, type=float)
parser.add_argument('--save_file', default='save/stock.pkl')  # 模型保存位置

parser.add_argument('--better_loss', default=0.007, type=float)  # loss值

# args = parser.parse_args()
# ... 其他参数
args, unknown = parser.parse_known_args()

device = torch.device(f"cuda:{args.gpu}" if torch.cuda.is_available() and args.useGPU else "cpu")
args.device = device

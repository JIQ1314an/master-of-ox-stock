# -*- coding: utf-8 -*-
# @Time : 2023/4/30 19:36
# @Author : JIQ
# @Email : jiq1314an@qq.com
import logging
import random

import numpy as np
import torch
import torch
from torch.utils.data import DataLoader, random_split

from model.parser_conf import args


def setup_device(args):
    args.device = 'cuda' if torch.cuda.is_available() else 'cpu'
    args.n_gpu = torch.cuda.device_count()


def setup_seed(args):
    random.seed(args.seed)
    np.random.seed(args.seed)
    torch.manual_seed(args.seed)


def setup_logging():
    logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s',
                        datefmt='%Y-%m-%d %H:%M:%S',
                        level=logging.INFO)
    logger = logging.getLogger(__name__)

    return logger


def split_dataset(data_loader, split_ratio=0.6):
    # 定义划分比例，例如 0.6 表示将数据划分成 60% 和 40% 两部分

    # 计算划分的数量
    dataset_size = len(data_loader.dataset)
    split_lengths = [int(split_ratio * dataset_size), dataset_size - int(split_ratio * dataset_size)]
    # print(split_lengths)

    # 利用 random_split 函数进行划分
    val_dataset,test_dataset  = random_split(data_loader.dataset, split_lengths)

    # 根据划分后的子集创建新的数据加载器
    val_data_loader = DataLoader(val_dataset, batch_size=args.batch_size, shuffle=True)
    test_data_loader = DataLoader(test_dataset, batch_size=args.batch_size, shuffle=True)

    return   val_data_loader,test_data_loader

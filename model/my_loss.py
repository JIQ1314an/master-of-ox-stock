# -*- coding: utf-8 -*-
# @Time : 2023/5/03 13:23
# @Author : JIQ
# @Email : jiq1314an@qq.com
import torch
from torch import nn


class MSLELoss(nn.Module):
    def __init__(self):
        super(MSLELoss, self).__init__()
        self.mse_loss = nn.MSELoss()

    def forward(self, input, target):
        return self.mse_loss(torch.log(input + 1), torch.log(target + 1))


# 平滑L1损失函数（Huber Loss）
class HuberLoss(nn.Module):
    def __init__(self, delta):
        super(HuberLoss, self).__init__()
        self.delta = delta

    def forward(self, pred, target):
        diff = torch.abs(pred - target)
        mask = (diff < self.delta).float()
        loss = mask * 0.5 * diff ** 2 + (1 - mask) * (self.delta * diff - 0.5 * self.delta ** 2)
        return loss.mean()

# 效果不好
# class QuantileLoss(nn.Module):
#     def __init__(self, quantile):
#         super(QuantileLoss, self).__init__()
#         self.quantile = quantile
#
#     def forward(self, input, target):
#         diff = target - input
#         loss = torch.max((self.quantile - 1) * diff, self.quantile * diff)
#         return loss.mean()


# 效果不好
# # 时间序列平滑因子损失函数（Time Series Smoothing Factor Loss）
# class TimeSeriesSmoothingLoss(nn.Module):
#     def __init__(self, alpha):
#         super(TimeSeriesSmoothingLoss, self).__init__()
#         self.alpha = alpha
#
#     def forward(self, pred, target):
#         diff = torch.abs(pred - target)
#         loss = torch.exp(-self.alpha * diff) - self.alpha * diff - 1
#         return loss.mean()

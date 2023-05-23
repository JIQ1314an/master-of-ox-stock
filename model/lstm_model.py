import torch
import torch.nn as nn


class lstm(nn.Module):

    def __init__(self, input_size=8, hidden_size=32, num_layers=1, output_size=1, dropout=0,
                 batch_first=True, bidirectional=False):
        super(lstm, self).__init__()
        # lstm的输入 batch, seq_len, input_size
        self.hidden_size = hidden_size
        self.input_size = input_size
        self.num_layers = num_layers
        self.output_size = output_size
        self.dropout = dropout
        self.batch_first = batch_first
        self.bidirectional = bidirectional
        self.rnn = nn.LSTM(input_size=self.input_size, hidden_size=self.hidden_size,
                           num_layers=self.num_layers, batch_first=self.batch_first,
                           dropout=self.dropout, bidirectional=self.bidirectional)
        self.linear = nn.Linear(self.hidden_size, self.output_size)

    def forward(self, x):
        # x.shape : batch, seq_len, hidden_size , hn.shape and cn.shape : num_layes * direction_numbers, batch, hidden_size
        # out, (hidden, cell) = self.rnn(x)
        # out = self.linear(hidden)

        h0 = torch.zeros(self.num_layers, x.size(0), self.hidden_size).requires_grad_()
        c0 = torch.zeros(self.num_layers, x.size(0), self.hidden_size).requires_grad_()
        out, (hn, cn) = self.rnn(x, (h0.detach(), c0.detach()))
        out = self.linear(out[:, -1, :])
        return out

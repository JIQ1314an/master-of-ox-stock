# -*- coding: utf-8 -*-
# @Time : 2023/4/7 21:42
# @Author : JIQ
# @Email : jiq1314an@qq.com
from pyecharts import options as opts


class Tech:
    def __init__(self, data):
        self.data = data
        self.close = self.data['close']
        self.low = self.data['low']
        self.high = self.data['high']
        self.volume = self.data['volume']
        # self.pre_close = self.data['pre_close']
        # self.eob = self.data['eob']
        # self.bob = self.data['bob']

    def ma(self, n=5):
        '''
        含义：求简单移动平均。参数n:n日移动平均值，默认n=5
        用法：MA(X,N)，求X的N日移动平均值。算法：(X1+X2+X3+，，，+Xn)/N。例如：MA(CLOSE,10)表示求10日均价。
        '''
        ma_n = self.close.rolling(n).mean()
        return ma_n

    def ema(self, m=5):
        '''
        含义：求指数平滑移动平均。参数n:n日指数平滑移动平均。默认m=5
        用法：EMA(X,N)，求X的N日指数平滑移动平均。算法：若Y=EMA(X,N)则Y=[2*X+(N-1)*Y']/(N+1)，其中Y'表示上一周期Y值。例如：EMA(CLOSE,30)表示求30日指数平滑均价。
        '''
        ema = self.close.ewm(span=m).mean()
        return ema

    def macd(self, short=12, long=26, M=9):
        '''
        MACD指数平滑异同移动平均线为两条长、短的平滑平均线。参数默认short=12,long=26,M=9
            DIFF : EMA(CLOSE,SHORT) - EMA(CLOSE,LONG);
            DEA  : EMA(DIFF,M);
            MACD : 2*(DIFF-DEA);
        其买卖原则为：
            1.DIFF、DEA均为正，DIFF向上突破DEA，买入信号参考。
            2.DIFF、DEA均为负，DIFF向下跌破DEA，卖出信号参考。
            3.DEA线与K线发生背离，行情可能出现反转信号。
            4.分析MACD柱状线，由红变绿(正变负)，卖出信号参考；由绿变红，买入信号参考。
        '''
        ema_short = self.close.ewm(span=short).mean()
        ema_long = self.close.ewm(span=long).mean()
        diff = ema_short - ema_long
        dea = diff.ewm(span=M).mean()
        macd = 2 * (diff - dea)
        return macd, diff, dea

    def kdj(self, N=9, M1=3, M2=3):
        '''
        返回k、d、j的值，默认N=9,M1=3,M2=3
        RSV=(CLOSE-LLV(LOW,N))/(HHV(HIGH,N)-LLV(LOW,N))*100;
        LLV:求最低值，HHV：求最高值，LOW：当日（周期）最低价，HIGH：当日（周期）最高价
                a=SMA(RSV,M1,1);
                b=SMA(a,M2,1);
                e=3*a-2*b;
                K:a;D:b;J:e;同花顺中默认N=9,M1=3,M2=3；
        KDJ指标指标说明
            KDJ，其综合动量观念、强弱指标及移动平均线的优点，早年应用在期货投资方面，功能颇为显著，目前为股市中最常被使用的指标之一。
        买卖原则
            1 K线由右边向下交叉D值做卖，K线由右边向上交叉D值做买。
            2 高档连续二次向下交叉确认跌势，低挡连续二次向上交叉确认涨势。
            3 D值<20%超卖，D值>80%超买，J>100%超买，J<10%超卖。
            4 KD值于50%左右徘徊或交叉时，无意义。
            5 投机性太强的个股不适用。
            6 可观察KD值同股价的背离，以确认高低点。'''
        llv = self.low.rolling(N).min()  # 假设你的low是一个pandas.series的对象
        hhv = self.high.rolling(N).max()
        rsv = (self.close - llv) / (hhv - llv) * 100
        k = rsv.ewm(M1 - 1).mean()
        d = k.ewm(M2 - 1).mean()
        j = 3 * k - 2 * d
        return k, d, j

    def rsi(self, N1=6, N2=12, N3=24):
        '''
         默认N1=6,N2=12,N3=24，返回6日RSI值、12日RSI值、24日RSI值，RSI一般选用6日、12日、24日作为参考基期
            LC := REF(CLOSE,1);#上一周期的收盘价
            RSI$1:SMA(MAX(CLOSE-LC,0),N1,1)/SMA(ABS(CLOSE-LC),N1,1)*100;
            RSI$2:SMA(MAX(CLOSE-LC,0),N2,1)/SMA(ABS(CLOSE-LC),N2,1)*100;
            RSI$3:SMA(MAX(CLOSE-LC,0),N3,1)/SMA(ABS(CLOSE-LC),N3,1)*100;
            a:20;
            d:80;
        RSI指标：
            RSIS为1978年美国作者Wells WidlerJR。所提出的交易方法之一。所谓RSI英文全名为Relative Strenth Index，中文名称为相对强弱指标．RSI的基本原理是在一个正常的股市中，多
            空买卖双方的力道必须得到均衡，股价才能稳定;而RSI是对于固定期间内，股价上涨总幅度平均值占总幅度平均值的比例。
            1 RSI值于0-100之间呈常态分配，当6日RSI值为80‰以上时，股市呈超买现象，若出现M头，市场风险较大；当6日RSI值在20‰以下时，股市呈超卖现象，若出现W头，市场机会增大。
            2 RSI一般选用6日、12日、24日作为参考基期，基期越长越有趋势性(慢速RSI)，基期越短越有敏感性，(快速RSI)。当快速RSI由下往上突破慢速RSI时，机会增大；当快速RSI由上而下跌破慢速RSI时，风险增大。
        '''
        lc = self.close.shift(1)
        # 计算前收盘价
        max_diff = (self.close - lc)
        abs_diff = max_diff.copy()

        max_diff[max_diff < 0] = 0  # 实现MAX(CLOSE-LC,0)
        abs_diff = abs_diff.abs()  # 实现ABS(CLOSE-LC)

        RSI1, RSI2, RSI3 = (max_diff.ewm(N - 1).mean() / abs_diff.ewm(N - 1).mean() * 100 for N in [N1, N2, N3])
        return RSI1, RSI2, RSI3

    def ad(self, N=14):
        '''
        估算一段时间该证券积累的资金流量 无需参数
        sum(((c-l)-(h-c))/(h-l)*volume) 该值从第一天开始累加
        指标向上，价格向下，买进信号
        指标向下，价格向上，卖出信号
        '''
        ad = (((self.close - self.low) - (self.high - self.close)) / (self.high - self.low) * self.volume).cumsum()
        return ad

    def atr(self, N=14):
        '''
        求真实波幅的N日移动平均    参数：N 天数，默认取14
        TR:MAX(MAX((HIGH-LOW),ABS(REF(CLOSE,1)-HIGH)),ABS(REF(CLOSE,1)-LOW));
        ATR:MA(TR,N);'''
        maxx = self.high - self.low
        abs_high = (self.pre_close - self.high).abs()
        abs_low = (self.pre_close - self.low).abs()
        import pandas as pd
        a = pd.DataFrame()
        a['maxx'] = maxx.values
        a['abs_high'] = abs_high.values
        a['abs_low'] = abs_low.values
        TR = a.max(axis=1)
        ATR = TR.rolling(N).mean()
        return ATR

    def moving_average(self, day_count):
        # 移动平均数计算，另一种方法
        self.data = self.data.values[:, 0]
        result = []
        for i in range(len(self.data)):
            start_day_index = i - day_count + 1
            if start_day_index <= 0:
                start_day_index = 0
            justified_day_count = i - start_day_index + 1
            mean = self.data[start_day_index:i + 1].sum() / justified_day_count
            result.append(mean)
        return result


def ma_line_add_yaxis(ma_line, close_df, sname="MA5", window_num=5):
    ma_line.add_yaxis(
        series_name=sname,
        y_axis=Tech(close_df).moving_average(window_num),
        is_smooth=True,
        is_hover_animation=False,
        linestyle_opts=opts.LineStyleOpts(width=1, opacity=0.5),
        label_opts=opts.LabelOpts(is_show=False),
    )
    return ma_line

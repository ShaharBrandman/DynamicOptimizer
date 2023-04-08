import pandas as pd

import talib as TA

from backtesting import Strategy

from utils import getRunJson

def Signal(data: pd.DataFrame, params: dict) -> pd.Series:
    EMA = TA.EMA(data[params['Source']], 100)

    ce = calculateCE(data, params)

    arr = len(data['close']) * [None]

    for i in range(1, len(arr)):
        if ce[i] == 1 and data['close'][i] > EMA[i] and ce[i-1] == -1:
            arr[i] = 'LONG'
        elif ce[i] == -1 and data['close'][i] < EMA[i] and ce[i-1] == 1:
            arr[i] = 'SHORT'

    return arr

def calculateCE(data: pd.DataFrame, params: dict) -> pd.Series:
    longStop = calculateLongCE(data, params)
    shortStop = calculateShortCE(data, params)

    dir = pd.Series([1] * len(data))

    for i in range(1, len(data)):
        if data[i] > shortStop[i-1]:
            dir[i] = 1
        elif data[i] < longStop[i-1]:
            dir[i] = -1
        else:
            dir[i] = dir[i-1]

def calculateLongCE(data: pd.DataFrame, params: dict) -> pd.Series:
    ATR = params['ChandelierExit-Multiplier'] * TA.ATR(
        data['High'],
        data['Low'],
        data['Close'],
        params['ChandelierExit-Length']
    )

    longStop = data[params['Source']] - ATR

    for i in range(1, len(longStop)):
        if data['Source'][i-1] > longStop[i-1]:
            longStop[i] = max(longStop[i], longStop[i-1])
            
    return longStop

def calculateShortCE(data: pd.DataFrame, params: dict) -> pd.Series:
    ATR = params['ChandelierExit-Multiplier'] * TA.ATR(
        data['High'],
        data['Low'],
        data['Close'],
        params['ChandelierExit-Length']
    )

    shortStop = data[params['Source']] + ATR

    for i in range(1, len(shortStop)):
        if data[params['Source']][i-1] < shortStop[i-1]:
            shortStop[i] = min(shortStop[i], shortStop[i-1])

    return 

class daStrategy(Strategy):
    def init(self) -> None:
        super().init()

        self.params = getRunJson()['Strategy']['Params']
        
        self.longCE = self.I(calculateLongCE, self.data, self.params)
        self.shortCE = self.I(calculateShortCE, self.data, self.params)
        self.signal = self.I(Signal, self.data, self.params)

    def next(self):
        if (self.signal[-1] == 'LONG') and (len(self.trades) == 0):
            self.buy(tp = self.params['TPSL']['TakeProfit'], sl = self.params['TPSL']['StopLoss'])
        elif (self.signal[-1] == 'SHORT') and (len(self.trades) == 0):
            self.sell(tp = self.params['TPSL']['TakeProfit'], sl = self.params['TPSL']['StopLoss'])
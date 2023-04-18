import matplotlib

import pandas as pd

import talib as TA

from backtesting import Strategy

from utils import getRunJson

def Signal(data: pd.DataFrame, params: dict) -> pd.Series:
    EMA = TA.EMA(data[params['Source']], 100)
    
    ce = calculateCE(data, params)
    
    arr = [0] * len(data['Close'])
    
    for i in range(1, len(arr)):
        if ce[i] == 1 and data['Close'][i] > EMA[i] and ce[i-1] == -1:
            arr[i] = 1
        elif ce[i] == -1 and data['Close'][i] < EMA[i] and ce[i-1] == 1:
            arr[i] = -1

    return arr

def calculateCE(data: pd.DataFrame, params: dict) -> pd.Series:
    longStop = calculateLongCE(data, params)
    shortStop = calculateShortCE(data, params)
    
    dir = pd.Series([1] * len(data['Close']))
    
    for i in range(1, len(data)):
        if data[params['Source']][i] > shortStop[i-1]:
            dir[i] = 1
        elif data[params['Source']][i] < longStop[i-1]:
            dir[i] = -1
        else:
            dir[i] = dir[i-1]

    return dir

def calculateLongCE(data: pd.DataFrame, params: dict) -> pd.Series:
    ATR = params['ChandelierExit-Multiplier'] * TA.ATR(
        data['High'],
        data['Low'],
        data['Close'],
        params['ChandelierExit-Length']
    )

    longStop = data[params['Source']] - ATR

    for i in range(1, len(longStop)):
        if data[params['Source']][i-1] > longStop[i-1]:
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

    return shortStop

class daStrategy(Strategy):
    def init(self) -> None:
        super().init()

        self.params = getRunJson()['Strategy']['Params']
        print(self.params)
        
        self.longCE = self.I(calculateLongCE, self.data, self.params)
        self.shortCE = self.I(calculateShortCE, self.data, self.params)
        self.signal = self.I(Signal, self.data, self.params)

    def next(self):
        if (self.signal[-1] == 1) and (len(self.trades) == 0):
            self.buy(
                tp = self.data[self.params['Source']] * 1 + self.params['TPSL']['TakeProfit'],
                sl = self.data[self.params['Source']] * 1 - self.params['TPSL']['StopLoss']
            )
        elif (self.signal[-1] == -1) and (len(self.trades) == 0):
            self.sell(
                tp = self.data[self.params['Source']] * 1 - self.params['TPSL']['TakeProfit'],
                sl = self.data[self.params['Source']] * 1 + self.params['TPSL']['StopLoss']
            )
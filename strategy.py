import matplotlib

import pandas as pd

import talib as TA

from backtesting import Strategy

from utils import getRunJson

def Signal(data: pd.DataFrame, params: dict) -> None:
    firstSMA = TA.SMA(data[params['Source']], params['firstSMA'])
    secondSMA = TA.SMA(data[params['Source']], params['secondSMA'])

    arr = pd.Series([0] * len(data))

    for i in range(len(arr)):
        if firstSMA[i] < secondSMA[i]:
            arr[i] = 1 #long
        else:
            arr[i] = 2 #short
    print(arr[lambda e: e != 0])

    return arr

class daStrategy(Strategy):
    def init(self) -> None:
        super().init()

        self.params = getRunJson()['Strategy']['Params']
        print(self.params)
        
        self.signal = self.I(Signal, self.data, self.params)

    def next(self):
        if len(self.trades) > 0:
            if self.signal[-1] == 1 and self.trades[-1].is_short:
                self.trades[-1].close()
            elif self.signal[-1] == 2 and self.trades[-1].is_long:
                self.trades[-1].close()

        if self.signal[-1] == 1:
            self.buy(size = 0.99)
        elif self.signal[-1] == -1:
            self.sell(size = 0.99)
import matplotlib

import pandas as pd

import talib as TA

from backtesting import Strategy
from backtesting.lib import crossover

from utils import getRunJson

def SMA(data: pd.Series, n: int) -> pd.Series:
    return pd.Series(data).rolling(n).mean()

class daStrategy(Strategy):
    def init(self) -> None:
        super().init()

        self.params = getRunJson()['Strategy']['Params']
        
        self.firstSMA = self.I(SMA, self.data[self.params['Source']], self.params['firstSMA'])
        self.secondSMA = self.I(SMA, self.data[self.params['Source']], self.params['secondSMA'])
        
    def next(self):
        if len(self.trades) > 0:
            print(self.trades)
        if crossover(self.firstSMA, self.secondSMA):
            print('long')
            self.position.close()
            self.buy()
        elif crossover(self.secondSMA, self.firstSMA):
            print('short')
            self.position.close()
            self.sell()
'''
simple template of a strategy using backtesting.py
'''

import numpy

import pandas as pd

from typing import Union

from backtesting import Strategy

from utils import getOptimizedParams

class daStrategy(Strategy):
    def getSignal(self) -> pd.Series:
        pass

    def init(self) -> None:
        super().init()

        self.params = getOptimizedParams()

        for e in self.params:
            self.params[e] = int(self.params[e])

        print('==============\n')
        print(self.params)
        print('===============\n')

        print(self.data.df)

        print('==============\n')
        self.signal = self.I(
            self.getSignal
        )
        print('==============\n')
        print(self.signal)
        pritn('============\n')

    def next(self) -> None:
        super().next()

        pass


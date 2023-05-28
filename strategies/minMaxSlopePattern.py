'''
MinMaxSlopePattern Strategy is a technical analysis autumation to find Pivot points
which are the lowest of highest points in a timeseries from X candles left and Y candles right
given parameters like:
    * PIVOT_LENGTH - default: 3, float
    * BACK_CANDLES - default: 20, float
those design the processing of the dataframe (we optimize those as well)

Finding Patterns Parameters:
For Long & Short
    * R_MAX - default: 0.9, float
    * R_MIN - default: 0.9, float
    * SLOPE_MIN - default: 0.0001, float
    * SLOPE_MAX - default: 0.0001, float

Order Parameters:
    * TAKE_PROFIT_PER - default: 0.5, Union[float, int]
    * STOP_LOSS_PER   - default: 0.4, Union[float, int]
    * TARGET          - default: Close, str, Options = Close, Open, High, Low 
'''
import os
import numpy

import pandas as pd

from typing import Union

from backtesting import Strategy

from utils import getOptimizedParams

from .analysis import getPivotPoint, pointPivotPosition, getLinearRegression, findInBoundsPatterns

class MinMaxSlopePattern(Strategy):
    def getSignal(self) -> pd.Series:
        df = self.data.df

        df['pivot'] = df.apply( 
            lambda row: getPivotPoint(
                df,
                row.name,
                self.params['PIVOT_LENGTH'],
                self.params['PIVOT_LENGTH']
            ), 
            axis = 1
        )

        df['Patterns'] = getLinearRegression(df, self.params['BACK_CANDLES'])
        
        inBonudsPattern = findInBoundsPatterns(df, self.params)
        
        return pd.Series(inBonudsPattern)
    
    def init(self) -> None:
        super().init()

        self.params = getOptimizedParams()

        self.params['PIVOT_LENGTH'] = int(self.params['PIVOT_LENGTH'])
        self.params['BACK_CANDLES'] = int(self.params['BACK_CANDLES'])

        #TODO: code this feature:
        self.params['Source'] = 'Close'

        self.signal = self.I(
            self.getSignal
        )
        
    def next(self) -> None:
        if len(self.trades) == 0:
            if self.signal[-1] == 2:
                tp = float((self.data[self.params['Source']][-1] * (100 + self.params['TAKE_PROFIT_PER'])) / 100)
                sl = float((self.data[self.params['Source']][-1] * (100 - self.params['STOP_LOSS_PER'])) / 100)
                
                self.buy(
                    tp = tp,
                    sl = sl
                )
            elif self.signal[-1] == 1:
                tp = float((self.data[self.params['Source']][-1] * (100 - self.params['TAKE_PROFIT_PER'])) / 100)
                sl = float((self.data[self.params['Source']][-1] * (100 + self.params['STOP_LOSS_PER'])) / 100)


                self.sell(
                    tp = tp,
                    sl = sl
                )
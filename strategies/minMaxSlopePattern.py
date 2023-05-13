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
    * TAKE_PROFIT_PIPS - default: 100, Union[float, int]
    * STOP_LOSS_PIPS   - default: 50, Union[float, int]
    * TARGET           - default: Close, str, Options = Close, Open, High, Low 
'''

import numpy

import pandas as pd

from typing import Union

from backtesting import Strategy

from utils import getOptimizedParams

class MinMaxSlopePattern(Strategy):
    def getPivotPoint(df: pd.DataFrame, num: int, pivotLeft: int, pivotRight: int) -> int:
        if num - pivotLeft < 0 or num + pivotRight >= len(df):
            return 0
        
        pivotLow = 1
        pivotHigh = 1
        for i in range(num - pivotLeft, num + pivotRight + 1):
            if(df['Low'][num] > df['Low'][i]):
                pivotLow = 0
            if(df['High'][num] < df['High'][i]):
                pivotHigh = 0
        if pivotLow and pivotHigh:
            return 3
        elif pivotLow:
            return 1
        elif pivotHigh:
            return 2
        else:
            return 0
        
    def pointPivotPosition(row: pd.DataFrame) -> float:
        if row['pivot'] == 1:
            return row['Low'] -1e-3
        elif row['pivot'] == 2:
            return row['High'] + 1e-3
        else:
            return numpy.nan

    def findInBoundsPatterns(df: pd.DataFrame, params: dict) -> pd.Series:
        arr = pd.Series([0] * len(df))

        pMin = 0
        pMax = 0

        for i in range(len(df)):
            if df['Patterns'][i] == None:
                continue

            slmin, intercmin, rmin, pmin, semin = df['Patterns'][i]['minSlope']
            slmax, intercmax, rmax, pmax, semax = df['Patterns'][i]['maxSlope']

            #duplication avoidness
            if pMin == rmin and pMax == rmax:
                continue

            pMin = rmin
            pMax = rmax
            
            if abs(rmax) >= params['R_MAX_LONG'] and abs(rmin) >= params['R_MIN_LONG'] and slmin >= params['SL_MIN_LONG'] and slmax <= params['SL_MIN_LONG']:
                arr[i] == 2

            if abs(rmax) <= params['R_MAX_SHORT'] and abs(rmin) <= params['R_MIN_SHORT'] and slmin <= params['SL_MIN_SHORT'] and slmax >= params['SL_MAX_SHORT']:
                arr[i] == 1

        return arr

    def getSignal(self) -> pd.Series:
        df = self.data.df

        df['pivot'] = df.apply(
            lambda x: self.getPivotPoint(
                df, x.name,
                self.params['PIVOT_LENGTH'],
                self.params['PIVOT_LENGTH']
            ), 
            axis = 1
        )

        df['pointpos'] = df.apply(
            lambda row: self.pointPivotPosition(row),
            axis = 1
        )

        df['Patterns'] = getLinearRegression(self.params['BACK_CANDLES'])

        return self.findInBoundsPatterns(df, self.params)

    def init(self) -> None:
        super().init()

        self.params = getOptimizedParams()

        #int cast specific variables
        for e in self.params:
            match self.params[e]:
                case 'TAKE_PROFIT_PIPS', 'STOP_LOSS_PIPS', 'PIVOT_LENGTH', 'BACK_CANDLES':
                    self.params[e] = int(self.params[e])

        #depracted:
        self.params['Source'] = 'Close'

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

        if len(self.trades) > 0:
            if self.signal[-1] == 2:
                self.buy(
                    size = self.equity,
                    tp = self.params['Source'] + self.params['TAKE_PROFIT_PIPS'],
                    sl = self.params['Source'] - self.params['STOP_LOSS_PIPS']
                )
            elif self.signal[-1] == 1:
                self.sell(
                    size = self.equity,
                    tp = self.params['Source'] - self.params['TAKE_PROFIT_PIPS'],
                    sl = self.params['Source'] + self.params['STOP_LOSS_PIPS']
                )
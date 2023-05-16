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

from scipy.stats import linregress

from utils import getOptimizedParams

class MinMaxSlopePattern(Strategy):
    def getPivotPoint(self, df: pd.DataFrame, num: int, pivotLeft: int, pivotRight: int) -> int:
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

    def pointPivotPosition(self, row: pd.DataFrame) -> float:
        if row['pivot'] == 1:
            return row['Low'] -1e-3
        elif row['pivot'] == 2:
            return row['High'] + 1e-3
        else:
            return numpy.nan
    
    def findInBoundsPatterns(self, df: pd.DataFrame, params: dict) -> pd.Series:
        arr: list[int] = [0] * len(df)

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

            if abs(rmax) >= params['R_MAX_LONG'] and abs(rmin) >= params['R_MIN_LONG'] and slmin >= params['SL_MIN_LONG'] and slmax <= params['SL_MAX_LONG']:
                arr[i] = 2

            elif abs(rmax) <= params['R_MIN_SHORT'] and abs(rmin) <= params['R_MIN_SHORT'] and slmin <= params['SL_MIN_SHORT'] and slmax >= params['SL_MAX_SHORT']:
                arr[i] = 1

        return pd.Series(arr)

    def getLinearRegression(self, df: pd.DataFrame, BACK_CANDLES: int) -> pd.Series:
        linreg: list[any] = [None] * len(df)

        for candleid in range(BACK_CANDLES, len(df) - 1):
            maxSlope = numpy.array([])
            minSlope = numpy.array([])

            minSlopeIndex = numpy.array([])
            maxSlopeIndex = numpy.array([])

            for i in range(candleid - BACK_CANDLES, candleid + 1):
                if df['pivot'][i] == 1:
                    minSlope = numpy.append(minSlope, df['Low'][i])
                    minSlopeIndex = numpy.append(minSlopeIndex, i)
                if df['pivot'][i] == 2:
                    maxSlope = numpy.append(maxSlope, df['High'][i])
                    maxSlopeIndex = numpy.append(maxSlopeIndex, i)
            
            if (maxSlopeIndex.size <3 and minSlopeIndex.size <3) or maxSlopeIndex.size==0 or minSlopeIndex.size==0:
                continue
            
            #slmin, intercmin = np.polyfit(xxmin, minim,1)
            #slmax, intercmax = np.polyfit(xxmax, maxim,1)

            linreg[candleid] = {
                'minSlope': linregress(minSlopeIndex, minSlope), #slmin, intercmin, rmin, pmin, semin
                'maxSlope': linregress(maxSlopeIndex, maxSlope), #slmax, intercmax, rmax, pmax, semax
                'minSlopeArr': minSlope,
                'maxSlopeArr': maxSlope,
                'minSlopeIndex': minSlopeIndex,
                'maxSlopeIndex': maxSlopeIndex
            }

        return pd.Series(linreg)

    def getSignal(self) -> pd.Series:
        df = self.data.df

        df['pivot'] = df.apply( 
            lambda x: self.getPivotPoint(
                df,
                x.name,
                self.params['PIVOT_LENGTH'],
                self.params['PIVOT_LENGTH']
            ), 
            axis = 1
        )

        df['pointpos'] = df.apply(
            lambda row: self.pointPivotPosition(row),
            axis = 1
        )

        df['Patterns'] = self.getLinearRegression(df, self.params['BACK_CANDLES'])
        
        inBonudsPattern = self.findInBoundsPatterns(df, self.params)
        
        return pd.Series(inBonudsPattern)
    
    def init(self) -> None:
        super().init()

        self.params = getOptimizedParams()

        self.params['PIVOT_LENGTH'] = int(self.params['PIVOT_LENGTH'])
        self.params['BACK_CANDLES'] = int(self.params['BACK_CANDLES'])

        #depracted:
        self.params['Source'] = 'Close'

        #print(self.params)
        
        #print(self.data.df)

        self.signal = self.I(
            self.getSignal
        )

        #print(self.signal[self.signal != 0], f'\nlength: {len(self.signal)}')
        
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
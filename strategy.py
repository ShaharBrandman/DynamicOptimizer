import numpy

import pandas as pd

from typing import Union

from backtesting import Strategy

from scipy import stats

from utils import getOptimizedParams

class daStrategy(Strategy):
    def isPivot(self, pivotLength: int) -> pd.Series:
        """
        function that detects if a candle is a pivot/fractal point
        args: candle index, window before and after candle to test if pivot
        returns: 1 if pivot high, 2 if pivot low, 3 if both and 0 default
        """
        isPivot = pd.Series([0] * len(self.data['Close']))

        for targetCandle in range(len(isPivot)):
            if targetCandle-pivotLength < 0 or targetCandle+pivotLength >= len(self.data['Close']):
                isPivot[targetCandle] = 0
                
            pivotHigh = 1
            pivotLow = 2
            for i in range(targetCandle - pivotLength, targetCandle + pivotLength + 1):
                if self.data['Low'][targetCandle] > self.data['Low'][i]:
                    pivotLow=0
                if self.data['High'][targetCandle] < self.data['High'][i]:
                    pivotHigh=0
            
            if (pivotHigh and pivotLow):
                isPivot[targetCandle] = 3
            elif pivotHigh:
                isPivot[targetCandle] = pivotHigh
            elif pivotLow:
                isPivot[targetCandle] = pivotLow
            else:
                isPivot[targetCandle] = 0

        return isPivot

    def collect_channel(self, candleIndex: int, candlesBack: int, pivotLength: int) -> tuple:
        df = self.data.df[
            candleIndex - candlesBack - pivotLength 
            :
            candleIndex - pivotLength
        ]

        highs = df[df['isPivot']==1].High.values
        idxhighs = df[df['isPivot']==1].High.index
        lows = df[df['isPivot']==2].Low.values
        idxlows = df[df['isPivot']==2].Low.index
        
        if len(lows)>=2 and len(highs)>=2:
            sl_lows, interc_lows, r_value_l, _, _ = stats.linregress(idxlows,lows)
            sl_highs, interc_highs, r_value_h, _, _ = stats.linregress(idxhighs,highs)
        
            return(sl_lows, interc_lows, sl_highs, interc_highs, r_value_l**2, r_value_h**2)
        else:
            return(0,0,0,0,0,0)
        
    def isBreakOut(self, candleIndex: int, candlesBack: int, pivotLength: int) -> int:
        if (candleIndex-candlesBack-pivotLength)<0:
            return 0
        
        sl_lows, interc_lows, sl_highs, interc_highs, r_sq_l, r_sq_h = self.collect_channel(candleIndex, 
                                                                                    candlesBack, 
                                                                                    pivotLength)
        
        prev_idx = candleIndex-1

        df = self.data.df

        prev_high = df.iloc[candleIndex-1].High
        prev_low = df.iloc[candleIndex-1].Low
        prev_close = df.iloc[candleIndex-1].Close
        
        curr_idx = candleIndex
        #curr_high = df.iloc[candleIndex].High
        #curr_low = df.iloc[candleIndex].Low
        curr_close = df.iloc[candleIndex].Close
        curr_open = df.iloc[candleIndex].Open

        if ( prev_high > (sl_lows*prev_idx + interc_lows) and
            prev_close < (sl_lows*prev_idx + interc_lows) and
            curr_open < (sl_lows*curr_idx + interc_lows) and
            curr_close < (sl_lows*prev_idx + interc_lows)): #and r_sq_l > 0.9
            return 1
        
        elif ( prev_low < (sl_highs*prev_idx + interc_highs) and
            prev_close > (sl_highs*prev_idx + interc_highs) and
            curr_open > (sl_highs*curr_idx + interc_highs) and
            curr_close > (sl_highs*prev_idx + interc_highs)): #and r_sq_h > 0.9
            return 2
        
        else:
            return 0

    def getSignal(self) -> pd.Series:
        print(self.params)
        signal = pd.Series([0] * len(self.data['Close']))

        for i in range(len(signal)):
            signal[i] = self.isBreakOut(i, self.params['candlesBack'], self.params['pivotLength'])
        
        return signal

    def init(self) -> None:
        super().init()

        self.params = getOptimizedParams()

        for e in self.params:
            self.params[e] = int(self.params[e])

        print('==============\n')
        print(self.params)
        print('===============\n')

        self.data['isPivot'] = self.isPivot(self.params['pivotLength'])

        self.signal = self.I(
            self.getSignal
        )

    def next(self):
        super().next()

        if len(self.trades[-1]) <= int(self.params['maxTrades']):
            if self.signal[-1] == 1:
                tp = self.data['Close'] + self.params['takeProfitPip']
                sl = self.data['Close'] - self.params['stopLossPip']
                self.buy(tp = tp, sl = sl)
            elif self.signa[-1] == 2:
                tp = self.data['Close'] - self.params['takeProfitPip']
                sl = self.data['Close'] + self.params['stopLossPip']
                self.sell(tp = tp, sl = sl)


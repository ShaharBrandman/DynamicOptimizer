import math

import pandas as pd
import talib as TA

from strategy import Strategy

from tools import validateParams

from exceptions import InvalidTakeProfitStopLoss

class CE(Strategy):
    def longStopCE(self, data: pd.Series, ceLength: int, ceMult: float) -> pd.Series:
        atr = ceMult * TA.ATR(data, ceLength)

        longStop = data - atr

        for i in range(1, len(longStop)):
            if data[i-1] > longStop[i-1]:
                longStop[i] = max(longStop[i], longStop[i-1])
            
        return longStop

    def shortStopCE(self, data: pd.Series, ceLength: int, ceMult: float) -> pd.Series:
        atr = ceMult * TA.ATR(data, ceLength)

        shortStop = data + atr

        for i in range(1, len(shortStop)):
            if data[i-1] < shortStop[i-1]:
                shortStop[i] = min(shortStop[i], shortStop[i-1])


        return shortStop

    def calculateZLSMA(self, data: pd.Series, zLength: int) -> pd.Series:
        lsma = TA.LINREG(data, zLength)
        secondLsma = TA.LINREG(lsma, zLength)
        eq = lsma - secondLsma
        return lsma + eq

    def calculateCE(self, data: pd.Series, ceLength: int, ceMult: float) -> pd.Series:
        longStop = self.longStopCE(data, ceLength, ceMult)
        shortStop = self.shortStopCE(data, ceLength, ceMult)

        dir = pd.Series([1] * len(data))

        for i in range(1, len(data)):
            if data[i] > shortStop[i-1]:
                dir[i] = 1
            elif data[i] < longStop[i-1]:
                dir[i] = -1
            else:
                dir[i] = dir[i-1]

    def setTakeProfitAndStopLoss(self, params: dict) -> None:
        validateParams(
            self.__class__.__name__,
            params
        )

        if params['TPSL']['useTakeProfit'] is True:
        
            def defintion(params: dict) -> tuple:
                return params['TPSL']['TakeProfit'], params['TPSL']['StopLoss']

            super().setTakeProfitAndStopLoss(defintion(params))

    def setLongConditions(self, params: dict) -> None:
        validateParams(
            self.__class__.__name__,
            params
        )

        def defintion(self, data: pd.DataFrame) -> pd.Series:
            CE = self.calculateCE(
                data[params['Source']],
                params['ChandelierExit-Length'],
                params['ChandelierExit-Multiplier']
            )
            ZLSMA = self.calculateZLSMA(data[params['Source']], params['ZLSMA-Length'])

            arr = pd.Series([0] * len(data[params['Source']]))

            for i in range(1, len(arr)):
                if CE[i] == 1 and ZLSMA[i] < data[params['Source']][i] and CE[i-1] == -1:
                    arr[i] = 1

            return arr

        super().setLongConditions(defintion)

    def setShortConditions(self, params: dict) -> None:
        validateParams(
            self.__class__.__name__,
            params
        )

        def defintion(self, data: pd.DataFrame) -> pd.Series:
            CE = self.calculateCE(
                params['ChandelierExit-Length'],
                params['ChandelierExit-Multiplier']
            )
            ZLSMA = self.calculateZLSMA(params['ZLSMA-Length'])

            arr = pd.Series([0] * len(data[params['Source']]))

            for i in range(1, len(arr)):
                if CE[i] == -1 and ZLSMA[i] > data[params['Source']][i] and CE[i-1] == 1:
                    arr[i] = 1

            return arr

        super().setLongConditions(defintion)

class UMAR(Strategy):
    def setTakeProfitAndStopLoss(self, params: dict, data: pd.DataFrame = None) -> None:
        validateParams(
            self.__class__.__name__,
            params
        )

        if params['TPSL']['useTakeProfit'] is True:
            if params['TPSL']['useATRBands'] is True:
                if data is None:
                    raise InvalidTakeProfitStopLoss('useATRBands is True and DataFrame is None brother')
                
                def definition(self, data: pd.DataFrame, params: dict) -> tuple:
                    upperBand = TA.ATR(data[params['ATR-UpperBand-Source']], params['ATR-Bands-Length']) * params['ATR-UpperBand-Multiplier']
                    lowerBand = TA.ATR(data[params['ATR-LowerBand-Source']], params['ATR-Bands-Length']) * params['ATR-LowerBand-Multiplier']

                    if 'Risk/Reward-Ratio' in params['TPSL']:
                        if self.direction == 'Long':
                            takeProfit = (lowerBand * (100 + params['TPSL']['Risk/Reward-Ratio'])) / 100

                            return takeProfit, lowerBand
                        else:
                            takeProfit = (upperBand * (100 - params['TPSL']['Risk/Reward-Ratio'])) / 100

                            return takeProfit, upperBand
                    else:
                        return upperBand, lowerBand

                super().setTakeProfitAndStopLoss(definition(data, params))
            else:
                def defintion(params: dict) -> tuple:
                    validateParams(
                        self.__class__.__name__,
                        params
                    )

                    return params['TPSL']['TakeProfit'], params['TPSL']['StopLoss']

                super().setTakeProfitAndStopLoss(definition(params))

    def onLongCondition(self, index: int) -> None:
        self.direction = 'Long'
        return super().onLongCondition(index)

    def onShortCondition(self, index: int) -> None:
        self.direction = 'Short'
        return super().onShortCondition(index)

    def setLongConditions(self, params: dict) -> None:
        validateParams(
            self.__class__.__name__,
            params
        )

        def defintion(data: pd.DataFrame) -> pd.Series:
            rsi = TA.RSI(data[params['Source']], params['RSI-Length'])
            adx = TA.ADX(data['high'], data['low'], data['close'], params['ADX-Length'])
            umas = UMAS.calculateMovingAverage(self, params['Source'], params['MA-Length'], params['MA-Type'])

            arr = pd.Series([0] * len(data[params['Source']]))

            for i in range(len(arr)):
                if umas[i] >= umas[params['Smoothing']] and rsi[i] >= params['RSI-UpperLevel'] and adx[i] >= params['ADX-Cross']:
                    arr[i] = 1

            return arr

        super().setLongConditions(defintion)

    def setShortConditions(self, params: dict) -> None:
        validateParams(
            self.__class__.__name__,
            params
        )

        def defintion(data: pd.DataFrame):
            rsi = TA.RSI(data[params['Source']], params['RSI-Length'])
            adx = TA.ADX(data['high'], data['low'], data['close'], params['ADX-Length'])
            umas = UMAS.calculateMovingAverage(self, params['Source'], params['MA-Length'], params['MA-Type'])

            arr = pd.Series([0] * len(data[params['Source']]))

            for i in range(len(arr)):
                if umas[i] < umas[params['Smoothing']] and rsi[i] <= params['RSI-LowerLevel'] and adx[i] >= params['ADX-Cross']:
                    arr[i] = 1

            return arr

        super().setShortConditions(defintion)

class UMAS(Strategy):
    def calculateMovingAverage(self: Strategy, source: str, maLength: int, maType: int = 1) -> pd.Series:
        if maType == 1:
            return TA.SMA(source, maLength)
        elif maType == 2:
            return TA.EMA(source, maLength)
        elif maType == 3:
            return TA.WMA(source, maLength)
        elif maType == 4:
            #hull Moving Average
            return TA.WMA(
                2 * TA.WMA(source, maLength / 2) - TA.WMA(source, maLength),
                math.round(math.sqrt(maLength))
            )
        elif maType == 5:
            return TA.VWMA(source, maLength)
        elif maType == 6:
            return TA.RMA(source, maLength)
        else:
            firstEMA = TA.EMA(source, maLength)
            secondEMA = TA.EMA(firstEMA, maLength)
            thirdEMA = TA.EMA(secondEMA, maLength)

            tema = 3 * (firstEMA - secondEMA) + thirdEMA

            return tema

    def setLongConditions(self, params: dict) -> None:
        validateParams(
            self.__class__.__name__,
            params
        )

        def defintion(self, data: pd.DataFrame) -> pd.Series:
            ma = self.calculateMovingAverage(
                data,
                params['Source'],
                params['maLength'],
                params['maType']
            )

            arr = pd.Series([0] * len(data[params['Source']]))

            for i in range(len(arr)):
                if ma[i] >= ma[params['Smoothing']]:
                    arr[i] = 1
            
            return arr

        super().setLongConditions(defintion)

    def setShortConditions(self, params: dict) -> None:
        validateParams(
            self.__class__.__name__,
            params
        )

        def defintion(self, data: pd.DataFrame) -> pd.Series:
            ma = self.calculateMovingAverage(
                data,
                params['Source'],
                params['maLength'],
                params['maType']
            )

            arr = pd.Series([0] * len(data[params['Source']]))

            for i in range(len(arr)):
                if ma[i] < ma[params['Smoothing']]:
                    arr[i] = 1
            
            return arr

        super().setShortConditions(defintion)

Strategies = {
    'CE': CE,
    'UMAR': UMAR,
    'UMAS': UMAS
}
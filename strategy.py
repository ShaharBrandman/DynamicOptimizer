'''
TradingOptimizer/strategy.py

Contains the basic abstract interface of a strategy

Author: ShaharBrandman (2023)
'''
import csv
import pandas as pd

from datetime import datetime

from pybit import usdt_perpetual

from exceptions import InvalidLongCondition, InvalidShortCondition, InvalidPortoflio

from tools import getClosedPosition, getConfig, getData, validateDataFrame

class Strategy:
    '''
    Strategy Parameters: \n
    @src: close, open, high, low\n
    @pair: BTCUSDT, ETHUSDT, DOGEUSDT, ADAUSDT\n
    @timeframe: 1, 5, 15, 30, 60\n
    @candlesToLooks: default = 1000\n
    @dataset: default = None\n
    
    Interface Functions\n
     * setLongConditions(function) required\n
     * setShortConditions(function) required\n
     * setPortfolio(equity, leverage, commission, percentage (optional)) required \n
     * setTakeProfitAndStopLoss(function)
    '''

    def __init__(self, src: str, pair: str, timeframe: str, candlesToLooks: int = 1000, dataframe: pd.DataFrame = None) -> None:
        self.ID = f'{src}-{pair}-{timeframe}-{candlesToLooks}-{datetime.now().timestamp()}'
        self.src = src
        self.pair = pair
        self.timeframe = timeframe
        self.candlesToLooks = candlesToLooks

        if dataframe != None:
            validateDataFrame(dataframe)
            self.data = dataframe

        c = getConfig()

        self.client = usdt_perpetual.HTTP(
            endpoint = c['bybitEndpoint'],
            api_key = c['bybitAPIKey'],
            api_secret = c['bybitAPISecretKey']
        )

    def setLongConditions(self, defintion: callable) -> None:
        '''
        @required = true \n
        define how to calculate long conditions
        '''
        self.longConditions = defintion

    def setShortConditions(self, defintion: callable) -> None:
        '''
        @required = true \n
        define how to calculate short conditions
        '''
        self.shortConditions = defintion

    def setPortfolio(self, equity: float, leverage: int, commision: float, percentPerPosition: float = 100) -> None:
        '''
        @required = true\
        sets equity, leverage and commision and percentPerPosition (optional)
        '''

        self.budget = (self.equity * percentPerPosition) / 100

        self.portoflio = {
            'equity': equity,
            'leverage': leverage,
            'commision': commision,
            'percentPerPosition': percentPerPosition
        }

    def setTakeProfitAndStopLoss(self, defintion: callable) -> None:
        '''
        @required = false \n
        define how to calculate take profits and stop losses \n
        @default = exit position when condition is changed
        '''
        self.takeprofitstoploss = defintion

    def onLongCondition(self, index: int) -> None:
        currentCandle = self.data[self.src][index]

        for i in range(self.positions):
            if self.positions[i]['Exit'] == 'On Long Condition':
                self.positions[i]['Status'] = 'CLOSED'
                self.closedPositions.append(
                    getClosedPosition(self.portoflio, self.positions[i], currentCandle)
                )

        if self.takeprofitstoploss != None:
            takeprofit, stoploss = self.takeprofitstoploss()

            self.positions.append({
                'ID': self.data['open_time'][index],
                'State': 'OPEN',
                'type': 'Long',
                'Entry': self.data[self.src][index],
                'Exit': {
                    'TakeProfit': takeprofit,
                    'StopLoss': stoploss
                }
            })
        else:
            self.positions.append({
                'ID': self.data['open_time'][index],
                'State': 'OPEN',
                'type': 'Long',
                'Exit': 'On Short Condition'
            })

    def onShortCondition(self, index: int) -> None:
        currentCandle = self.data[self.src][index]

        for i in range(self.positions):
            if self.positions[i]['Exit'] == 'On Long Condition':
                self.positions[i]['Status'] = 'CLOSED'
                self.closedPositions.append(
                    getClosedPosition(self.portoflio, self.positions[i], currentCandle)
                )

        if self.takeprofitstoploss != None:
            takeprofit, stoploss = self.takeprofitstoploss()

            self.positions.append({
                'ID': self.data['interval'][index],
                'State': 'OPEN',
                'type': 'Short',
                'Entry': self.data[self.src][index],
                'Exit': {
                    'TakeProfit': takeprofit,
                    'StopLoss': stoploss
                }
            })
        else:
            self.positions.append({
                'ID': self.data['interval'][index],
                'State': 'OPEN',
                'type': 'Short',
                'Exit': 'On Long Condition'
            })

    def checkPositions(self, currentIndex) -> None:
        for i in range(len(self.positions)):
            if self.positions['Status'] != 'OPEN':
                continue
            tp = self.positions[i]['Exit']['TakeProfit']
            sl = self.positions[i]['Exit']['StopLoss']

            #long position
            if self.positions[i]['Type'] == 'Long':
                exitPrice = 0

                #win
                if self.data['high'][currentIndex] >= tp or self.data['close'][currentIndex] >= tp:
                    exitPrice = tp
                #loss
                elif self.data['low'][currentIndex] <= sl or self.data['close'][currentIndex] <= sl:
                    exitPrice = sl
                else:
                    continue

                self.positions[i]['Status'] = 'CLOSED'

                self.closedPositions.append(
                    getClosedPosition(
                        self.portoflio,
                        self.positions[i],
                        exitPrice
                    )
                ) 

            if self.positions[i]['Type'] == 'Short':
                exitPrice = 0
                #win
                if self.data['low'][currentIndex] <= tp or self.data['close'][currentIndex] <= tp:
                    exitPrice = tp
                #loss
                elif self.data['high'][currentIndex] >= sl or self.data['close'][currentIndex] >= sl:
                    exitPrice = sl
                else:
                    continue

                self.positions[i]['Status'] = 'CLOSED'

                self.closedPositions.append(
                    getClosedPosition(
                        self.portoflio,
                        self.positions[i],
                        exitPrice
                    )
                )  

    def backtest(self) -> None:
        wins = 0
        losses = 0
        
        for e in self.closedPositions:
            if e['PNL'] > 0:
                wins += 1

                self.budget = (self.budget * (100 + e['PNL'])) / 100 #add PNL to budget
                self.budget = (self.budget * (100 - self.portoflio.commision)) #clean commision
            else:
                losses += 1

                self.budget = (self.budget * (100 - e['PNL'])) / 100 #minus PNL to budget
                self.budget = (self.budget * (100 - self.portoflio.commision)) #clean commision :(

        totalPNL = (self.budget * 100) / self.equity
        accuracy = (wins * 100) / wins + losses

        with open(f'closedPositions/{self.ID}-{accuracy}-{totalPNL}-{self.portoflio.leverage}-{wins + losses}-closedPositions.csv', 'w') as f:
            w = csv.writer(f, delimiter=',')
            w.writerows(self.closedPositions) 
            f.close()   

    def runStrategy(self) -> None:
        '''
        runs the strategy
        '''
        if self.longCondition is None:
            raise InvalidLongCondition('Long Condition cant be None')

        if self.shortCondition is None:
            raise InvalidShortCondition('Short Condition cant be None')

        if self.portoflio is None:
            raise InvalidPortoflio('Portoflio cant be None')

        if self.data == None:
            self.data = getData(self.pair, self.timeframe, self.candlesToLooks, self.client).astype('float')

        self.data['longConditions'] = self.longConditions(self.data)
        self.data['shortConditions'] = self.shortConditions(self.data)

        #save dataset as a file
        with open(f'datasets/{self.ID}-dataset', 'w') as f:
            f.write(self.data.to_csv())
            f.close()

        '''
        positions structure:
            * ID
            * State
            * Type
            * Entry [float]
            * Exit [TakeProfit, StopLoss or when condition changed]
        '''
        self.positions = []

        '''
        closed positions structure:
            * ID
            * State
            * Type
            * PNL
            * Entry [float]
            * Exit [float]
        '''
        self.closedPositions = []

        for index in range(len(self.data['longConditions'])):
            if self.data['longConditions'][index] == 1:
                self.onLongCondition()

            if self.data['shortConditions'][index] == 1:
                self.onShortCondition()

            self.checkPositions(index)

        self.backtest()
from threading import Thread

from backtesting import Backtest

from pybit import usdt_perpetual

from strategy import daStrategy

from tools import randomizeParams, randomizePair, randomizeTimeframe, validateParams, isBetter

from utils import getData, getConfig

class Optimizer(Thread):
    def __init__(self, params: dict) -> None:
        validateParams(params)

        c = getConfig()

        self.client = usdt_perpetual.HTTP(
            endpoint = c['bybitEndpoint'],
            api_key = c['bybitAPIKey'],
            api_secret = c['bybitAPISecretKey']
        )

        self.params = params

    def getData(self):
        self.data = getData(
            self.params['Strategy']['Pair'],
            self.params['Strategy']['Timeframe'],
            self.params['Strategy']['dataLength'],
            self.client
        )

    def start(self) -> None:
        datasetChanged = False
        
        mostProfitable = {
            'Duration': 0,
            'Return': 0,
            'SharpeRatio': 0,
            'MaxDrawdown': 0,
            'Trades': 0,
            'WinRate': 0,
            'Profit Factor': 0
        }

        for i in range(self.params['Optimizer']['loops']):

            if self.params['Optimizer']['randomizeParamEveryLoop']:
                self.params['Strategy']['Params'] = randomizeParams(self.params['Strategy']['Params'])

            if self.params['Optimizer']['randomizeTimeframeEveryLoop']:
                self.params['Strategy']['Pair'] = randomizePair()
                datasetChanged = True

            if self.params['Optimizer']['randomizeTimeframeEveryLoop']:
                self.params['Strategy']['Timeframe'] = randomizeTimeframe()
                datasetChanged = True

            if datasetChanged:
                self.getData()

            if self.data == None:
                self.getData()

            bt = Backtest(
                self.data,
                daStrategy(),
                cash = self.params['Portfolio']['Equity'],
                margin = 1 / self.params['Portfolio']['Leverage'],
                commission = self.params['Portfolio']['Commision']
            ).run()

            mostProfitable = isBetter(mostProfitable, bt)
        pass
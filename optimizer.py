from threading import Thread

from backtesting import Backtest

from pybit import usdt_perpetual

import pandas as pd

from strategy import daStrategy

from utils import getData, getConfig

class Optimizer(Thread):
    def __init__(self, params: dict) -> None:
        c = getConfig()

        self.client = usdt_perpetual.HTTP(
            endpoint = c['bybitEndpoint'],
            api_key = c['bybitAPIKey'],
            api_secret = c['bybitAPISecretKey']
        )

        self.params = params

    def start(self) -> None:
        data = getData(
            self.params['Strategy']['Pair'],
            self.params['Strategy']['Timeframe'],
            self.params['Strategy']['dataLength'],
            self.client
        ).astype('float')

        data[['High', 'Low', 'Open', 'Close', 'Volume']] = data[['high', 'low', 'open', 'close', 'volume']].copy()
        data.drop(columns= ['high', 'low', 'open', 'close', 'volume'])
        #print(data)
        
        bt = Backtest(
            data,
            daStrategy,
            cash = self.params['Portfolio']['Equity'],
            margin = 1 / self.params['Portfolio']['Leverage'],
            commission = self.params['Portfolio']['Commision']
        ).run()

        bt.plot()
        print(bt)
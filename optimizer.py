from threading import Thread

from backtesting import Backtest

from strategy import daStrategy

from bybitHTTPX import BybitClient

from utils import getData, getConfig

class Optimizer(Thread):
    def __init__(self, params: dict) -> None:
        c = getConfig()

        self.client = BybitClient(
            url = c['bybitEndpoint'],
            apiKey = c['bybitAPIKey'],
            apiSecret = c['bybitAPISecretKey']
        )

        self.params = params

    def start(self) -> None:
        data = getData(
            self.params['Strategy']['Pair'],
            self.params['Strategy']['Timeframe'],
            self.params['Strategy']['dataLength'],
            self.client
        ).astype('float')
        
        bt = Backtest(
            data,
            daStrategy,
            cash = self.params['Portfolio']['Equity'],
            margin = 1 / self.params['Portfolio']['Leverage'],
            commission = self.params['Portfolio']['Commision']
        )

        stat = bt.run()
        
        print(stat)

        bt.plot()
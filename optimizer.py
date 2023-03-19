import pandas as pd

from threading import Thread

from strategy import Strategy

from tools import getStrategy, randomizeParams

class Optimizer(Thread):
    def __init__(self, portfolio: dict, strategy: Strategy, paramsToRandomize: dict, loops: int = 1000) -> None:
        self.strategy = strategy
        self.portfolio = portfolio
        self.paramsToRandomize = paramsToRandomize
        self.loops = loops

    def run(self) -> None:
        for i in range(self.loops):
            randomizeParams(self.paramsToRandomize)

            self.strategy.setLongConditions(self.paramsToRandomize)
            self.strategy.setShortConditions(self.paramsToRandomize)
            self.strategy.setPortfolio(self.portfolio)
            
            if 'TPSL' in self.paramsToRandomize:
                if self.paramsToRandomize['TPSL']['useTakeProfit'] == True:
                    self.strategy.setTakeProfitAndStopLoss(self.paramsToRandomize['TPSL'])

            
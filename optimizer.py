import json
import logging

from threading import Thread

from strategy import Strategy

from tools import *
from utils import *

class Optimizer(Thread):
    def __init__(self, portfolio: dict, strategy: Strategy, paramsToRandomize: dict, loops: int = 1000) -> None:
        validatePortfolio(portfolio)
        
        self.portfolio = portfolio
        self.strategy = strategy
        self.paramsToRandomize = paramsToRandomize
        self.loops = loops

        self.bestPNL = {
            'PNL': 0.0,
            'params': None
        }

        self.bestAccuracy = {
            'accuracy': 0.0,
            'params': None
        }

    def run(self) -> None:
        for i in range(self.loops):
            randomizeParams(self.paramsToRandomize)

            self.strategy.setLongConditions(self.paramsToRandomize)
            self.strategy.setShortConditions(self.paramsToRandomize)
            self.strategy.setPortfolio(
                self.portfolio['Equity'],
                self.portfolio['Leverage'],
                self.portfolio['Commision'],
                self.portfolio['PercentPerPosition']
            )
            
            if 'TPSL' in self.paramsToRandomize:
                if self.paramsToRandomize['TPSL']['useTakeProfit'] == True:
                    self.strategy.setTakeProfitAndStopLoss(self.paramsToRandomize['TPSL'])

            strategyID = self.strategy.ID
            self.strategy.runStrategy()

            status = json.loads(open(f'output/strategiesStats/{strategyID}.json', 'r').read())
            
            if status['PNL'] >= self.bestPNL['PNL']:
                self.bestPNL['PNL'] = status['PNL']
                self.bestPNL['params'] = self.paramsToRandomize

            if status['accuracy'] >= self.bestAccuracy['accuracy']:
                self.bestAccuracy['accuracy'] = status['accuracy']
                self.bestAccuracy['params'] = self.paramsToRandomize

            print(f'loop #{i}, params: {self.paramsToRandomize}, PNL: {status["PNL"]}%, Accuracy: {status["accuracy"]}%\n')
            logging.debug(f'loop #{i}, params: {self.paramsToRandomize}, PNL: {status["PNL"]}%, Accuracy: {status["accuracy"]}%')

        logging.debug(f'bestPNL: {self.bestPNL["PNL"]}, params: {self.bestPNL["params"]}')
        logging.debug(f'bestAccuracy: {self.bestAccuracy["accuracy"]}, params: {self.bestPNL["params"]}')

        print(f'bestPNL: {self.bestPNL["PNL"]}, params: {self.bestPNL["params"]}\n')
        print(f'bestAccuracy: {self.bestAccuracy["accuracy"]}, params: {self.bestPNL["params"]}\n')

            

        
                    
            

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
        self.loops = int(loops)

        self.best = {
            'PNL': 0.0,
            'accuracy': 0.0,
            'params': []
        }

        super().__init__()

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
            
            if (status['PNL'] >= self.best['PNL']) and (status['accuracy'] >= self.best['accuracy']):
                self.best['PNL'] = status['PNL']
                self.best['accuracy'] = status['accuracy']
                self.best['params'] = self.paramsToRandomize

            print(f'loop #{i}, params: {self.paramsToRandomize}, PNL: {status["PNL"]}%, Accuracy: {status["accuracy"]}%\n')
            logging.debug(f'loop #{i}, params: {self.paramsToRandomize}, PNL: {status["PNL"]}%, Accuracy: {status["accuracy"]}%')

        logging.debug(f'best params: {self.paramsToRandomize}')
        logging.debug(f'best PNL {self.best["PNL"]}, best accuracy: {self.best["accuracy"]}')

        print(f'best params: {self.paramsToRandomize}\n')
        print(f'best PNL {self.best["PNL"]}, best accuracy: {self.best["accuracy"]}\n')

            

        
                    
            

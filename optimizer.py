import os
import json
import logging

from typing import Union

from threading import Thread

from functools import lru_cache

import numpy

import pandas as pd

from backtesting import Backtest

from bayes_opt import BayesianOptimization
from bayes_opt.logger import JSONLogger
from bayes_opt.event import Events
from bayes_opt.util import load_logs

from strategies.minMaxSlopePattern import MinMaxSlopePattern

from utils import getDataset, getInternalDataset, getDatasetFromYahoo, saveOptimiezdParamsToJson, savePatterns

class Optimizer(Thread):

    @lru_cache(maxsize = None)
    def loadData(self) -> Union[pd.DataFrame, dict[str, pd.DataFrame]]:
        data: Union[pd.DataFrame, dict[str, pd.DataFrame]] = None

        logging.debug(f'{self.runID} - loading data')

        if 'yFinance' in self.params['Strategy']:
            data = getDatasetFromYahoo(
                self.params['Strategy']['yFinance']['pair'],
                self.params['Strategy']['yFinance']['period'],
                self.params['Strategy']['yFinance']['interval']
            )

            logging.debug(f"{self.runID} - loaded data from yFinance, details: {self.params['Strategy']['yFinance']}")
        elif 'DatasetPath' in self.params['Strategy']:
            data = getInternalDataset(self.params['Strategy']['DatasetPath'])

            logging.debug(f'{self.runID} - loaded data from {self.params["Strategy"]["DatasetPath"]}')
        elif 'DatasetURL' in self.params['Strategy']:
            data = getDataset(self.params['Strategy']['DatasetURL'])

            logging.debug(f'{self.runID} - loaded data from {self.params["Strategy"]["DatasetURL"]}')
        else:
            raise Exception(f'No Data Source, Strategy has to include attributes yFinance or DatasetPath or DatasetURL')

        return data

    def loadBounds(self) -> dict:
        bounds: dict = {}

        logging.debug(f'{self.runID} - loading Bounds')

        for e in self.params['Strategy']['Params']:
            if e == 'Source':
                continue
            
            bounds[e] = (
                self.params['Strategy']['Params'][e]['min'],
                self.params['Strategy']['Params'][e]['max']
            )

        logging.debug(f'{self.runID} - got bounds: {bounds}')

        return bounds
    
    def loadBacktest(self) -> Backtest:
        logging.debug(f'{self.runID} - start Backtesting...')
        return Backtest(
            data = self.data,
            strategy = MinMaxSlopePattern,
            cash = self.params['Portfolio']['Equity'],
            margin = 1 / self.params['Portfolio']['Leverage'],
            commission = self.params['Portfolio']['Commision']
        )
    
    @lru_cache(maxsize = None)
    def blackBoxFunction(self, **params: dict) -> any:
        saveOptimiezdParamsToJson(params)
        
        backtest = self.loadBacktest()

        stats = backtest.run()

        maxValue = float(stats[self.params['Optimizer']['maximize']])

        # Optimizer shit, not apart of the function calculation
        if (self.max == None) or (self.max <= maxValue):
            self.max = maxValue
            self.backtestResults = backtest._results
            self.closedTrades = stats['_trades']

        return maxValue
        
    def quickSave(self) -> None:
        logging.debug(f'{self.runID} - quick saving...')

        with open(f'output/{self.runID}/StrategyParameters.json', 'w') as w:
            w.write(json.dumps(self.params))
            w.close()
            logging.debug(f'{self.runID} - saved Best Strategy Params in: output/{self.runID}/StrategyParameters.json')

        with open(f'output/{self.runID}/backtestResults.txt', 'w') as w:
            w.write(str(self.backtestResults))
            w.close()
            logging.debug(f'{self.runID} - saved Best Strategy Results in: output/{self.runID}/backtestResults.txt')

        with open(f'output/{self.runID}/TradeResults.txt', 'w') as w:
            w.write(self.closedTrades.to_string())
            w.close()
            logging.debug(f'{self.runID} - saved Best Strategy Trade Results in: output/{self.runID}/TradeResults.txt')

        savePatterns(
            self.runID,
            self.data,
            self.closedTrades,
            self.params['Strategy']['Params']
        )

        logging.debug(f'{self.runID} - done quick saving')

    def __init__(self, params: dict, runID: str) -> None:
        super().__init__()

        self.params = params
        self.runID = runID

        self.max = None

        self.backtestResults = None
        self.closedTrades = None

        logging.debug(f'initilzed optimizer, ID: {runID}')
        logging.debug(f'optimizer params: {self.params}')

        self.data = self.loadData()

    def start(self) -> None:
        logging.debug(f'{self.runID} - starting optimization')
        optimizer = BayesianOptimization(
            f = self.blackBoxFunction,
            pbounds = self.loadBounds(),
            verbose = 2,
            allow_duplicate_points = True
        )

        if 'loadFrom' in self.params['Optimizer']:
            load_logs(new_optimizer, logs = self.params['Optimizer']['loadFrom'])
            logging.debug(f'{self.runID} - loaded progress from {self.params["Optimizer"]["loadFrom"]}')

        optimizer.subscribe(Events.OPTIMIZATION_STEP, JSONLogger(path=f'output/{self.runID}/progress'))

        logging.debug(f'{self.runID} - optimizer subscribed to path: output/{self.runID}/progress')

        optimizer.set_gp_params(alpha = 1e-3)

        logging.debug(f'{self.runID} - optimizer GP params are: alpha 1e-3')

        optimizer.maximize(
            init_points = self.params['Optimizer']['initPoints'],
            n_iter = self.params['Optimizer']['nIter']
        )

        logging.debug(f'{self.runID} - done optimizing')

        maxParams = optimizer.max

        logging.debug(f'{self.runID} - max params: {maxParams}')

        logging.debug(f'{self.runID} - max results: {self.backtestResults}')

        logging.debug(f'{self.runID} - max trade resuts: {self.closedTrades}')

        self.params['Strategy']['Params'] = maxParams['params']
        self.quickSave()
import os
import json
import logging

from typing import Union

from threading import Thread

import numpy

import pandas as pd

from backtesting import Backtest

from bayes_opt import BayesianOptimization
from bayes_opt.logger import JSONLogger
from bayes_opt.event import Events
from bayes_opt.util import load_logs

from strategies.minMaxSlopePattern import MinMaxSlopePattern

from utils import getDatasets, getDataset, getConfig, getInternalDataset, getDatasetFromYahoo, saveOptimiezdParamsToJson, saveClosedTrades

class Optimizer(Thread):
    def loadData(self) -> Union[pd.DataFrame, dict[str, pd.DataFrame]]:
        data: Union[pd.DataFrame, dict[str, pd.DataFrame]] = None

        if 'yFinance' in self.params['Strategy']:
            data = getDatasetFromYahoo(
                self.params['Strategy']['yFinance']['pair'],
                self.params['Strategy']['yFinance']['period'],
                self.params['Strategy']['yFinance']['interval']
            )
        elif 'DatasetPath' in self.params['Strategy']:
            data = getInternalDataset(self.params['Strategy']['DatasetPath'])
        elif 'DatasetURL' in self.params['Strategy']:
            if os.path.exists('datasets/tmp') != True:
                os.mkdir('datasets/tmp')

            data = getDataset(
                self.params['Strategy']['DatasetURL'],
                'datasets/tmp/tmpDf.csv.gz'
            )
        else:
            data = getDatasets(
                self.params['Strategy']['Pair'],
                self.params['Strategy']['Timeframe'],
                self.params['Strategy']['Year']
            )

        return data

    def loadBounds(self) -> dict:
        bounds: dict = {}

        for e in self.params['Strategy']['Params']:
            if e == 'Source':
                continue
            
            bounds[e] = (
                self.params['Strategy']['Params'][e]['min'],
                self.params['Strategy']['Params'][e]['max']
            )

        return bounds
    
    def loadBacktest(self) -> Backtest:
        return Backtest(
            data = self.data,
            strategy = MinMaxSlopePattern,
            cash = self.params['Portfolio']['Equity'],
            margin = 1 / self.params['Portfolio']['Leverage'],
            commission = self.params['Portfolio']['Commision']
        )
    
    def blackBoxFunction(self, **params: dict) -> any:
        saveOptimiezdParamsToJson(params)
        
        self.bt = self.loadBacktest()
        
        stats = self.bt.run()

        m = self.params['Optimizer']['maximize'] 

        result: float = 0.0

        for e in m:
            try:
                if str(stats[e]) == 'nan':
                    continue
                result += float(stats[e])
            except Exception as e:
                logging.debug(f'{stats[e]} is not valid, exception: {e}')

        return result / len(m)

    def quickSave(self) -> None:
        self.data.to_csv(f'output/{self.runID}/DataFrame.csv')

        with open(f'output/{self.runID}/StrategyParameters.json', 'w') as w:
            w.write(json.dumps(self.params))
            w.close()

        saveClosedTrades(
            self.runID,
            self.bt._strategy.closed_trades,
            self.data,
            self.params
        )

    def __init__(self, params: dict, runID: str) -> None:
        super().__init__()

        self.params = params
        self.runID = runID

        if os.path.exists(f'output/{runID}') != True:
            os.mkdir(f'output/{runID}')

        self.data = self.loadData()

    def start(self) -> None:
        optimizer = BayesianOptimization(
            f = self.blackBoxFunction,
            pbounds = self.loadBounds(),
            verbose = 2,
            allow_duplicate_points = True
        )

        if 'loadFrom' in self.params['Optimizer']:
            load_logs(new_optimizer, logs = self.params['Optimizer']['loadFrom']);

        optimizer.subscribe(Events.OPTIMIZATION_STEP, JSONLogger(path=f'output/{self.runID}.log'))

        optimizer.set_gp_params(alpha = 1e-3)

        optimizer.maximize(
            init_points = self.params['Optimizer']['initPoints'],
            n_iter = self.params['Optimizer']['nIter']
        )

        maxParams = optimizer.max

        logging.debug(maxParams)

        self.params['Strategy']['Params'] = maxParams['params']
        self.quickSave()
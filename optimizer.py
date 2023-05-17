import os
import pandas as pd

import numpy

from typing import Union

from threading import Thread

from backtesting import Backtest

#from strategy import daStrategy
from strategies.minMaxSlopePattern import MinMaxSlopePattern

from utils import getDatasets, getDataset, getConfig, getInternalDataset, getDatasetFromYahoo, saveOptimiezdParamsToJson

from bayes_opt import BayesianOptimization

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

                if stats[e] < 0:
                    result -= float(stats[e]) * 4
                else:            
                    result += float(stats[e])
            except Exception as e:
                print(f'{stats[e]} is not valid')

        return result / len(m)

    def __init__(self, params: dict) -> None:
        super().__init__()

        self.params = params

        self.data = self.loadData()

    def start(self) -> None:
        optimizer = BayesianOptimization(
            f = self.blackBoxFunction,
            pbounds = self.loadBounds(),
            verbose = 2,
            allow_duplicate_points = True
        )

        #from bayes_opt import UtilityFunction
        #utility = UtilityFunction(kind = 'ucb', kappa = 2.5, xi = 0.0)

        optimizer.set_gp_params(alpha = 1e-3)

        optimizer.maximize(
            init_points = self.params['Optimizer']['initPoints'],
            n_iter = self.params['Optimizer']['nIter']
        )

        max = optimizer.max

        print(max)

        if max['target'] <= 0:
            self.start()

        from backtester import run

        self.params['Strategy']['Params'] = max['params']
        
        p = self.params

        run(p)

        #for i, res in enumerate(optimizer.res):
        #    print("Iteration {}: \n\t{}".format(i, res))

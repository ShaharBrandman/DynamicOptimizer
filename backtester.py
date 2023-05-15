import os
import pandas as pd

from typing import Union

from threading import Thread

from backtesting import Backtest

#from strategy import daStrategy
from strategies.minMaxSlopePattern import MinMaxSlopePattern

from utils import getDatasets, getDataset, getConfig, getInternalDataset, saveOptimiezdParamsToJson

class Backtester(Thread):
    def loadBacktest(self) -> Backtest:
        return Backtest(
            data = self.data,
            strategy = MinMaxSlopePattern,
            cash = self.params['Portfolio']['Equity'],
            margin = 1 / self.params['Portfolio']['Leverage'],
            commission = self.params['Portfolio']['Commision']
        )

    def loadData(self) -> Union[pd.DataFrame, dict[str, pd.DataFrame]]:
        data: Union[pd.DataFrame, dict[str, pd.DataFrame]] = None

        if 'DatasetPath' in self.params['Strategy']:
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

    def __init__(self, params: dict) -> None:
        super().__init__()

        self.params = params

        self.params['Strategy']['Params'] = {
            "Source": 'Close',
            "TAKE_PROFIT_PER": 1.5,
            "STOP_LOSS_PER": 0.85,
            "PIVOT_LENGTH": 3,
            "BACK_CANDLES": 20,
            "R_MIN_LONG": 0.9,
            "R_MAX_LONG": 0.9,
            "R_MIN_SHORT": -0.9,
            "R_MAX_SHORT": -0.9,
            "SL_MIN_LONG": 0.001,
            "SL_MAX_LONG": 0.001,
            "SL_MIN_SHORT": -0.0001,
            "SL_MAX_SHORT": -0.0001
        }
        
        self.data = self.loadData()

    def start(self) -> None:
        saveOptimiezdParamsToJson(self.params['Strategy']['Params'])

        self.bt = self.loadBacktest()
        
        stats = self.bt.run()

        self.bt.plot()

        print(stats)

from utils import getRunJson

if os.path.exists('datasets') != True:
    os.mkdir('datasets')

if os.path.exists('tmp') != True:
    os.mkdir('tmp')

o = Backtester(getRunJson())
o.start()
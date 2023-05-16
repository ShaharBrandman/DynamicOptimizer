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
            "TAKE_PROFIT_PER": 1.446447586383931,
            "STOP_LOSS_PER": 4.4251353319491855,
            "PIVOT_LENGTH": 4.297145731278758,
            "BACK_CANDLES": 35.5843502127593,
            "R_MIN_LONG": 0.5942546426663565,
            "R_MAX_LONG": 0.11776539845298459,
            "R_MIN_SHORT": -0.4205391033511241,
            "R_MAX_SHORT": 0.7973783984383424,
            "SL_MIN_LONG": 0.0005362551401242417,
            "SL_MAX_LONG": 0.0008462531080675778,
            "SL_MIN_SHORT": 0.008960442623547402,
            "SL_MAX_SHORT": 0.0009449977347971846
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
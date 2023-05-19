import os
import logging
import pandas as pd

from typing import Union

from threading import Thread

from backtesting import Backtest

from strategies.minMaxSlopePattern import MinMaxSlopePattern

from utils import getDatasets, getDataset, getConfig, getInternalDataset, getDatasetFromYahoo, saveOptimiezdParamsToJson, getRunJson

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

    def __init__(self, params: dict) -> None:
        super().__init__()
        
        self.params = params

        self.data = self.loadData()

    def start(self) -> None:
        saveOptimiezdParamsToJson(self.params['Strategy']['Params'])

        self.bt = self.loadBacktest()
        
        stats = self.bt.run()

        self.bt.plot()

        logging.debug(stats)

def runBacktest(params: dict) -> None:
    o = Backtester(params)
    o.start()

if __name__ == '__main__':
    runBacktest(getRunJson())
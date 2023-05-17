import os
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

        '''self.params['Strategy']['Params'] = {
            'BACK_CANDLES': 33.468569464667276,
            'PIVOT_LENGTH': 1.524624596094434,
            'R_MAX_LONG': 0.32244024985967457,
            'R_MAX_SHORT': -0.0060000986784292335,
            'R_MIN_LONG': 0.4989715648568345,
            'R_MIN_SHORT': 0.9345467095632859,
            'SL_MAX_LONG': 0.2909353737175032,
            'SL_MAX_SHORT': 0.6616227784219257,
            'SL_MIN_LONG': 0.34289550105287264,
            'SL_MIN_SHORT': 0.5754348321299666,
            'STOP_LOSS_PER': 4.3626871550212805,
            'TAKE_PROFIT_PER': 1.6889425683640362
        }'''

        self.data = self.loadData()

    def start(self) -> None:
        saveOptimiezdParamsToJson(self.params['Strategy']['Params'])

        self.bt = self.loadBacktest()
        
        stats = self.bt.run()

        self.bt.plot()

        print(stats)

def run(params: dict) -> None:
    if os.path.exists('datasets') != True:
        os.mkdir('datasets')

    if os.path.exists('tmp') != True:
        os.mkdir('tmp')

    o = Backtester(params)
    o.start()

if __name__ == '__main__':
    run(getRunJson())
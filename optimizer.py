import os
import pandas as pd

from typing import Union

from threading import Thread

from backtesting import Backtest

from strategy import daStrategy

from utils import getDatasets, getDataset, getConfig, getInternalDataset

from bybitHTTPX import BybitClient

class Optimizer(Thread):
    def __init__(self, params: dict) -> None:
        c = getConfig()

        '''self.client = BybitClient(
            url = c['bybitEndpoint'],
            apiKey = c['bybitAPIKey'],
            apiSecret = c['bybitAPISecretKey']
        )'''

        self.params = params

    def start(self) -> None:
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

        if type(data) == pd.DataFrame:
            bt = Backtest(
                data,
                daStrategy,
                cash = self.params['Portfolio']['Equity'],
                margin = 1 / self.params['Portfolio']['Leverage'],
                commission = self.params['Portfolio']['Commision']
            )

            stat = bt.run()
        
            print(stat)

            #bt.plot()
        else:
            for d in data:
                bt = Backtest(
                    data[d],
                    daStrategy,
                    cash = self.params['Portfolio']['Equity'],
                    margin = 1 / self.params['Portfolio']['Leverage'],
                    commission = self.params['Portfolio']['Commision']
                )

                stat = bt.run()
        
                print(stat)

                #bt.plot()

                a = input('[y/N]?')
                if a.lower() == 'y':
                    continue
                else:
                    break
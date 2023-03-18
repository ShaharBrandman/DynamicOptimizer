import logging
import time
import requests
import json

import pandas as pd

from datetime import datetime
from datetime import timedelta

from pybit import usdt_perpetual
from pybit import exceptions

from strategy import Strategy

def getData(pair: str, timeframe: str, limit: int, client: usdt_perpetual.HTTP) -> pd.DataFrame:
    postMin = 0
    data = None

    while postMin <= limit:
        t = datetime.now() - timedelta(minutes = (limit - postMin) * timeframe)

        while True:
            try:
                tmp = client.query_kline(
                    symbol = pair,
                    interval = timeframe,
                    from_time = int(t.timestamp())
                )
                break
            except requests.exceptions.ConnectionError as e:
                logging.debug(f'{pair} ConnectionError fetching data: {e}')
                time.sleep(1)
                continue
            except requests.exceptions.RequestException as e:
                logging.debug(f'{pair} RequestException fetching data: {e}')
                time.sleep(1)
                continue
            except requests.exceptions.ReadTimeout as e:
                logging.debug(f'{pair} ReadTimeout fetching data: {e}')
                time.sleep(1)
                continue


        tmp = pd.DataFrame(
            tmp['result'],
            columns = (
                'symbol',
                'interval', 
                'open_time', 
                'open',
                'high', 
                'low', 
                'close', 
                'volume', 
                'turnover'
            )
        ).drop(columns= ['symbol'])

        if data is None:
            data = tmp
        else:
            data = pd.concat([data, tmp], ignore_index = True)

        postMin+= 200
        #time.sleep(0.1)

    return data

def getConfig() -> any:
    with open('config.json', 'r') as f:
        f.read(json.loads(r))

def validatePair(pair: str) -> None:
    pass

def validateTimeframe(timeframe: str) -> None:
    pass

def validateStrategy(strat: str) -> None:
    pass

def validateLoops(loops: str) -> None:
    pass

def validateDataset(dataset: str) -> None:
    pass

def getStrategy(name: str) -> Strategy:
    pass

def validateSrc(src: str) -> None:
    pass

def getClosedPosition(leverage: int, position: dict, ExitPrice: float) -> dict:
    pass
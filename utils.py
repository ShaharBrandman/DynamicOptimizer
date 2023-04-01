import json
import logging
import time
import requests

from datetime import datetime
from datetime import timedelta

from pybit import usdt_perpetual

import pandas as pd

from exceptions import StrategyNotExists

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

def getRunJson() -> dict:
    return json.loads(open('run.json', 'r').read())

def getClosedPosition(leverage: int, position: dict, ExitPrice: float) -> dict:
    PNL = 0.0
    if position['Type'] == 'Long':
        PNL = ((ExitPrice * 100) / position['Entry']) - 100
    else:
        PNL = 100 - ((ExitPrice * 100) / position['Entry'])

    PNL *= leverage

    return {
        'ID': position['ID'],
        'State': 'CLOSED',
        'Type': position['Type'],
        'PNL': PNL,
        'Entry': position['Entry'],
        'Exit': ExitPrice
    }

def getConfig() -> dict:
    return json.loads(open('config.json', 'r').read())

def getStrategyByInput(input: str) -> any:
    #moved it here because this cause a circular import error
    from strategies import Strategies

    if input not in Strategies:
        raise StrategyNotExists(f'{input} doesnot exists!')
    
    return Strategies[input]

def getStrategyParamsByInput(input: str) -> dict:
    return json.loads(open('strategies.json', 'r').read())[input]
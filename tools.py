import logging
import time
import requests
import json
import os
import random

import pandas as pd

from datetime import datetime
from datetime import timedelta

from pybit import usdt_perpetual

from strategy import Strategy
from strategies import Strategies

from exceptions import *

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

def getConfig() -> dict:
    return json.loads(open('config.json', 'r').read())

def validateDataset(pathToDataset: str) -> pd.DataFrame:
    if pathToDataset is None:
        raise InvalidDataset('Path to dataset cannot be None')

    if os.path.exists(pathToDataset):
        data = pd.read_csv(pathToDataset)
        
        if data is None:
            raise InvalidDataset(f'data from {pathToDataset} cannot be None')

    else:
        raise InvalidDataset('Path to dataset doesnt exists')

    columns = [
        'symbol',
        'interval', 
        'open_time', 
        'open',
        'high', 
        'low', 
        'close', 
        'volume', 
        'turnover'
    ]

    if columns not in data:
        raise InvalidDataset(f'Dataset must include the colums: {columns}')
    
    return data

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

def getStrategyByInput(input: str) -> Strategy:
    if input not in Strategies:
        raise StrategyNotExists(f'{input} doesnot exists!')
    
    return Strategies[input]

def getRunJson() -> dict:
    return json.loads(open('run.json', 'r').read())

def randomizeParams(paramsToRandomize: dict) -> dict:
    for i in range(len(paramsToRandomize)):
        if type(paramsToRandomize[i]) == str:
            s = ['close', 'open', 'high', 'low']
            r = random.randint(0, len(s))

            paramsToRandomize[i] = s[r]
        elif type(paramsToRandomize[i]) == 'float':
            r = random.randrange(0.0, 100.0)
            paramsToRandomize[i] = r
        elif type(paramsToRandomize[i]) == 'int':
            r = random.randint(0, 100)
            paramsToRandomize[i] = r
        elif type(paramsToRandomize[i]) == 'bool':
            s = [True, False]
            r = random.randint(0, 1)

            paramsToRandomize[i] = s[r]
        elif type(paramsToRandomize[i]) == 'dict':
            paramsToRandomize[i] = randomizeParams[paramsToRandomize[i]]

    return paramsToRandomize

def getStrategyParamsByInput(input: str) -> dict:
    return json.loads(open('strategies.json', 'r').read())[input]

def validateParams(self: Strategy, params: dict) -> None:
    for e in Strategies:
        if e is self:
            sParams = getStrategyParamsByInput(e.__class__.__name__)

            for j in sParams:
                if j not in params:
                    raise InvalidParams(f'{j} Parameter is not in params')
                
    raise InvalidParams(f'{self} is not in Strategies.py')

def validatePortfolio(portfolio: dict) -> None:
    if 'Equity' in portfolio:
        if portfolio['Equity'] <= 0:
            raise InvalidPortoflio('Portfolio Equity cannot be less or equal to 0')
    else:
        raise InvalidPortoflio('Portfolio doesnt have Equity attribute')
    
    if 'Leverage' in portfolio:
        if portfolio['Leverage'] < 0:
            raise InvalidPortoflio('Portfolio Leverage cannot be less then 0, (can be 0 tho)')
    
    if 'Commision' in portfolio:
        if portfolio['Commision'] < 0:
            raise InvalidPortoflio('Portfolio Commission cannot be less then 0')
        
    if 'PercentPerPosition' in portfolio:
        if portfolio['PercentPerPosition'] <= 0:
            raise InvalidPortoflio('PercentPerPosition cannot be less or equal to 0 brother')
    else:
        raise InvalidPortoflio('Portfolio doesnt have PercentPerPosition attribute')
        
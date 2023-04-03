import os
import random

import pandas as pd

from exceptions import *

from utils import getStrategyParamsByInput

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

def randomizeParams(paramsToRandomize: dict) -> dict:
    for e in paramsToRandomize:
        if e == 'Source':
            s = ['close', 'open', 'high', 'low']
            r = random.randint(0, len(s) - 1)
            
            paramsToRandomize[e] = s[r]
        elif e == 'TPSL':
            randomizeParams(paramsToRandomize['TPSL'])
        elif e == 'StopLoss':
            r = random.uniform(0.1, 2.5)
            paramsToRandomize[e] = r
        elif type(paramsToRandomize[e]) == float:
            r = random.uniform(0.0, 100.0)
            paramsToRandomize[e] = r
        elif type(paramsToRandomize[e]) == int:
            r = random.randint(0, 100)
            paramsToRandomize[e] = r
        elif type(paramsToRandomize[e]) == bool:
            s = [True, False]
            r = random.randint(0, 1)

            paramsToRandomize[e] = s[r]

    return paramsToRandomize

def validateParams(strat: any, params: dict) -> None:
    sParams = getStrategyParamsByInput(strat)
    for e in sParams:
        if e not in params:
            raise InvalidParams(f'{e} Parameter is not in params')

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
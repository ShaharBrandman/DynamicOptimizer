import os
import random

import pandas as pd

from exceptions import *

from strategies import Strategies

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

def validateParams(self: any, params: dict) -> None:
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
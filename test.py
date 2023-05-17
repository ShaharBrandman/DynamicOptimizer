import os

import numpy as np

import pandas as pd

from matplotlib import pyplot
from scipy.stats import linregress

from scipy import stats

from utils import getInternalDataset, getRunJson

import plotly.graph_objects as go

from datetime import datetime

#from utils import getDatasetFromYahoo

from typing import Optional

import yfinance as yf

def getDatasetFromYahoo(pair: str, period: str, interval: str, start: Optional[str] = None, end: Optional[str] = None) -> pd.DataFrame:
    if os.path.exists(f'datasets/{pair}') != True:
        os.mkdir(f'datasets/{pair}')

    try:
        data = pd.DataFrame(yf.download(
            tickers = pair, 
            period = period,
            interval = interval,
            start = start,
            end = end
        ))
    except yf.exceptions.YFinanceDataException as e:
        print(f'first error: {e}')
    except yf.exceptions.YFinanceException as e:
        print(f'second error: {e}')

    data = data[data['Volume'] != 0]
    
    data.reset_index(drop = True, inplace = True)
    
    data.isna().sum()

    return data

d = getDatasetFromYahoo('AAPL', '2y', '1d')
print(d)
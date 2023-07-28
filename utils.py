import os
import json
import time
import logging

import pandas as pd
import numpy as np
import yfinance as yf
import plotly.graph_objects as go

from datetime import datetime

from typing import Union, Optional

from strategies.analysis import getLinearRegression, getPivotPoint, pointPivotPosition, findInBoundsPatterns

from scipy.stats import linregress

'''
depracted features

def getRunJson() -> dict:
    return json.loads(open('jsonFiles/run.json', 'r').read())

def getConfig() -> dict:
    return json.loads(open('jsonFiles/config.json', 'r').read())
'''
def getOptimizedParams() -> dict:
    return json.loads(open('tmp/optimizedParams.json', 'r').read())

def saveOptimiezdParamsToJson(oParams: dict) -> None:
    with open('tmp/optimizedParams.json', 'w') as f:
        f.write(json.dumps(oParams))
        f.flush()
        f.close()

def getDatasetFromYahoo(pair: str, period: str, interval: str) -> pd.DataFrame:
    try:
        data = pd.DataFrame(yf.download(
            tickers = pair, 
            period = period,
            interval = interval
        ))
    except yf.exceptions.YFinanceDataException as e:
        logging.debug(f'first error: {e}')
    except yf.exceptions.YFinanceException as e:
        logging.debug(f'second error: {e}')

    data = data[data['Volume'] != 0]
    
    data.reset_index(drop = True, inplace = True)
    
    data.isna().sum()

    return data

def fetchAndAppend(data: pd.DataFrame, pair: str, timeframe: str, path: str, datasets: list) -> None:
    for e in datasets:
        if e.__contains__(f'{pair}_{timeframe}'):
            data[str(e).replace('.csv.gz', '')] = getDataset(path + e, f'datasets/{pair}/{e}')
    
def getDataset(url: str) -> pd.DataFrame:
    return pd.read_csv(
        url,
        names = [
            'datetime',
            'Open',
            'High',
            'Low',
            'Close',
            'Volume'
        ],
        compression = 'gzip',
        index_col = 'datetime',
        parse_dates= True
    ).astype('float')

def getInternalDataset(path: str, compression: Optional[str] = None) -> pd.DataFrame:
    '''
    commonly used to import static files
    '''
    data: pd.DataFrame = None
    
    if compression != None:
        data = pd.read_csv(
            path,
            compression = compression,
            #index_col = 'Gmt time',
            #parse_dates= True
        )
    else:
        data =  pd.read_csv(path)

    df = pd.DataFrame()

    df['Open'] = data['open']
    df['High'] = data['high']
    df['Low'] = data['low']
    df['Close'] = data['close']
    df['Volume'] = data['volume']

    df['datetime'] = data['Gmt time']
    
    df['datetime'] = df.apply(
        lambda x: datetime.strptime(
            df['datetime'][x.name] ,
            "%d.%m.%Y %H:%M:%S.%f"
        ).timestamp(), 
        axis = 1
    )

    df = df[df['Volume'] != 0]
    
    df.reset_index(drop = True, inplace = True)
    
    df.isna().sum()
    
    return df

def saveGraphByIndex(runID: str, index: int, backCandles: int, previewNum: int, df: pd.DataFrame) -> None:
    slmin, intercmin, rmin, pmin, semin = df['Patterns'][index]['minSlope']
    slmax, intercmax, rmax, pmax, semax = df['Patterns'][index]['maxSlope']

    minSlopeIndex = df['Patterns'][index]['minSlopeIndex']
    maxSlopeIndex = df['Patterns'][index]['maxSlopeIndex']

    dfpl = df[index-backCandles-previewNum:index+backCandles+previewNum]

    fig = go.Figure(data=[go.Candlestick(x=dfpl.index,
                    open=dfpl['Open'],
                    high=dfpl['High'],
                    low=dfpl['Low'],
                    close=dfpl['Close'])])

    fig.add_scatter(x=dfpl.index, y=dfpl['pointpos'], mode="markers",
                    marker=dict(size=4, color="MediumPurple"),
                    name="pivot")

    #-------------------------------------------------------------------------
    # Fitting intercepts to meet highest or lowest candle point in time slice
    #adjintercmin = df.low.loc[candleid-backcandles:candleid].min() - slmin*df.low.iloc[candleid-backcandles:candleid].idxmin()
    #adjintercmax = df.high.loc[candleid-backcandles:candleid].max() - slmax*df.high.iloc[candleid-backcandles:candleid].idxmax()

    minSlopeIndex = np.append(minSlopeIndex, minSlopeIndex[-1]+15)
    maxSlopeIndex = np.append(maxSlopeIndex, maxSlopeIndex[-1]+15)
    #fig.add_trace(go.Scatter(x=xxmin, y=slmin*xxmin + adjintercmin, mode='lines', name='min slope'))
    #fig.add_trace(go.Scatter(x=xxmax, y=slmax*xxmax + adjintercmax, mode='lines', name='max slope'))

    fig.add_trace(go.Scatter(x=minSlopeIndex, y=slmin*minSlopeIndex + intercmin, mode='lines', name='min slope'))
    fig.add_trace(go.Scatter(x=maxSlopeIndex, y=slmax*maxSlopeIndex + intercmax, mode='lines', name='max slope'))
    fig.update_layout(xaxis_rangeslider_visible=False)

    if os.path.exists(f'output/{runID}/graphs/{index}') != True:
        os.mkdir(f'output/{runID}/graphs/{index}')

    fig.write_image(f'output/{runID}/graphs/{index}/Graph.png')
    dfpl.to_csv(f'output/{runID}/graphs/{index}/DataFrame.csv')

def savePatterns(runID: str, closedTrades: list, df: pd.DataFrame, params: dict, show: Optional[bool] = False) -> None:
    logging.debug(f'{runID} - start recalucating patterns')

    for e in closedTrades:
        print(e)

    df['pivot'] = df.apply( 
        lambda row: getPivotPoint(
            df,
            row.name,
            int(params['PIVOT_LENGTH']),
            int(params['PIVOT_LENGTH'])
        ), 
        axis = 1
    )

    df['pointpos'] = df.apply(
        lambda row: pointPivotPosition(row),
        axis = 1
    )

    df['Patterns'] = getLinearRegression(df, int(params['BACK_CANDLES']))

    logging.debug(f'{runID} - done calculating patterns')

    for i in range(len(df['Patterns'])):
        if i in closedTrades:
            saveGraphByIndex(
                runID,
                i,
                10,
                20,
                df
            )
    
    df.to_csv(f'output/{runID}/Dataset.csv') 

    logging.debug(f'{runID} - saved trades in: output/{runID}/Dataset.csv')





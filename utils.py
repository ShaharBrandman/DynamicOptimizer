import os
import json
import time
import logging

import pandas as pd
import yfinance as yf
import plotly.graph_objects as go

from datetime import datetime

from typing import Union, Optional

import pandas as pd

from bybitHTTPX import historicDB

from strategies.analysis import getLinearRegression, getPivotPoint

def getRunJson() -> dict:
    return json.loads(open('jsonFiles/run.json', 'r').read())

def getConfig() -> dict:
    return json.loads(open('jsonFiles/config.json', 'r').read())

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

def getDatasets(pair: str, timeframe: Union[str, list[str]], years: Optional[Union[int, list[int]]] = None) -> dict[str, pd.DataFrame]:
    if os.path.exists(f'datasets/{pair}') != True:
        os.mkdir(f'datasets/{pair}')

    hdb = historicDB()
    path = hdb.KLINE_FOR_METATRADER4 + pair + '/'
    data: dict = {}

    if type(timeframe) == list:
        for t in timeframe:
            if years != None:
                if type(years) == int:
                    fetchAndAppend(data, pair, t, path + f'{year}/', hdb.getKeyItems(path + f'{year}/'))
                else:
                    for year in years:
                        fetchAndAppend(data, pair, t, path + f'{year}/', hdb.getKeyItems(path + f'{year}/'))

            else:
                years = hdb.getKeyItems(path)
                for year in years:
                    fetchAndAppend(data, pair, t, path + f'{year}/', hdb.getKeyItems(path + f'{year}/'))
    else:
        if years != None:
            if type(years) == int:
                fetchAndAppend(data, pair, timeframe, path + f'{year}/', hdb.getKeyItems(path + f'{year}/'))
            else:
                for year in years:
                    fetchAndAppend(data, pair, timeframe, path + f'{year}/', hdb.getKeyItems(path + f'{year}/'))
        else:
            years = hdb.getKeyItems(path)
            for year in years:
                fetchAndAppend(data, pair, timeframe, path + f'{year}/', hdb.getKeyItems(path + f'{year}/'))
    return data

def fetchAndAppend(data: pd.DataFrame, pair: str, timeframe: str, path: str, datasets: list) -> None:
    for e in datasets:
        if e.__contains__(f'{pair}_{timeframe}'):
            data[str(e).replace('.csv.gz', '')] = getDataset(path + e, f'datasets/{pair}/{e}')
    
def getDataset(url: str, pathToFile: str) -> pd.DataFrame:
    hdb = historicDB()
    hdb.getItem(url, pathToFile)
    return pd.read_csv(
        pathToFile,
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

def saveAndPlot(runID: str, index: int, df: pd.DataFrame) -> None:
    fig = go.Figure(
        data = [
            go.Candlestick(
                x=df.index,
                open=df['Open'],
                high=df['High'],
                low=df['Low'],
                close=df['Close']
            )
        ]
    )

    fig.add_scatter(
        x=df.index,
        y=df['pointpos'], 
        mode="markers",
        marker = dict(
            size=4,
            color="MediumPurple"
        ),
        name="pivot"
    )

    df['minSlopeIndex'] = np.append(df['minSlopeIndex'], df['minSlopeIndex'][-1]+15)
    df['maxSlopeIndex'] = np.append(df['maxSlopeIndex'], df['maxSlopeIndex'][-1]+15)
    
    slmin, intercmin = df['minSlope']
    slmax, intercmax = df['maxSlope']


    fig.add_trace(
        go.Scatter(
            x = df['minSlopeIndex'],
            y = slmin * df['minSlopeIndex'] + intercmin,
            mode='lines',
            name='min slope'
        )
    )

    fig.add_trace(
        go.Scatter(
            x = df['maxSlopeIndex'],
            y = slmax * df['maxSlopeIndex'] + intercmax,
            mode='lines',
            name='max slope'
        )
    )
    
    fig.update_layout(xaxis_rangeslider_visible=False)

    fig.to_image(f'output/{runID}/{index}/Graph.png')

def saveClosedTrades(runID: str, closedTrades: list, df: pd.DataFrame, params: dict) -> None:
    df['pivot'] = df.apply( 
        lambda row: getPivotPoint(
            df,
            row.name,
            params['PIVOT_LENGTH'],
            params['PIVOT_LENGTH']
        ), 
        axis = 1
    )

    df['pointpos'] = df.apply(
        lambda row: pointPivotPosition(row),
        axis = 1
    )

    patterns = getLinearRegression(df, params['BACK_CANDLES'])

    for i in range(len(patterns)):
        if i in closedTrades:
            tmp = pd.DataFrame(
                patterns[i]['minSlope'],
                patterns[i]['maxSlope'],
                patterns[i]['minSlopeArr'],
                patterns[i]['maxSlopeArr'],
                patterns[i]['minSlopeIndex'],
                patterns[i]['maxSlopeIndex']
            )

            tmp = pd.concat(tmp, df[i - params['BACK_CANDLES']: i + 1], axis = 1)

            saveAndPlot(runID, i, tmp)

            tmp.save_csv(f'output/{runID}/{i}/DataFrame.csv')

    #inBonudsPattern = findInBoundsPatterns(df, params)
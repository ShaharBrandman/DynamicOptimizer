import os
import json

from typing import Union, Optional

import pandas as pd

from bybitHTTPX import historicDB

def getRunJson() -> dict:
    return json.loads(open('jsonFiles/run.json', 'r').read())

def getConfig() -> dict:
    return json.loads(open('jsonFiles/config.json', 'r').read())

def getDatasets(pair: str, timeframe: Union[str, list[str]], year: Optional[Union[int, list[int]]] = None) -> dict[str, pd.DataFrame]:
    if os.path.exists(f'datasets/{pair}') != True:
        os.mkdir(f'datasets/{pair}')

    hdb = historicDB()
    path = hdb.KLINE_FOR_METATRADER4 + pair + '/'
    data: dict = {}

    if type(timeframe) == list:
        for t in timeframe:
            if year != None:
                if type(year) == int:
                    path = path + f'{year}/'
                    fetchAndDecompress(data, pair, t, path, hdb.getKeyItems(path), hdb)
                else:
                    for y in year:
                        fetchAndDecompress(data, pair, t, path, hdb.getKeyItems(path + y), hdb)

            else:
                years = hdb.getKeyItems(path)
                for year in years:
                    fetchAndDecompress(data, pair, t, path, hdb.getKeyItems(path + year), hdb)
    else:
        if year != None:
            if type(year) == int:
                path = path + f'{year}/'
                fetchAndDecompress(data, pair, timeframe, path, hdb.getKeyItems(path), hdb)
            else:
                for y in year:
                    fetchAndDecompress(data, pair, timeframe, path, hdb.getKeyItems(path + y), hdb)
        else:
            years = hdb.getKeyItems(path)
            for year in years:
                fetchAndDecompress(data, pair, timeframe, path, hdb.getKeyItems(path + year), hdb)
    return data

def fetchAndDecompress(data: pd.DataFrame, pair: str, timeframe: str, path: str, datasets: list, hdb: historicDB) -> None:
    for e in datasets:
        if str(e).__contains__(f'{pair}_{timeframe}'):
            data[str(e).replace('.csv.gz', '')] = getDataset(path + e, f'datasets/{pair}/{str(e)}', hdb)
    
def getDataset(url: str, pathToFile: str, hdb: historicDB) -> pd.DataFrame:
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
        compression = 'gzip'
    )

def plotData(data: pd.DataFrame) -> None:
    import plotly.graph_objects as go
    from plotly.subplots import make_subplots

    fig = go.Figure(
        data = [go.Candlestick(
            x = data.index,
            open = data['Open'],
            high = data['High'],
            low = data['Low'],
            close = data['Close']
        )]
    )

    fig.update_layout(
        autosize = False,
        width = 600,
        margin = dict(
            l = 50,
            r = 50,
            b = 100,
            pad = 4
        ),
        paper_bgcolor = 'white'
    )
    fig.show()



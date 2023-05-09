import os
import json

from typing import Union, Optional

import pandas as pd

from bybitHTTPX import historicDB

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
    )

def getInternalDataset(path: str) -> pd.DataFrame:
    return pd.read_csv(
        path,
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
    )





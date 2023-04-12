import json
import time
import logging
import requests

import pandas as pd

from datetime import datetime, timedelta

from pybit import usdt_perpetual

def getRunJson() -> dict:
    return json.loads(open('jsonFiles/run.json', 'r').read())

def getConfig() -> dict:
    return json.loads(open('jsonFiles/config.json', 'r').read())

def getData(pair: str, timeframe: int, limit: int, client: usdt_perpetual.HTTP) -> pd.DataFrame:
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




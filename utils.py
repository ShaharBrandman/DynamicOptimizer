import json
import time
import logging

import pandas as pd

from datetime import datetime, timedelta

from httpx import NetworkError

from bybitHTTPX import BybitClient

def getRunJson() -> dict:
    return json.loads(open('jsonFiles/run.json', 'r').read())

def getConfig() -> dict:
    return json.loads(open('jsonFiles/config.json', 'r').read())

def getData(pair: str, timeframe: str, limit: int, client: BybitClient) -> pd.DataFrame:
    candlesCounter = 0
    data = None

    dateNow = datetime.now()
    while candlesCounter < limit:
        #timeRange = datetime.now() - timedelta(minutes = (limit - candlesCounter) * timeframe)
        
        if timeframe.isdigit():
            timeRange = dateNow - timedelta(minutes = (limit - candlesCounter) * int(timeframe))
        elif timeframe == 'D':
            timeRange = dateNow - timedelta(days=  (limit - candlesCounter))
        elif timeframe == 'W':
            timeRange = dateNow - timedelta(weeks=  (limit - candlesCounter))
        elif timeframe == 'M':
            timeRange = dateNow - timedelta(weeks=  (limit - candlesCounter) * 4)

        while True:
            try:
                tmp = json.loads(client.getkLines(
                    category='inverse',
                    symbol = pair,
                    interval = timeframe,
                    fromTimestamp= timeRange,
                    limit = limit
                ).content)['result']['list']

                if limit - candlesCounter < 200:
                    tmp = tmp[:limit - candlesCounter]

                break
            
            except NetworkError as e:
                print(f'{pair} Exception fetching data: {e}, type of Exception: {type(e)}')
                logging.debug(f'{pair} Exception fetching data: {e}, type of Exception: {type(e)}')
                time.sleep(1)
                continue
        
        tmp = pd.DataFrame(
            tmp,
            columns = (
                'open_time',
                'Open', 
                'High', 
                'Low',
                'Close', 
                'Volume',
                'turnover'
            )
        )

        if data is None:
            data = tmp
        else:
            data = pd.concat([data, tmp], ignore_index = True)

        candlesCounter+= 200
        #time.sleep(0.1)

    return data



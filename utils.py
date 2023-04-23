import json
import time
import logging

import numpy 

import pandas as pd

from datetime import datetime, timedelta

from httpx import NetworkError

from bybitHTTPX import BybitClient

def getRunJson() -> dict:
    return json.loads(open('jsonFiles/run.json', 'r').read())

def getConfig() -> dict:
    return json.loads(open('jsonFiles/config.json', 'r').read())

def getData(pair: str, timeframe: str, candlesToRetrieve: int, client: BybitClient) -> pd.DataFrame:
    '''if timeframe.isdigit():
            timeRange = dateNow - timedelta(minutes = (limit - candlesCounter) * int(timeframe))
        elif timeframe == 'D':
            timeRange = dateNow - timedelta(days=  (limit - candlesCounter))
        elif timeframe == 'W':
            timeRange = dateNow - timedelta(weeks=  (limit - candlesCounter))
        elif timeframe == 'M':
            timeRange = dateNow - timedelta(weeks=  (limit - candlesCounter) * 4)'''

    data: pd.DataFrame = None
    candlesCounter: int = 0

    start: datetime = datetime.now()
    print(f'start: {start.astimezone()}')

    end = start - timedelta(minutes = int(timeframe) * candlesToRetrieve)
    print(f'end: {end.astimezone()}')

    #200 is the max length bybit can provide per request
    maxLength: int = 200

    while candlesCounter < candlesToRetrieve:
        #t = start - timedelta(minutes = int(timeframe) * (candlesToRetrieve - candlesCounter))
        #print(f'{candlesToRetrieve - candlesCounter} before start is: {t.astimezone()}')
        endTimestamp = start - timedelta(minutes = int(timeframe) * (candlesToRetrieve - candlesCounter))
        startTimestamp = endTimestamp + timedelta(minutes = int(timeframe) * maxLength)

        print(f'{candlesToRetrieve - candlesCounter} start is: {startTimestamp.astimezone()}')
        print(f'{candlesToRetrieve - candlesCounter} end is: {endTimestamp.astimezone()}')

        startTimestamp = int(startTimestamp.timestamp())
        endTimestamp = int(endTimestamp.timestamp())

        print(f'{candlesToRetrieve - candlesCounter} startTimestamp is: {startTimestamp}')
        print(f'{candlesToRetrieve - candlesCounter} endTimestamp is: {endTimestamp}')

        tmp: dict = None

        while True:
            try:
                from pybit.unified_trading import HTTP
                session = HTTP(testnet=True)

                '''tmp = client.getkLines(
                    category='inverse',
                    symbol = pair,
                    interval = timeframe,
                    #fromTimestamp = int(t.timestamp() / 10),
                    fromTimestamp = None,
                    startTimestamp = int(startTimestamp.timestamp()),
                    endTimestamp = int(endTimestamp.timestamp()),
                    limit = 200 if candlesToRetrieve - candlesCounter >= 200 else candlesToRetrieve - candlesCounter
                )'''

                tmp = session.get_kline(
                    category="inverse",
                    symbol = pair,
                    interval = timeframe,
                    start = startTimestamp,
                    end = endTimestamp,
                    limit = 200 if candlesToRetrieve - candlesCounter >= 200 else candlesToRetrieve - candlesCounter
                )['result']['list']

                #tmp = json.loads(tmp)['result']['list']

                break
            
            except NetworkError as e:
                print(f'{pair} Exception fetching data: {e}, type of Exception: {type(e)}')
                logging.debug(f'{pair} Exception fetching data: {e}, type of Exception: {type(e)}')
                time.sleep(1)
                continue

        tmp = pd.DataFrame(
            tmp,
            columns = [
                'datetime',
                'Open', 
                'High', 
                'Low',
                'Close', 
                'Volume',
                'turnover'
            ]
        )
        
        if tmp.index.empty:
            return print('client is returning Empty dataframes')

        if data is None:
            data = tmp
        else:
            data = pd.concat([data, tmp], ignore_index = True)

        dfStartDate = datetime.fromtimestamp(int(tmp['datetime'][0]) / 1000)
        dfEndDate = datetime.fromtimestamp(int(tmp['datetime'][len(tmp['datetime']) - 1]) / 1000)
        print(f'{candlesToRetrieve - candlesCounter}: startDate: {dfStartDate}')
        print(f'{candlesToRetrieve - candlesCounter}: endDate: {dfEndDate}')

        candlesCounter += maxLength

    return data


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



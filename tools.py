import pandas as pd

import plotly.graph_objects as go
from plotly.subplots import make_subplots

def plotData(data: pd.DataFrame) -> None:
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

def randomizeParams(params: dict) -> dict:
    pass

def isBetter(x: dict, y: dict) -> dict:
    '''
    mostProfitable = {
                    'Duration': bt[2],
                    'Return': bt[6],
                    'SharpeRatio': bt[10],
                    'MaxDrawdown': bt[13],
                    'Trades': bt[17],
                    'WinRate': bt[18],
                    'Profit Factor': bt[24]
                }
    '''
    pass
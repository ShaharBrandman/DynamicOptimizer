import pandas as pd

import plotly.graph_objects as go

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
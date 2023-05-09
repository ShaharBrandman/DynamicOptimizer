import numpy

import pandas as pd

from matplotlib import pyplot
from scipy.stats import linregress

from scipy import stats

from utils import getInternalDataset, getRunJson

import plotly.graph_objects as go

c = getRunJson()

df = getInternalDataset(c['Strategy']['DatasetPath'])

PIVOT_CANDLES = 3
PATTERN_CANDLES = 20
candleIndex = len(df) - 1

maxim = numpy.array([])
xxmax = numpy.array([])
minim = numpy.array([])
xxmin = numpy.array([])

def isPivot(candleTarget: int, candlesBack: int, candlesForward: int) -> int:
    global df
        
    if candleTarget - candlesBack < 0 or candleTarget + candlesForward >= len(df):
        return 0
    
    pividlow=1
    pividhigh=1
    for i in range(candleTarget - candlesBack, candleTarget + candlesForward + 1):
        if(df['Low'][candleTarget] > df['Low'][i]):
            pividlow=0
        if(df['High'][candleTarget]<df['High'][i]):
            pividhigh=0
    if pividlow and pividhigh:
        return 3
    elif pividlow:
        return 1
    elif pividhigh:
        return 2
    else:
        return 0

#apply the pivot points to the dataframe
p = [0] * len(df)

for i in range(len(p)):
    p[i] = isPivot(i, PIVOT_CANDLES, PIVOT_CANDLES)
    
df['pivot'] = p

def getPivotPoint(candleTarget: int) -> float:
    global df
       
    if df['pivot'][candleTarget] == 1:
        return df['Low'][candleTarget] - 1e-3
    elif df['pivot'][candleTarget] == 2:
        return df['High'][candleTarget] + 1e-3
    else:
        return numpy.nan
    

p = [0] * len(df)
for i in range(len(p)):
    p[i] = getPivotPoint(i)

df['pivotPoints'] = p

for i in range(candleIndex-PATTERN_CANDLES, candleIndex+1):
    if df['pivot'][i] == 1:
        minim = numpy.append(minim, df['Low'][i])
        xxmin = numpy.append(xxmin, df['Low'][i]) #could be i instead df.iloc[i].name
    if df['pivot'][i] == 2:
        maxim = numpy.append(maxim, df['High'][i])
        xxmax = numpy.append(xxmax, df['High'][i]) # df.iloc[i].name
        
#slmin, intercmin = numpy.polyfit(xxmin, minim,1)
#slmax, intercmax = numpy.polyfit(xxmax, maxim,1)

slmin, intercmin, rmin, pmin, semin = linregress(xxmin, minim)
slmax, intercmax, rmax, pmax, semax = linregress(xxmax, maxim)

print(rmin, rmax)

fig = go.Figure(data=[go.Candlestick(x=df.index,
                open=df['Open'],
                high=df['High'],
                low=df['Low'],
                close=df['Close'])])

fig.add_scatter(x=df.index, y=df['pivotPoints'], mode="markers",
                marker=dict(size=4, color="MediumPurple"),
                name="pivot")

#xxmin = numpy.append(xxmin, xxmin[-1]+15)
#xxmax = numpy.append(xxmax, xxmax[-1]+15)
#fig.add_trace(go.Scatter(x=xxmin, y=slmin*xxmin + adjintercmin, mode='lines', name='min slope'))
#fig.add_trace(go.Scatter(x=xxmax, y=slmax*xxmax + adjintercmax, mode='lines', name='max slope'))

#fig.add_trace(go.Scatter(x=xxmin, y=slmin*xxmin + intercmin, mode='lines', name='min slope'))
#f##ig.add_trace(go.Scatter(x=xxmax, y=slmax*xxmax + intercmax, mode='lines', name='max slope'))
fig.update_layout(xaxis_rangeslider_visible=False)
fig.show()
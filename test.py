import os

import numpy as np

import pandas as pd

from matplotlib import pyplot
from scipy.stats import linregress

from scipy import stats

from utils import getInternalDataset, getRunJson

import plotly.graph_objects as go

from datetime import datetime

c = getRunJson()
PIVOT_LENGTH = 3
BACK_CANDLES = 20

#df = getInternalDataset(c['Strategy']['DatasetPath'])

df = pd.read_csv('static/EURUSD_Candlestick_4_Hour_ASK_05.05.2003-16.10.2021.csv')

df['High'] = df['high']
df['Open'] = df['open']
df['Low'] = df['low']
df['Close'] = df['close']
df['Volume'] = df['volume']

df = df[df['Volume'] != 0]
df.reset_index(drop = True, inplace = True)
df.isna().sum()

def getPivotPoint(df: pd.DataFrame, num: int, pivotLeft: int, pivotRight: int) -> int:
    if num-pivotLeft < 0 or num+pivotRight >= len(df):
        return 0
    
    pivotLow=1
    pivotHigh=1
    for i in range(num-pivotLeft, num+pivotRight+1):
        if(df['Low'][num]>df['Low'][i]):
            pivotLow=0
        if(df['High'][num]<df['High'][i]):
            pivotHigh=0
    if pivotLow and pivotHigh:
        return 3
    elif pivotLow:
        return 1
    elif pivotHigh:
        return 2
    else:
        return 0
    
df['pivot'] = df.apply(lambda x: getPivotPoint(df, x.name,PIVOT_LENGTH,PIVOT_LENGTH), axis=1)

def pointPivotPosition(row: pd.DataFrame) -> float:
    if row['pivot']==1:
        return row['Low']-1e-3
    elif row['pivot']==2:
        return row['High']+1e-3
    else:
        return np.nan

df['pointpos'] = df.apply(lambda row: pointPivotPosition(row), axis=1)

def getLinearRegression(BACK_CANDLES: int) -> pd.Series:
    linreg = [None] * len(df)

    for candleid in range(BACK_CANDLES, len(df) - 1):
        maxSlope = np.array([])
        minSlope = np.array([])

        minSlopeIndex = np.array([])
        maxSlopeIndex = np.array([])

        for i in range(candleid-BACK_CANDLES, candleid+1):
            if df['pivot'][i] == 1:
                minSlope = np.append(minSlope, df['Low'][i])
                minSlopeIndex = np.append(minSlopeIndex, i)
            if df['pivot'][i] == 2:
                maxSlope = np.append(maxSlope, df['High'][i])
                maxSlopeIndex = np.append(maxSlopeIndex, i)
        
        if (maxSlopeIndex.size <3 and minSlopeIndex.size <3) or maxSlopeIndex.size==0 or minSlopeIndex.size==0:
            continue
        
        #slmin, intercmin = np.polyfit(xxmin, minim,1)
        #slmax, intercmax = np.polyfit(xxmax, maxim,1)

        linreg[candleid] = {
            'minSlope': linregress(minSlopeIndex, minSlope), #slmin, intercmin, rmin, pmin, semin
            'maxSlope': linregress(maxSlopeIndex, maxSlope), #slmax, intercmax, rmax, pmax, semax
            'minSlopeArr': minSlope,
            'maxSlopeArr': maxSlope,
            'minSlopeIndex': minSlopeIndex,
            'maxSlopeIndex': maxSlopeIndex
        }

    return pd.Series(linreg)
            
def savePatternToFile(df: pd.DataFrame, CANDLE_ID: str, displayCandles: int = 10, fixLength: int = 15) -> None:
    print(f'candleID is: {CANDLE_ID}')

    slmin, intercmin, rmin, pmin, semin = df['Patterns'][CANDLE_ID]['minSlope']
    slmax, intercmax, rmax, pmax, semax = df['Patterns'][CANDLE_ID]['maxSlope']

    dfpl = df[CANDLE_ID - BACK_CANDLES - displayCandles : CANDLE_ID + BACK_CANDLES + displayCandles]

    fig = go.Figure(data=[go.Candlestick(x=dfpl.index,
                    open=dfpl['Open'],
                    high=dfpl['High'],
                    low=dfpl['Low'],
                    close=dfpl['Close'])])

    fig.add_scatter(x=dfpl.index, y=dfpl['pointpos'], mode="markers",
                    marker=dict(size=4, color="MediumPurple"),
                    name="pivot")

    adjintercmin = df['Low'][CANDLE_ID-BACK_CANDLES:CANDLE_ID].min() - slmin*df['Low'][CANDLE_ID-BACK_CANDLES:CANDLE_ID].idxmin()
    adjintercmax = df['High'][CANDLE_ID-BACK_CANDLES:CANDLE_ID].max() - slmax*df['High'][CANDLE_ID-BACK_CANDLES:CANDLE_ID].idxmax()

    print(dfpl['Patterns'][CANDLE_ID]['minSlopeIndex'])

    #fix slope length
    dfpl['Patterns'][CANDLE_ID]['minSlopeIndex'] = np.append(
        dfpl['Patterns'][CANDLE_ID]['minSlopeIndex'],
        dfpl['Patterns'][CANDLE_ID]['minSlopeIndex'][-1] + fixLength
    )

    dfpl['Patterns'][CANDLE_ID]['maxSlopeIndex'] = np.append(
        dfpl['Patterns'][CANDLE_ID]['maxSlopeIndex'], 
        dfpl['Patterns'][CANDLE_ID]['maxSlopeIndex'][-1] + fixLength
    
    )

    fig.add_trace(
        go.Scatter(
            x = dfpl['Patterns'][CANDLE_ID]['minSlopeIndex'],
            y = slmin * dfpl['Patterns'][CANDLE_ID]['minSlopeIndex'] + adjintercmin,
            mode = 'lines',
            name = 'min slope'
        )
    )
    fig.add_trace(
        go.Scatter(
            x = dfpl['Patterns'][CANDLE_ID]['maxSlopeIndex'],
            y = slmax * dfpl['Patterns'][CANDLE_ID]['maxSlopeIndex'] + adjintercmax,
            mode = 'lines',
            name = 'max slope'
        )
    )

    #fig.add_trace(go.Scatter(x=minSlopeIndex, y=slmin*minSlopeIndex + intercmin, mode='lines', name='min slope'))
    #fig.add_trace(go.Scatter(x=maxSlopeIndex, y=slmax*maxSlopeIndex + intercmax, mode='lines', name='max slope'))
    fig.update_layout(xaxis_rangeslider_visible=False)
    #fig.show()

    if os.path.exists(f'tmp/{CANDLE_ID}') is False:
        os.mkdir(f'tmp/{CANDLE_ID}')    

    fig.write_image(
        f'tmp/{CANDLE_ID}/Graph.png'
    )

    with open(f'tmp/{CANDLE_ID}/DataFrame.csv', 'w') as f:
        dfpl.to_csv(f)
        f.close()

df['Patterns'] = getLinearRegression(BACK_CANDLES)

print(df)

def findInBoundsPatterns(df: pd.DataFrame, rMaxP: float, rMinP: float, slminP: float, slmaxP: float) -> None:
    pMin = 0
    pMax = 0

    for i in range(len(df)):
        if df['Patterns'][i] == None:
            continue

        slmin, intercmin, rmin, pmin, semin = df['Patterns'][i]['minSlope']
        slmax, intercmax, rmax, pmax, semax = df['Patterns'][i]['maxSlope']

        #if abs(rmax)>=0.7 and abs(rmin)>=0.7 and abs(slmin)<=0.00001 and slmax<-0.0001:
        #if abs(rmax)>=0.7 and abs(rmin)>=0.7 and slmin>=0.0001 and abs(slmax)<=0.00001:
        #if abs(rmax)>=0.9 and abs(rmin)>=0.9 and slmin>=0.0001 and slmax<=-0.0001:
        if abs(rmax) >= rMaxP and abs(rmin) >= rMinP and slmin >= slminP and slmax <= slmaxP:
            #duplication avoidness
            if pMin != rmin and pMax != rmax:
                pMin = rmin
                pMax = rmax
                print(rmax, rmin, slmin, slmax, i)
                savePatternToFile(df, i, 10, 15)

findInBoundsPatterns(df, 0.9, 0.9, 0.0001, 0.0001)
        
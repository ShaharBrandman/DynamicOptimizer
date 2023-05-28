import numpy
import pandas as pd

from scipy.stats import linregress

def getPivotPoint(df: pd.DataFrame, num: int, pivotLeft: int, pivotRight: int) -> int:
    if num - pivotLeft < 0 or num + pivotRight >= len(df):
        return 0

    pivotLow = 1
    pivotHigh = 1
    for i in range(num - pivotLeft, num + pivotRight + 1):
        if(df['Low'][num] > df['Low'][i]):
            pivotLow = 0
        if(df['High'][num] < df['High'][i]):
            pivotHigh = 0
        if pivotLow and pivotHigh:
            return 3
        elif pivotLow:
            return 1
        elif pivotHigh:
            return 2
        else:
            return 0

def pointPivotPosition(row: pd.DataFrame) -> float:
    if row['pivot'] == 1:
        return row['Low'] -1e-3
    elif row['pivot'] == 2:
        return row['High'] + 1e-3
    else:
        return numpy.nan
    
def findInBoundsPatterns(df: pd.DataFrame, params: dict) -> pd.Series:
    arr: list[int] = [0] * len(df)

    pMin = 0
    pMax = 0

    for i in range(len(df)):
        if df['Patterns'][i] == None:
            continue

        slmin, intercmin, rmin, pmin, semin = df['Patterns'][i]['minSlope']
        slmax, intercmax, rmax, pmax, semax = df['Patterns'][i]['maxSlope']

        #duplication avoidness
        if pMin == rmin and pMax == rmax:
            continue

        pMin = rmin
        pMax = rmax

        if abs(rmax) >= params['R_MAX_LONG'] and abs(rmin) >= params['R_MIN_LONG'] and slmin >= params['SL_MIN_LONG'] and slmax <= params['SL_MAX_LONG']:
            arr[i] = 2

        elif abs(rmax) <= params['R_MIN_SHORT'] and abs(rmin) <= params['R_MIN_SHORT'] and slmin <= params['SL_MIN_SHORT'] and slmax >= params['SL_MAX_SHORT']:
            arr[i] = 1

    return pd.Series(arr)

def getLinearRegression(df: pd.DataFrame, BACK_CANDLES: int) -> pd.Series:
    linreg: list[any] = [None] * len(df)

    for candleid in range(BACK_CANDLES, len(df) - 1):
        maxSlope = numpy.array([])
        minSlope = numpy.array([])

        minSlopeIndex = numpy.array([])
        maxSlopeIndex = numpy.array([])

        for i in range(candleid - BACK_CANDLES, candleid + 1):
            if df['pivot'][i] == 1:
                minSlope = numpy.append(minSlope, df['Low'][i])
                minSlopeIndex = numpy.append(minSlopeIndex, i)
            if df['pivot'][i] == 2:
                maxSlope = numpy.append(maxSlope, df['High'][i])
                maxSlopeIndex = numpy.append(maxSlopeIndex, i)
            
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

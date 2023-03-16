import logging
import sys

from datetime import datetime

from tools import validateSymbol

from exceptions import InvalidCLIArguement

logging.basicConfig(filename=f'{datetime.now().timestamp()}.txt',
                            filemode='a',
                            format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
                            datefmt='%Y-%m-%d %H:%M:%S',
                            level=logging.DEBUG)

logging.info()

def printHelp():
    print('arguments are: <symbol: string> <timeframe: string> <candles: int> <strategy: string>\n')
    print('--help: to print this message\n')
    print('possible commands are: --symbol, --timeframe, --strategies\n')

def printSymbols():
    print('everything on bybit\n')

def printTimeFrames():
    print('Timeframes are: 1,3,5,15,30,60,120,240,360,720,D,M,W\n')

def printStrategies():
    print('UMAS: Ultimate Moving Average Strategy, has a Ultimate Moving average that signals long and shorts\n')
    print('UMAR: Ultimate MA ADX RSI Strategy,\nLong Condition: RSI > X, ADX > Y, UMA LONG\nShortCondition: RSI < X, ADX > Y, UMA SHORT\n')
    print('')
args = sys.argv
try:

except InvalidCLIArguement as e:
    printHelp()
    print(e)
    exit(1)
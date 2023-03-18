import logging
import sys
import os

from datetime import datetime

from exceptions import InvalidCLIArguement

from tools import validatePair, validateTimeframe, validateStrategy, validateLoops, validateDataset, getStrategy

from optimizer import Optimizer

if os.path.exists('logs') is False:
    os.mkdir('logs')

def initLogs():
    logging.basicConfig(filename=f'logs/{datetime.now().timestamp()}.txt',
                            filemode='a',
                            format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
                            datefmt='%Y-%m-%d %H:%M:%S',
                            level=logging.DEBUG)

    logging.info(f'Running {os.getcwd()}/main.py')

def printHelp():
    print('arguments are: <pair: string> <timeframe: string> <candles back: int> <strategy: string> <loops: int> <dataset: filename (optional)>\n')
    print('--help: to print this message\n')
    print('possible commands are: --pair, --timeframe, --strategies\n')

def printSymbols():
    print('everything on bybit\n')

def printTimeFrames():
    print('Timeframes are: 1,3,5,15,30,60,120,240,360,720,D,M,W\n')

def printStrategies():
    print('UMAS: Ultimate Moving Average Strategy, has a Ultimate Moving average that signals long and shorts\n')
    print('UMAR: Ultimate MA ADX RSI Strategy,\nLong Condition: RSI > X, ADX > Y, UMA LONG\nShortCondition: RSI < X, ADX > Y, UMA SHORT\n')
    print('ZLSMA + CE: ZLSMA + Chandelier Exit,\nLong Condition: ZLSMA > PRICE, CE == 1 and preivousCE == -1,\nShort Condition: ZLSMA < PRICE, CE == -1 and previousCE == 1\n')

args = sys.argv
args = args[1:]

try:
    if len(args) > 1:
        validatePair(args[0])
        validateTimeframe(args[1])
        validateStrategy(args[2])
        validateLoops(args[3])

        if len(args) > 4:
            validateDataset(args[4])

        initLogs()

        o = Optimizer(
            {

            }
        )

        
    else:
        raise InvalidCLIArguement('Must enter arguments')
except InvalidCLIArguement as e:
    printHelp()
    print(e)
    exit(1)
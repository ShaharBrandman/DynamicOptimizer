import logging
import sys
import os

from datetime import datetime

from tools import validateDataset, getRunJson

from optimizer import Optimizer

if os.path.exists('logs') is False:
    os.mkdir('logs')

if os.path.exists('output') is False:
    os.mkdir('output')

if os.path.exists('output/closedPositions') is False:
    os.mkdir('output/closedPositions')

if os.path.exists('output/datasets') is False:
    os.mkdir('output/datasets')

def initLogs():
    logging.basicConfig(filename=f'logs/{datetime.now().timestamp()}.txt',
                            filemode='a',
                            format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
                            datefmt='%Y-%m-%d %H:%M:%S',
                            level=logging.DEBUG)

    logging.info(f'Running {os.getcwd()}/run.py')


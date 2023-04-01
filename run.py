import logging
import time
import os

from datetime import datetime

from utils import getRunJson, getStrategyByInput
from tools import validateDataset

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

start = time.time()

settings = getRunJson()

s = getStrategyByInput(
    settings['Strategy']['NAME']
).__init__(
    settings['Strategy']['Pair'],
    settings['Strategy']['Timeframe'],
    settings['Strategy']['candlesToLooks'],
    validateDataset(settings['Strategy']['dataset']) if settings['Strategy']['dataset'] != '' else None
)

o = Optimizer(
    settings['Portfolio'],
    s,
    settings['Strategy']['Params'],
    settings['Optimizer']['loops']
)

o.join()

end = time.time()

print(f'Finished executing {os.getcwd()}/run.py at {end - start} seconds')
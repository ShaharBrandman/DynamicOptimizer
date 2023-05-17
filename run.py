import os
import logging

from datetime import datetime

from optimizer import Optimizer
from utils import getRunJson

runID = datetime.now().timestamp()

def initLogs():
    global runID

    logging.basicConfig(filename=f'logs/{runID}.txt',
                            filemode='a',
                            format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
                            datefmt='%Y-%m-%d %H:%M:%S',
                            level=logging.DEBUG)

    logging.info(f'Running {os.getcwd()}/run.py')

if os.path.exists('logs') != True:
    os.mkdir('logs')

if os.path.exists('output') != True:
    os.mkdir('output')

if os.path.exists('tmp') != True:
    os.mkdir('tmp')

initLogs()

o = Optimizer(getRunJson(), runID)
o.start()
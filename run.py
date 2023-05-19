import os
import logging

from datetime import datetime

from optimizer import Optimizer
from utils import getRunJson

runID = int(datetime.now().timestamp())

def initLogs():
    global runID

    logging.basicConfig(filename=f'output/{runID}.logs',
                            filemode='a',
                            format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
                            datefmt='%Y-%m-%d %H:%M:%S',
                            level=logging.DEBUG)

    logging.info(f'Running {os.getcwd()}/run.py')

if os.path.exists('output') != True:
    os.mkdir('output')

if os.path.exists('tmp') != True:
    os.mkdir('tmp')

initLogs()

o = Optimizer(getRunJson(), runID)
o.start()
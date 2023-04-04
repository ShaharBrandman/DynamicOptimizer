import os
import logging

from datetime import datetime

from optimizer import Optimizer
from utils import getRunJson

def initLogs():
    logging.basicConfig(filename=f'logs/{datetime.now().timestamp()}.txt',
                            filemode='a',
                            format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
                            datefmt='%Y-%m-%d %H:%M:%S',
                            level=logging.DEBUG)

    logging.info(f'Running {os.getcwd()}/run.py')

o = Optimizer(getRunJson())
o.start()
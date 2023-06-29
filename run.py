import os
import argparse
import logging

from datetime import datetime

from optimizer import Optimizer

from functools import lru_cache

runID: str = ''

def initLogs(runID: str) -> None:
    logging.basicConfig(filename=f'output/{runID}.logs',
                            filemode='a',
                            format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
                            datefmt='%Y-%m-%d %H:%M:%S',
                            level=logging.DEBUG)

    logging.info(f'Running {os.getcwd()}/run.py')

def initCLI() -> dict:
    parser = argparse.ArgumentParser(description='DynamicOptimizer Configuration')

    parser.add_argument('-sp', '--strategy_params', metavar='KEY=VALUES', nargs='+', help='Strategy parameters')
    parser.add_argument('-u', '--url', help='Dataset URL', required = False)
    parser.add_argument('-p', '--path', help='Dataset Path', required = False)
    parser.add_argument('-y', '--yfinance', metavar='KEY=VALUE', nargs='+', help='yFinance settings', required = False)
    parser.add_argument('-of', '--optimizer_file', help='path Optimizer progress json file', required = False)
    parser.add_argument('-i', '--init_points', type=int, help='Number of initial exploration steps', required = True)
    parser.add_argument('-n', '--n_iter', type=int, help='Number of Bayesian optimization steps', required = True)
    parser.add_argument('-m', '--maximize', type=str, help='Result parameters to maximize', required = True)
    parser.add_argument('-e', '--equity', type=int, help='Portfolio equity', required = True)
    parser.add_argument('-l', '--leverage', type=int, help='Portfolio leverage', required = True)
    parser.add_argument('-c', '--commission', type=float, help='Portfolio commission', required = True)
    parser.add_argument('-s', '--show', action = 'store_true', help = 'show successful trades?', required = False)

    # Parse the arguments
    args = parser.parse_args()

    runJson = {}

    #config params duh
    #inside if statement just for t variable to be locally
    if args.strategy_params:
        t = {}
        for param in args.strategy_params:
            key, values = param.split('=')
            t[key] = [float(value) for value in values.split(',')]
        runJson['Strategy']['Params'] = t

    runID = ''

    #config data source
    if args.url:
        runJson['Strategy']['DatasetURL'] = args.url

        runID += f'DS-{args.url}'
    elif args.path:
        runJson['Strategy']['DatasetPath'] = args.path

        runID += 'DS-CUSTOM'
    elif args.yfinance:
        t = {}
        for settings in args.yfinance:
            key, value = settings.split('=')
            t[key] = value
        runJson['Strategy']['yFinance'] = t
        runID += f"DS-yFinance-{t['pair']}-{t['period']}-{t['interval']}"
    else:
        parser.error('Please provide datasource, use --h or --help for help')

    #config the optimizer
    if args.optimizer_file:
        runJson['Optimzer']['loadFrom'] = args.optimizerfile

    if args.show:
        runJson['Optimizer']['show'] = True

    runJson['Optimizer']['initPoints'] = args.init_points
    runJson['Optimizer']['nIter'] = args.n_iter
    runJson['Optimizer']['maximize'] = args.maximize

    #config portfolio
    runJson['Portoflio']['Equity'] = args.equity
    runJson['Portoflio']['Leverage'] = args.leverage
    runJson['Portoflio']['Commision'] = args.commision

    return runJson, runID

lru_cache(maxsize = None)
def initMain() -> None:
    if os.path.exists('output') != True:
        os.mkdir('output')

    if os.path.exists('tmp') != True:
        os.mkdir('tmp')

    runJson, runID = initCLI()

    initLogs(runID)

    o = Optimizer(runJson, runID)
    o.start()

if __name__ == '__main__':
    initMain()
import os
import argparse
import logging

from time import perf_counter

from datetime import datetime

from optimizer import Optimizer

def initLogs(runID: str) -> None:
    logging.basicConfig(
        filename=f'output/{runID}/progress.logs',
        filemode='a',
        format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S',
        level=logging.DEBUG
    )

    logging.getLogger('DynamicOptimizer')

    logging.info(f'Running {os.getcwd()}/run.py')

def initCLI() -> dict:
    runID = ''

    parser = argparse.ArgumentParser(description='DynamicOptimizer Configuration')

    parser.add_argument('-sp', '--strategy_params', metavar='KEY=VALUES', nargs='*', help='Strategy parameters')
    parser.add_argument('-u', '--url', help='Dataset URL', required = False)
    parser.add_argument('-p', '--path', help='Dataset Path', required = False)
    parser.add_argument('-yf', '--yfinance', metavar='KEY=VALUE', nargs='+', help='yFinance settings', required = False)
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

    runJson = {
        'Strategy': {},
        'Optimizer': {},
        'Portfolio': {}
    }

    #config params duh
    if args.strategy_params:
        t = {}
        for param in args.strategy_params:
            key, values = param.split('=')
            values = [float(value) for value in values.split(',')]
            if len(values) == 2:
                t[key] = {'min': values[0], 'max': values[1]}
            else:
                parser.error(f'Strategy Parameters must include a Max and Min value')
        runJson['Strategy']['Params'] = t

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
        runJson['Optimizer']['loadFrom'] = args.optimizerfile

    if args.show:
        runJson['Optimizer']['show'] = True
    else:
        runJson['Optimizer']['show'] = False

    runJson['Optimizer']['initPoints'] = args.init_points
    runJson['Optimizer']['nIter'] = args.n_iter
    runJson['Optimizer']['maximize'] = args.maximize

    #config portfolio
    runJson['Portfolio']['Equity'] = args.equity
    runJson['Portfolio']['Leverage'] = args.leverage
    runJson['Portfolio']['Commision'] = args.commission

    logging.debug(f'{runID} - CLI arguments: {runJson}')

    return runJson, runID

def initMain() -> None:
    start = perf_counter()

    if os.path.exists('output') != True:
        os.mkdir('output')

    if os.path.exists('tmp') != True:
        os.mkdir('tmp')

    runJson, runID = initCLI()
    print(runID)

    if os.path.exists(f'output/{runID}') != True:
        logging.debug(f'{runID} - created output dir')
        os.mkdir(f'output/{runID}')

    if os.path.exists(f'output/{runID}/graphs') != True:
        logging.debug(f'{runID} - created output dir for graphs')
        os.mkdir(f'output/{runID}/graphs')

    initLogs(runID)

    o = Optimizer(runJson, runID)
    o.start()

    end = perf_counter()

    logging.debug(f'{runID} start: {start}')
    logging.debug(f'{runID} end: {end}')
    logging.debug(f'{runID} stopped optimizing at {end - start}')

if __name__ == '__main__':
    initMain()
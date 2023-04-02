from tools import *
from utils import *

p = getStrategyParamsByInput('CE')
print(p)

randomizeParams(p)

print('after: \n')
print(p)
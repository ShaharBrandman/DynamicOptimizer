from datetime import datetime, timedelta

from bybitHTTPX import BybitClient

from utils import getConfig, getData

config = getConfig()

client = BybitClient(
    url = config['bybitEndpoint'],
    apiKey = config['bybitAPIKey'],
    apiSecret= config['bybitAPISecretKey'],
    recvWindow = 1000
)

timeframe = 5
limit = 999

d = getData(
    'ETHUSDT',
    '30',
    limit,
    client
)
print(len(d))
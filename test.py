from datetime import datetime, timedelta

from utils import getConfig, getData
from libs.bybitHTTPX import BybitClient

c = getConfig()

client = BybitClient(
    url = c['bybitEndpoint'],
    apiKey = c['bybitAPIKey'],
    apiSecret = c['bybitAPISecretKey']
)

print(getData(
    'BTCUSDT',
    '15',
    400,
    client
))

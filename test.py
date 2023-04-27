from datetime import datetime, timedelta

from utils import getConfig, getRunJson
from tools import plotData
from bybitHTTPX import BybitClient
from bybitHTTPX import historicDB

c = getConfig()
j = getRunJson()

client = BybitClient(
    url = c['bybitEndpoint'],
    apiKey = c['bybitAPIKey'],
    apiSecret = c['bybitAPISecretKey']
)

from utils import getInternalDataset

plotData(getInternalDataset(j['Strategy']['DatasetPath']))

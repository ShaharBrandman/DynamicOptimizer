import pandas as pd

from strategy import Strategy

class CE(Strategy):
    def __init__(self, src: str, pair: str, timeframe: str, candlesToLooks: int = 1000, dataset: pd.DataFrame = None) -> None:
        super().__init__(src, pair, timeframe, candlesToLooks, dataset)

class UMAR(Strategy):
    def __init__(self, src: str, pair: str, timeframe: str, candlesToLooks: int = 1000, dataset: pd.DataFrame = None) -> None:
        super().__init__(src, pair, timeframe, candlesToLooks, dataset)

class UMAS(Strategy):
    def __init__(self, src: str, pair: str, timeframe: str, candlesToLooks: int = 1000, dataset: pd.DataFrame = None) -> None:
        super().__init__(src, pair, timeframe, candlesToLooks, dataset)

Strategies = {
    'CE': CE,
    'UMAR': UMAR,
    'UMAS': UMAS
}
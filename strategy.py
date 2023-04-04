import pandas as pd
import pandas_ta as TA

from backtesting import Strategy

def Signal() -> pd.Series:
    pass

class daStrategy(Strategy):
    def __init__(self, params: dict) -> None:
        super().__init__()

        self.signal = self.I(Signal)

    def next(self):
        if (self.signal == 'LONG') and (len(self.trades) == 0):
            pass
        elif (self.signal == 'SHORT') and (len(self.trades) == 0):
            pass
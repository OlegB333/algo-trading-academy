from freqtrade.strategy import IStrategy
from pandas import DataFrame
import talib.abstract as ta

class Forex_EURUSD_30m(IStrategy):
    """
    Example strategy for Forex (EUR/USD).
    Timeframe 30m.
    """
    INTERFACE_VERSION = 3
    can_short = False
    timeframe = "30m"

    minimal_roi = {
        "0": 0.0001
    }
    stoploss = -0.01
    trailing_stop = False
    startup_candle_count = 0

    plot_config = {
        "main_plot": {
            "sma_20": {"color": "blue"},
            "sma_50": {"color": "orange"}
        },
        "subplots": {
            "RSI": {
                "rsi": {"color": "red"}
            }
        }
    }

    def populate_indicators(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        dataframe["volume"] = 1.0  # Freqtrade ignores entries with 0 volume
        dataframe["rsi"] = ta.RSI(dataframe, timeperiod=14)
        dataframe["sma_20"] = ta.SMA(dataframe, timeperiod=20)
        dataframe["sma_50"] = ta.SMA(dataframe, timeperiod=50)
        return dataframe

    def populate_entry_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        print(f"DEBUG Forex DataFrame len: {len(dataframe)}")
        dataframe.loc[:, 'enter_long'] = 1
        return dataframe

    def populate_exit_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        # Rely entirely on ROI/Stoploss
        return dataframe

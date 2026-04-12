from freqtrade.strategy import IStrategy
from pandas import DataFrame
import talib.abstract as ta

class TrendFollow_AAPL_30m(IStrategy):
    """
    Very simple trend following strategy for AAPL on 30m.
    """
    INTERFACE_VERSION = 3
    can_short = False
    timeframe = "30m"

    minimal_roi = {
        "0": 0.05,
        "20": 0.02,
        "40": 0.0
    }
    stoploss = -0.05
    trailing_stop = False
    startup_candle_count = 50

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
        if dataframe.empty:
            return dataframe

        dataframe["rsi"] = ta.RSI(dataframe, timeperiod=14)
        dataframe["sma_20"] = ta.SMA(dataframe, timeperiod=20)
        dataframe["sma_50"] = ta.SMA(dataframe, timeperiod=50)
        return dataframe

    def populate_entry_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        dataframe.loc[
            (
                (dataframe["rsi"] < 40) &
                (dataframe["sma_20"] > dataframe["sma_50"]) &
                (dataframe["volume"] > 0)
            ),
            "enter_long"
        ] = 1
        return dataframe

    def populate_exit_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        dataframe.loc[
            (
                (dataframe["rsi"] > 70) &
                (dataframe["volume"] > 0)
            ),
            "exit_long"
        ] = 1
        return dataframe

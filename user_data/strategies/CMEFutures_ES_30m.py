from freqtrade.strategy import IStrategy
from pandas import DataFrame
import talib.abstract as ta
from datetime import datetime

class CMEFutures_ES_30m(IStrategy):
    """
    Example strategy for CME futures (ES/USD).
    Timeframe 30m.
    """
    INTERFACE_VERSION = 3
    can_short = True
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

    def leverage(self, pair: str, current_time: datetime, current_rate: float,
                 proposed_leverage: float, max_leverage: float, entry_tag: str, side: str,
                 **kwargs) -> float:
        """
        Set trading leverage to 3.0x for ES.
        """
        return 3.0

    def populate_indicators(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        if dataframe.empty:
            return dataframe

        dataframe["rsi"] = ta.RSI(dataframe, timeperiod=14)
        dataframe["sma_20"] = ta.SMA(dataframe, timeperiod=20)
        dataframe["sma_50"] = ta.SMA(dataframe, timeperiod=50)
        return dataframe

    def populate_entry_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        # Long condition: RSI < 40 and SMA20 > SMA50
        dataframe.loc[
            (
                (dataframe["rsi"] < 40) &
                (dataframe["sma_20"] > dataframe["sma_50"]) &
                (dataframe["volume"] > 0)
            ),
            "enter_long"
        ] = 1

        # Short condition: RSI > 60 and SMA20 < SMA50
        dataframe.loc[
            (
                (dataframe["rsi"] > 60) &
                (dataframe["sma_20"] < dataframe["sma_50"]) &
                (dataframe["volume"] > 0)
            ),
            "enter_short"
        ] = 1

        return dataframe

    def populate_exit_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        # Exit long
        dataframe.loc[
            (
                (dataframe["rsi"] > 70) &
                (dataframe["volume"] > 0)
            ),
            "exit_long"
        ] = 1

        # Exit short
        dataframe.loc[
            (
                (dataframe["rsi"] < 30) &
                (dataframe["volume"] > 0)
            ),
            "exit_short"
        ] = 1

        return dataframe

# Freqtrade Strategy Template
# This is a minimal sample strategy for the Algo Trading Academy course.
# Use this as a starting point to create your own strategies.

from freqtrade.strategy.interface import IStrategy
from pandas import DataFrame
import talib.abstract as ta


class AcademySampleStrategy(IStrategy):
    """
    Sample strategy using SMA crossover.
    This is a teaching example — NOT for live trading.
    """

    INTERFACE_VERSION = 3

    # Minimal ROI table
    minimal_roi = {
        "60": 0.01,   # 1% profit after 60 minutes
        "30": 0.02,   # 2% profit after 30 minutes
        "0": 0.04     # 4% profit immediately
    }

    # Stoploss
    stoploss = -0.10  # 10% stoploss

    # Timeframe
    timeframe = '1h'

    # Run "populate_indicators()" only for new candle
    process_only_new_candles = True

    # Number of candles the strategy requires before producing valid signals
    startup_candle_count: int = 30

    def populate_indicators(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        """Add technical indicators to the dataframe."""
        dataframe['sma_fast'] = ta.SMA(dataframe, timeperiod=10)
        dataframe['sma_slow'] = ta.SMA(dataframe, timeperiod=30)
        return dataframe

    def populate_entry_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        """Define entry (buy) conditions."""
        dataframe.loc[
            (
                (dataframe['sma_fast'] > dataframe['sma_slow']) &  # Fast SMA above slow SMA
                (dataframe['volume'] > 0)
            ),
            'enter_long'] = 1
        return dataframe

    def populate_exit_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        """Define exit (sell) conditions."""
        dataframe.loc[
            (
                (dataframe['sma_fast'] < dataframe['sma_slow']) &  # Fast SMA below slow SMA
                (dataframe['volume'] > 0)
            ),
            'exit_long'] = 1
        return dataframe

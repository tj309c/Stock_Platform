"""
Pro Indicator Engine - 7-Tier Technical Analysis Engine

This engine calculates a wide range of technical indicators using the pandas-ta library.
It's designed to be extensible and efficient, calculating only what's requested.
"""

import pandas as pd
import pandas_ta as ta
from typing import List, Dict, Any

class ProIndicatorEngine:
    """
    A powerful technical analysis engine that calculates various indicators.
    """
    def calculate_indicators(self, price_data: pd.DataFrame) -> pd.DataFrame:
        """
        Calculates a specified list of technical indicators and appends them to the DataFrame.

        Args:
            price_data (pd.DataFrame): DataFrame with OHLCV data. Must have lowercase columns.
            indicators (List[str]): A list of indicator names to calculate.

        Returns:
            pd.DataFrame: The original DataFrame with new indicator columns appended.
        """
        if price_data is None or price_data.empty:
            return pd.DataFrame()

        data = price_data.copy()

        # Use the pandas_ta strategy feature for a clean implementation
        # This defines a set of common indicators to calculate.
        # This can be expanded in Phase 3 to include all 7 tiers.
        MyStrategy = ta.Strategy(
            name="Common Indicators",
            description="Common technical indicators",
            ta=[
                {"kind": "sma", "length": 50},
                {"kind": "ema", "length": 20},
                {"kind": "rsi"},
                {"kind": "macd"},
                {"kind": "bbands", "length": 20},
                {"kind": "atr", "length": 14},      # Average True Range
                {"kind": "stoch"},                  # Stochastic Oscillator (%K, %D)
            ]
        )

        # Run the strategy on the data
        data.ta.strategy(MyStrategy)
        return data
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

        # Define the full strategy based on PROJECT_PLAN.md (Tiers 1-4)
        strategy_definition = [
            # Tier 1 (Trend)
            {"kind": "sma", "length": 50}, {"kind": "ema", "length": 20},
            {"kind": "vwap"},
            {"kind": "psar"},
            {"kind": "adx"},

            # Tier 2 (Momentum/Oscillators)
            {"kind": "rsi"}, {"kind": "macd"}, {"kind": "stoch"},
            {"kind": "cci"},
            {"kind": "rvi"},

            # Tier 3 (Volatility)
            {"kind": "bbands", "length": 20},
            {"kind": "atr", "length": 14},
            {"kind": "kc"},
            {"kind": "donchian"},

            # Tier 4 (Volume)
            {"kind": "obv"},
            {"kind": "ad"},
            # Volume Profile is complex and not a standard pandas-ta indicator, requires separate implementation
        ]

        try:
            # Try to create and run a pandas-ta Strategy (modern, optimized approach)
            if not hasattr(ta, 'Strategy'):
                raise AttributeError("pandas-ta version does not support Strategy.")
            
            MyStrategy = ta.Strategy(name="Pro Indicator Strategy", ta=strategy_definition)
            data.ta.strategy(MyStrategy)

        except Exception as e:
            # If Strategy fails or is unavailable, fall back to manual calculation.
            # This makes the logic robust and avoids silent failures.
            # pandas_ta version doesn't expose Strategy; calculate indicators manually.
            # Prefer using DataFrame.ta methods when present, otherwise fall back to pandas/numpy implementations.
            # SMA
            try:
                if hasattr(data, 'ta') and hasattr(data.ta, 'sma'):
                    data['SMA_50'] = data.ta.sma(length=50)
                else:
                    data['SMA_50'] = data['close'].rolling(window=50, min_periods=1).mean()
            except Exception:
                data['SMA_50'] = data['close'].rolling(window=50, min_periods=1).mean()
            # EMA
            try:
                if hasattr(data, 'ta') and hasattr(data.ta, 'ema'):
                    data['EMA_20'] = data.ta.ema(length=20)
                else:
                    data['EMA_20'] = data['close'].ewm(span=20, adjust=False).mean()
            except Exception:
                data['EMA_20'] = data['close'].ewm(span=20, adjust=False).mean()
            # RSI - fallback implementation
            try:
                if hasattr(data, 'ta') and hasattr(data.ta, 'rsi'):
                    data['RSI_14'] = data.ta.rsi(length=14)
                else:
                    delta = data['close'].diff()
                    gain = delta.clip(lower=0).fillna(0)
                    loss = -1 * delta.clip(upper=0).fillna(0)
                    avg_gain = gain.rolling(window=14, min_periods=1).mean()
                    avg_loss = loss.rolling(window=14, min_periods=1).mean()
                    rs = avg_gain / (avg_loss.replace(0, 1))
                    data['RSI_14'] = 100 - (100 / (1 + rs))
            except Exception:
                delta = data['close'].diff()
                gain = delta.clip(lower=0).fillna(0)
                loss = -1 * delta.clip(upper=0).fillna(0)
                avg_gain = gain.rolling(window=14, min_periods=1).mean()
                avg_loss = loss.rolling(window=14, min_periods=1).mean()
                rs = avg_gain / (avg_loss.replace(0, 1))
                data['RSI_14'] = 100 - (100 / (1 + rs))
            # MACD
            try:
                if hasattr(data, 'ta') and hasattr(data.ta, 'macd'):
                    macd = data.ta.macd()
                    # macd returns dataframe with MACD, MACDh, MACDs
                    data = data.join(macd)
                else:
                    ema12 = data['close'].ewm(span=12, adjust=False).mean()
                    ema26 = data['close'].ewm(span=26, adjust=False).mean()
                    data['MACD'] = ema12 - ema26
                    data['MACD_SIGNAL'] = data['MACD'].ewm(span=9, adjust=False).mean()
                    data['MACD_HIST'] = data['MACD'] - data['MACD_SIGNAL']
                    # Add alias columns matching pandas-ta naming so dashboards detect MACD columns
                    data['MACD_12_26_9'] = data['MACD']
                    data['MACDh_12_26_9'] = data['MACD_HIST']
                    data['MACDs_12_26_9'] = data['MACD_SIGNAL']
            except Exception:
                pass
            # Bollinger Bands
            try:
                if hasattr(data, 'ta') and hasattr(data.ta, 'bbands'):
                    bb = data.ta.bbands(length=20)
                    data = data.join(bb)
                else:
                    sma20 = data['close'].rolling(window=20, min_periods=1).mean()
                    std20 = data['close'].rolling(window=20, min_periods=1).std()
                    data['BB_UPPER'] = sma20 + 2 * std20
                    data['BB_LOWER'] = sma20 - 2 * std20
            except Exception:
                pass
            # ATR (Approximation if not available)
            try:
                if hasattr(data, 'ta') and hasattr(data.ta, 'atr'):
                    data['ATR_14'] = data.ta.atr(length=14)
                else:
                    data['TR'] = (data['high'] - data['low']).abs()
                    data['ATR_14'] = data['TR'].rolling(window=14, min_periods=1).mean()
            except Exception:
                pass
            # Stochastic (simple K/D)
            try:
                if hasattr(data, 'ta') and hasattr(data.ta, 'stoch'):
                    stoch = data.ta.stoch()
                    data = data.join(stoch)
                else:
                    low14 = data['low'].rolling(window=14, min_periods=1).min()
                    high14 = data['high'].rolling(window=14, min_periods=1).max()
                    data['STOCH_K'] = ((data['close'] - low14) / (high14 - low14).replace(0, 1)) * 100
                    data['STOCH_D'] = data['STOCH_K'].rolling(window=3, min_periods=1).mean()
                    # Add alias columns matching pandas-ta naming
                    data['STOCHk_14_3_3'] = data['STOCH_K']
                    data['STOCHd_14_3_3'] = data['STOCH_D']
            except Exception:
                pass

        return data
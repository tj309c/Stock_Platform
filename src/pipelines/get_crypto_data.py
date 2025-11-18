"""
Crypto Data Pipeline for Analysis Master
Fetches cryptocurrency market data using ccxt (free exchange data).
Provides OHLCV data, market info, and exchange data for major cryptocurrencies.
"""

import ccxt
import pandas as pd
import numpy as np
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta
import streamlit as st
from src.core.cache_manager import CacheManager


class CryptoDataPipeline:
    """
    Main pipeline for fetching cryptocurrency data using ccxt.
    Supports multiple exchanges with Coinbase as the default.
    """

    def __init__(self, exchange_id: str = 'coinbase'):
        """
        Initialize the crypto data pipeline.

        Args:
            exchange_id: Exchange to use (default: 'coinbase')
        """
        self.exchange_id = exchange_id
        self._exchange = None

    @property
    def exchange(self):
        """Lazy load the exchange connection."""
        if self._exchange is None:
            try:
                exchange_class = getattr(ccxt, self.exchange_id)
                self._exchange = exchange_class({
                    'enableRateLimit': True,
                    'timeout': 30000,
                })
            except Exception as e:
                st.error(f"Error connecting to {self.exchange_id}: {str(e)}")
                # Fallback to coinbase
                self._exchange = ccxt.coinbase({'enableRateLimit': True})
        return self._exchange

    @CacheManager.cache_market_data
    def get_crypto_price(
        _self,
        symbol: str,
        timeframe: str = '1d',
        limit: int = 365
    ) -> Optional[pd.DataFrame]:
        """
        Fetch historical OHLCV data for a cryptocurrency.

        Args:
            symbol: Trading pair (e.g., 'BTC/USDT', 'ETH/USDT')
            timeframe: Candlestick timeframe ('1m', '5m', '15m', '1h', '4h', '1d', '1w')
            limit: Number of candles to fetch

        Returns:
            DataFrame with OHLCV data or None if error
        """
        try:
            # Fetch OHLCV data
            ohlcv = _self.exchange.fetch_ohlcv(symbol, timeframe, limit=limit)

            if not ohlcv:
                st.warning(f"No data found for {symbol}")
                return None

            # Convert to DataFrame
            df = pd.DataFrame(
                ohlcv,
                columns=['timestamp', 'Open', 'High', 'Low', 'Close', 'Volume']
            )

            # Convert timestamp to datetime
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
            df.set_index('timestamp', inplace=True)

            return df

        except Exception as e:
            st.error(f"Error fetching price data for {symbol}: {str(e)}")
            return None

    @CacheManager.cache_market_data
    def get_current_price(_self, symbol: str) -> Optional[float]:
        """
        Get the current price for a cryptocurrency.

        Args:
            symbol: Trading pair (e.g., 'BTC/USDT')

        Returns:
            Current price as float or None
        """
        try:
            ticker = _self.exchange.fetch_ticker(symbol)
            return ticker.get('last')

        except Exception as e:
            st.error(f"Error fetching current price for {symbol}: {str(e)}")
            return None

    @CacheManager.cache_market_data
    def get_ticker_info(_self, symbol: str) -> Optional[Dict[str, Any]]:
        """
        Get detailed ticker information for a cryptocurrency.

        Args:
            symbol: Trading pair (e.g., 'BTC/USDT')

        Returns:
            Dictionary with ticker info or None
        """
        try:
            ticker = _self.exchange.fetch_ticker(symbol)

            return {
                'symbol': ticker.get('symbol'),
                'last': ticker.get('last'),
                'bid': ticker.get('bid'),
                'ask': ticker.get('ask'),
                'high': ticker.get('high'),
                'low': ticker.get('low'),
                'volume': ticker.get('quoteVolume'),  # Volume in quote currency
                'base_volume': ticker.get('baseVolume'),  # Volume in base currency
                'change': ticker.get('change'),
                'percentage': ticker.get('percentage'),
                'timestamp': ticker.get('timestamp'),
                'datetime': ticker.get('datetime'),
            }

        except Exception as e:
            st.error(f"Error fetching ticker info for {symbol}: {str(e)}")
            return None

    @CacheManager.cache_market_data
    def get_orderbook(_self, symbol: str, limit: int = 20) -> Optional[Dict[str, Any]]:
        """
        Get orderbook data for a cryptocurrency.

        Args:
            symbol: Trading pair (e.g., 'BTC/USDT')
            limit: Number of levels to fetch

        Returns:
            Dictionary with bids and asks or None
        """
        try:
            orderbook = _self.exchange.fetch_order_book(symbol, limit=limit)

            return {
                'bids': orderbook.get('bids', []),
                'asks': orderbook.get('asks', []),
                'timestamp': orderbook.get('timestamp'),
                'datetime': orderbook.get('datetime'),
            }

        except Exception as e:
            st.error(f"Error fetching orderbook for {symbol}: {str(e)}")
            return None

    @CacheManager.cache_market_data
    def get_market_info(_self, symbol: str) -> Optional[Dict[str, Any]]:
        """
        Get market information and trading limits for a cryptocurrency.

        Args:
            symbol: Trading pair (e.g., 'BTC/USDT')

        Returns:
            Dictionary with market info or None
        """
        try:
            markets = _self.exchange.load_markets()
            market = markets.get(symbol)

            if not market:
                return None

            return {
                'id': market.get('id'),
                'symbol': market.get('symbol'),
                'base': market.get('base'),
                'quote': market.get('quote'),
                'active': market.get('active'),
                'maker_fee': market.get('maker'),
                'taker_fee': market.get('taker'),
                'limits': market.get('limits'),
                'precision': market.get('precision'),
            }

        except Exception as e:
            st.error(f"Error fetching market info for {symbol}: {str(e)}")
            return None

    @CacheManager.cache_market_data
    def get_multiple_tickers(
        _self,
        symbols: List[str]
    ) -> Dict[str, Dict[str, Any]]:
        """
        Fetch ticker data for multiple cryptocurrencies at once.

        Args:
            symbols: List of trading pairs

        Returns:
            Dictionary mapping symbols to their ticker data
        """
        results = {}

        for symbol in symbols:
            ticker = _self.get_ticker_info(symbol)
            if ticker is not None:
                results[symbol] = ticker

        return results

    def calculate_returns(self, price_data: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate various return metrics from price data.

        Args:
            price_data: DataFrame with OHLCV data

        Returns:
            DataFrame with added return columns
        """
        df = price_data.copy()

        # Daily returns
        df['Daily_Return'] = df['Close'].pct_change()

        # Cumulative returns
        df['Cumulative_Return'] = (1 + df['Daily_Return']).cumprod() - 1

        # Log returns
        df['Log_Return'] = np.log(df['Close'] / df['Close'].shift(1))

        return df

    def calculate_volatility(
        self,
        price_data: pd.DataFrame,
        window: int = 30
    ) -> pd.DataFrame:
        """
        Calculate rolling volatility metrics.

        Args:
            price_data: DataFrame with OHLCV data
            window: Rolling window size

        Returns:
            DataFrame with volatility metrics
        """
        df = self.calculate_returns(price_data)

        # Annualized volatility (365 days for crypto, 24/7 market)
        df['Volatility'] = df['Daily_Return'].rolling(window=window).std() * np.sqrt(365)

        return df

    @staticmethod
    def get_available_exchanges() -> List[str]:
        """
        Get list of available exchanges from ccxt.

        Returns:
            List of exchange IDs
        """
        return ccxt.exchanges

    @staticmethod
    def validate_symbol(symbol: str, exchange_id: str = 'coinbase') -> bool:
        """
        Validate if a trading pair exists on an exchange.

        Args:
            symbol: Trading pair (e.g., 'BTC/USD')
            exchange_id: Exchange to check

        Returns:
            bool: True if valid, False otherwise
        """
        try:
            exchange_class = getattr(ccxt, exchange_id)
            exchange = exchange_class({'enableRateLimit': True})
            markets = exchange.load_markets()
            return symbol in markets
        except:
            return False


# Convenience functions for quick access
def get_crypto_price(symbol: str, timeframe: str = '1d', limit: int = 365) -> Optional[pd.DataFrame]:
    """Quick function to get crypto price data."""
    pipeline = CryptoDataPipeline()
    return pipeline.get_crypto_price(symbol, timeframe, limit)


def get_current_price(symbol: str) -> Optional[float]:
    """Quick function to get current crypto price."""
    pipeline = CryptoDataPipeline()
    return pipeline.get_current_price(symbol)


def get_ticker_info(symbol: str) -> Optional[Dict[str, Any]]:
    """Quick function to get ticker info."""
    pipeline = CryptoDataPipeline()
    return pipeline.get_ticker_info(symbol)


def validate_symbol(symbol: str) -> bool:
    """Quick function to validate a symbol."""
    return CryptoDataPipeline.validate_symbol(symbol)

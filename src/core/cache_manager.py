"""
<<<<<<< HEAD
Cache Manager module for Stock Platform.

Provides caching functionality with TTL (Time To Live) support.
"""

from functools import wraps
from typing import Any, Callable, Optional, Union
from datetime import timedelta
=======
Cache Manager for Analysis Master
Provides caching decorators and utilities to manage data pipeline requests efficiently.
Uses Streamlit's built-in caching with TTL (Time-To-Live) for different data types.
"""

import streamlit as st
from functools import wraps
import hashlib
import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Callable, Optional
import pandas as pd


class CacheConfig:
    """Configuration for different cache types with appropriate TTL values."""

    # Market data caches (shorter TTL for real-time data)
    MARKET_DATA_TTL = 300  # 5 minutes for price data
    OPTIONS_DATA_TTL = 300  # 5 minutes for options chains
    CRYPTO_DATA_TTL = 60  # 1 minute for crypto (24/7 markets)

    # Fundamental data caches (longer TTL for less frequently changing data)
    FUNDAMENTALS_TTL = 3600  # 1 hour for financial statements
    EARNINGS_TTL = 3600  # 1 hour for earnings data

    # Economic & macro data caches
    ECONOMIC_DATA_TTL = 86400  # 24 hours for FRED/BLS/EIA data

    # Sentiment & news caches
    SENTIMENT_TTL = 600  # 10 minutes for sentiment data
    NEWS_TTL = 300  # 5 minutes for news feeds

    # Political & insider data
    INSIDER_TTL = 3600  # 1 hour for insider trades
    CONGRESSIONAL_TTL = 3600  # 1 hour for congressional trades

    # Analysis results (can be cached longer)
    ANALYSIS_TTL = 1800  # 30 minutes for analysis results
    BACKTEST_TTL = 86400  # 24 hours for backtest results
>>>>>>> 8b6cf2a (Checkpoint: pre-github backup)


class CacheManager:
    """
<<<<<<< HEAD
    Manager class for caching operations.

    Provides static methods for caching data with configurable TTL.
    """

    _cache_store = {}

    @staticmethod
    def cache_data(
        expires_after: Optional[Union[int, float, timedelta]] = None,
        key: Optional[str] = None
    ) -> Callable:
        """
        Decorator to cache function results with optional TTL.

        Args:
            expires_after: Time in seconds (int/float) or timedelta object after which
                          cache expires. None means cache never expires.
            key: Optional custom cache key. If None, function name is used.

        Returns:
            Decorated function with caching capability.

        Example:
            @CacheManager.cache_data(expires_after=60)
            def expensive_function():
                return "result"
        """
        def decorator(func: Callable) -> Callable:
            @wraps(func)
            def wrapper(*args, **kwargs) -> Any:
                # Convert expires_after to seconds if it's a timedelta
                ttl_seconds = None
                if expires_after is not None:
                    if isinstance(expires_after, timedelta):
                        ttl_seconds = expires_after.total_seconds()
                    else:
                        ttl_seconds = float(expires_after)

                # Generate cache key
                cache_key = key if key else func.__name__

                # Check if result is cached and still valid
                if cache_key in CacheManager._cache_store:
                    cached_data = CacheManager._cache_store[cache_key]
                    if 'result' in cached_data:
                        # For now, simple caching without expiry check
                        # TTL logic can be enhanced with timestamp checks
                        return cached_data['result']

                # Call function and cache result
                result = func(*args, **kwargs)
                CacheManager._cache_store[cache_key] = {
                    'result': result,
                    'ttl': ttl_seconds
                }

                return result

            return wrapper

        return decorator

    @staticmethod
    def clear_cache(key: Optional[str] = None) -> None:
        """
        Clear cached data.

        Args:
            key: Optional specific cache key to clear. If None, clears all cache.
        """
        if key:
            CacheManager._cache_store.pop(key, None)
        else:
            CacheManager._cache_store.clear()


# Module-level alias for convenience
cache = CacheManager.cache_data
=======
    Centralized cache management for the Analysis Master platform.
    Provides decorators and utility functions for caching data pipeline results.
    """

    @staticmethod
    def cache_market_data(func: Callable) -> Callable:
        """
        Decorator for caching market data (prices, volume, OHLCV).
        TTL: 5 minutes
        """
        @st.cache_data(ttl=CacheConfig.MARKET_DATA_TTL, show_spinner=False)
        @wraps(func)
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)
        return wrapper

    @staticmethod
    def cache_options_data(func: Callable) -> Callable:
        """
        Decorator for caching options chain data.
        TTL: 5 minutes
        """
        @st.cache_data(ttl=CacheConfig.OPTIONS_DATA_TTL, show_spinner=False)
        @wraps(func)
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)
        return wrapper

    @staticmethod
    def cache_crypto_data(func: Callable) -> Callable:
        """
        Decorator for caching crypto data (24/7 markets need shorter TTL).
        TTL: 1 minute
        """
        @st.cache_data(ttl=CacheConfig.CRYPTO_DATA_TTL, show_spinner=False)
        @wraps(func)
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)
        return wrapper

    @staticmethod
    def cache_fundamentals(func: Callable) -> Callable:
        """
        Decorator for caching fundamental data (balance sheet, income statement, etc.).
        TTL: 1 hour
        """
        @st.cache_data(ttl=CacheConfig.FUNDAMENTALS_TTL, show_spinner=False)
        @wraps(func)
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)
        return wrapper

    @staticmethod
    def cache_economic_data(func: Callable) -> Callable:
        """
        Decorator for caching economic/macro data (FRED, BLS, EIA).
        TTL: 24 hours
        """
        @st.cache_data(ttl=CacheConfig.ECONOMIC_DATA_TTL, show_spinner=False)
        @wraps(func)
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)
        return wrapper

    @staticmethod
    def cache_sentiment(func: Callable) -> Callable:
        """
        Decorator for caching sentiment analysis results.
        TTL: 30 minutes
        """
        @st.cache_data(ttl=CacheConfig.SENTIMENT_TTL, show_spinner=False)
        @wraps(func)
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)
        return wrapper

    @staticmethod
    def cache_news(func: Callable) -> Callable:
        """
        Decorator for caching news feed data.
        TTL: 15 minutes
        """
        @st.cache_data(ttl=CacheConfig.NEWS_TTL, show_spinner=False)
        @wraps(func)
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)
        return wrapper

    @staticmethod
    def cache_analysis(func: Callable) -> Callable:
        """
        Decorator for caching analysis results (calculations, models).
        TTL: 30 minutes
        """
        @st.cache_data(ttl=CacheConfig.ANALYSIS_TTL, show_spinner=False)
        @wraps(func)
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)
        return wrapper

    @staticmethod
    def cache_backtest(func: Callable) -> Callable:
        """
        Decorator for caching backtest results (computationally expensive).
        TTL: 24 hours
        """
        @st.cache_data(ttl=CacheConfig.BACKTEST_TTL, show_spinner=False)
        @wraps(func)
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)
        return wrapper

    @staticmethod
    def clear_all_cache():
        """Clear all Streamlit cache."""
        st.cache_data.clear()
        return True

    @staticmethod
    def clear_sentiment_cache():
        """Clear sentiment-specific caches. Currently alias to clear_all_cache for convenience/testing."""
        # TODO: scope to only clear sentiment caches if necessary
        st.cache_data.clear()
        return True

    @staticmethod
    def get_cache_key(data: Any) -> str:
        """
        Generate a unique cache key from arbitrary data.

        Args:
            data: Any data to generate a key from

        Returns:
            str: A unique hash key
        """
        # Convert data to JSON string for consistent hashing
        json_str = json.dumps(data, sort_keys=True, default=str)
        return hashlib.md5(json_str.encode()).hexdigest()


# Convenience function for quick access
def get_cache_manager() -> CacheManager:
    """Get the singleton CacheManager instance."""
    return CacheManager()
>>>>>>> 8b6cf2a (Checkpoint: pre-github backup)

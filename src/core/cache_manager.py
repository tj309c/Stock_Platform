"""
Cache Manager module for Stock Platform.

Provides caching functionality with TTL (Time To Live) support.
"""

from functools import wraps
from typing import Any, Callable, Optional, Union
from datetime import timedelta


class CacheManager:
    """
    Manager class for caching operations.

    Provides static methods for caching data with configurable TTL.
    """

<<<<<<< HEAD
    _cache_store = {}
=======
    @staticmethod
    def cache_data(ttl: Optional[int] = None, **kwargs) -> Callable:
        """
        Generic cache_data decorator that wraps Streamlit's st.cache_data with TTL handling.
        
        Args:
            ttl: Time to live in seconds. If None, cache persists indefinitely.
            **kwargs: Additional arguments to pass to st.cache_data
            
        Returns:
            Callable: Decorated function with caching applied
            
        Example:
            @CacheManager.cache_data(ttl=3600)
            def expensive_computation(x):
                return x * 2
        """
        def decorator(func: Callable) -> Callable:
            # Prepare cache_data arguments
            cache_kwargs = kwargs.copy()
            cache_kwargs['ttl'] = ttl
            
            # Apply Streamlit's cache_data decorator and return directly
            return st.cache_data(**cache_kwargs)(func)
        
        return decorator

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
>>>>>>> c256e4d (Add generic cache_data method and module-level cache alias with tests)

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


<<<<<<< HEAD
=======
# Convenience function for quick access
def get_cache_manager() -> CacheManager:
    """Get the singleton CacheManager instance."""
    return CacheManager()


>>>>>>> c256e4d (Add generic cache_data method and module-level cache alias with tests)
# Module-level alias for convenience
cache = CacheManager.cache_data

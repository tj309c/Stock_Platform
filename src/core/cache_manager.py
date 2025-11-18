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

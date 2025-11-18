"""Cache Manager for Stock Platform.

Provides caching functionality with a decorator-based API.
"""

import functools
from typing import Any, Callable, Optional
from datetime import datetime, timedelta


class CacheManager:
    """Manages caching operations for the Stock Platform.
    
    Provides a generic cache_data decorator method that can cache function results
    based on their arguments.
    """
    
    def __init__(self):
        """Initialize the CacheManager with an empty cache store."""
        self._cache = {}
        self._cache_timestamps = {}
    
    def cache_data(
        self,
        ttl: Optional[int] = None,
        key_prefix: Optional[str] = None
    ) -> Callable:
        """Decorator to cache function results.
        
        Args:
            ttl: Time to live in seconds. If provided, cached data expires after ttl seconds.
            key_prefix: Optional prefix for cache keys to avoid collisions.
            
        Returns:
            A decorator function that caches the wrapped function's results.
            
        Example:
            >>> manager = CacheManager()
            >>> @manager.cache_data(ttl=60)
            ... def expensive_function(x):
            ...     return x * 2
        """
        def decorator(func: Callable) -> Callable:
            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                # Create a cache key from function name, args, and kwargs
                cache_key_parts = [
                    key_prefix or '',
                    func.__name__,
                    str(args),
                    str(sorted(kwargs.items()))
                ]
                cache_key = ':'.join(cache_key_parts)
                
                # Check if we have a cached result
                if cache_key in self._cache:
                    # Check if TTL is set and if cache has expired
                    if ttl is not None:
                        timestamp = self._cache_timestamps.get(cache_key)
                        if timestamp:
                            age = (datetime.now() - timestamp).total_seconds()
                            if age > ttl:
                                # Cache expired, remove it
                                del self._cache[cache_key]
                                del self._cache_timestamps[cache_key]
                            else:
                                # Cache is valid, return cached result
                                return self._cache[cache_key]
                    else:
                        # No TTL, return cached result
                        return self._cache[cache_key]
                
                # Compute the result
                result = func(*args, **kwargs)
                
                # Store in cache
                self._cache[cache_key] = result
                if ttl is not None:
                    self._cache_timestamps[cache_key] = datetime.now()
                
                return result
            
            return wrapper
        return decorator
    
    def clear_cache(self):
        """Clear all cached data."""
        self._cache.clear()
        self._cache_timestamps.clear()
    
    def get_cache_size(self) -> int:
        """Get the number of items in the cache.
        
        Returns:
            Number of cached items.
        """
        return len(self._cache)


# Create a default instance for convenient module-level usage
_default_manager = CacheManager()

# Module-level alias for easy importing: from cache_manager import cache
cache = _default_manager.cache_data

"""Cache management for Stock Platform using Streamlit's caching."""
import streamlit as st
from typing import Callable, Optional, Any
from functools import wraps


class CacheManager:
    """Manages caching functionality with TTL handling."""
    
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
            if ttl is not None:
                cache_kwargs['ttl'] = ttl
            
            # Apply Streamlit's cache_data decorator
            cached_func = st.cache_data(**cache_kwargs)(func)
            
            @wraps(func)
            def wrapper(*args, **kwargs) -> Any:
                return cached_func(*args, **kwargs)
            
            return wrapper
        
        return decorator


# Module-level alias for convenience
cache = CacheManager.cache_data

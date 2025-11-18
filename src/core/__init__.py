<<<<<<< HEAD
"""Core module for Stock Platform."""

from .cache_manager import CacheManager, cache

__all__ = ['CacheManager', 'cache']
=======
"""Core utilities and configuration"""
from .config import AppConfig
from .cache_manager import CacheManager, cache
from .design_system import ThemeManager, MetricCardRenderer
from .wsb_quotes import WSBQuotes, get_random_quote

__all__ = ['AppConfig', 'CacheManager', 'cache', 'ThemeManager', 'MetricCardRenderer', 'WSBQuotes', 'get_random_quote']
>>>>>>> c256e4d (Add generic cache_data method and module-level cache alias with tests)

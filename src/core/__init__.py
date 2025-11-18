<<<<<<< HEAD
"""Core module for Stock Platform."""

from .cache_manager import CacheManager, cache

__all__ = ['CacheManager', 'cache']
=======
"""Core utilities and configuration"""
from .config import AppConfig
from .cache_manager import CacheManager
from .design_system import ThemeManager, MetricCardRenderer
from .wsb_quotes import WSBQuotes, get_random_quote

__all__ = ['AppConfig', 'CacheManager', 'ThemeManager', 'MetricCardRenderer', 'WSBQuotes', 'get_random_quote']
>>>>>>> 8b6cf2a (Checkpoint: pre-github backup)

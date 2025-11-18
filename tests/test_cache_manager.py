"""Unit tests for CacheManager.

Tests the cache_data decorator and module-level cache alias.
"""

import unittest
import time
import sys
import os

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.cache_manager import CacheManager, cache


class TestCacheManager(unittest.TestCase):
    """Test cases for CacheManager class."""
    
    def setUp(self):
        """Set up a fresh CacheManager for each test."""
        self.manager = CacheManager()
    
    def test_cache_manager_initialization(self):
        """Test that CacheManager initializes correctly."""
        self.assertEqual(self.manager.get_cache_size(), 0)
    
    def test_cache_data_decorator_basic(self):
        """Test basic caching functionality."""
        call_count = {'count': 0}
        
        @self.manager.cache_data()
        def expensive_function(x):
            call_count['count'] += 1
            return x * 2
        
        # First call should execute the function
        result1 = expensive_function(5)
        self.assertEqual(result1, 10)
        self.assertEqual(call_count['count'], 1)
        
        # Second call with same arguments should use cache
        result2 = expensive_function(5)
        self.assertEqual(result2, 10)
        self.assertEqual(call_count['count'], 1)  # Function not called again
        
        # Call with different arguments should execute function
        result3 = expensive_function(10)
        self.assertEqual(result3, 20)
        self.assertEqual(call_count['count'], 2)
    
    def test_cache_data_with_kwargs(self):
        """Test caching with keyword arguments."""
        call_count = {'count': 0}
        
        @self.manager.cache_data()
        def function_with_kwargs(x, y=5):
            call_count['count'] += 1
            return x + y
        
        # Test with positional and keyword args
        result1 = function_with_kwargs(3, y=7)
        self.assertEqual(result1, 10)
        self.assertEqual(call_count['count'], 1)
        
        # Same call should use cache
        result2 = function_with_kwargs(3, y=7)
        self.assertEqual(result2, 10)
        self.assertEqual(call_count['count'], 1)
        
        # Different kwargs should execute function
        result3 = function_with_kwargs(3, y=10)
        self.assertEqual(result3, 13)
        self.assertEqual(call_count['count'], 2)
    
    def test_cache_data_with_ttl(self):
        """Test cache expiration with TTL."""
        call_count = {'count': 0}
        
        @self.manager.cache_data(ttl=1)  # 1 second TTL
        def timed_function(x):
            call_count['count'] += 1
            return x * 3
        
        # First call
        result1 = timed_function(4)
        self.assertEqual(result1, 12)
        self.assertEqual(call_count['count'], 1)
        
        # Immediate second call should use cache
        result2 = timed_function(4)
        self.assertEqual(result2, 12)
        self.assertEqual(call_count['count'], 1)
        
        # Wait for cache to expire
        time.sleep(1.1)
        
        # Call after TTL should execute function again
        result3 = timed_function(4)
        self.assertEqual(result3, 12)
        self.assertEqual(call_count['count'], 2)
    
    def test_cache_data_with_key_prefix(self):
        """Test cache with key prefix to avoid collisions."""
        call_count = {'count': 0}
        
        @self.manager.cache_data(key_prefix="prefix1")
        def function_a(x):
            call_count['count'] += 1
            return x * 2
        
        @self.manager.cache_data(key_prefix="prefix2")
        def function_b(x):
            call_count['count'] += 1
            return x * 3
        
        # Call both functions with same argument
        result1 = function_a(5)
        result2 = function_b(5)
        
        self.assertEqual(result1, 10)
        self.assertEqual(result2, 15)
        self.assertEqual(call_count['count'], 2)
        
        # Both should use their own cache
        result3 = function_a(5)
        result4 = function_b(5)
        
        self.assertEqual(result3, 10)
        self.assertEqual(result4, 15)
        self.assertEqual(call_count['count'], 2)  # No additional calls
    
    def test_clear_cache(self):
        """Test clearing the cache."""
        call_count = {'count': 0}
        
        @self.manager.cache_data()
        def cached_function(x):
            call_count['count'] += 1
            return x * 2
        
        # Populate cache
        cached_function(5)
        self.assertEqual(self.manager.get_cache_size(), 1)
        
        # Clear cache
        self.manager.clear_cache()
        self.assertEqual(self.manager.get_cache_size(), 0)
        
        # Next call should execute function again
        cached_function(5)
        self.assertEqual(call_count['count'], 2)
    
    def test_get_cache_size(self):
        """Test getting cache size."""
        @self.manager.cache_data()
        def func(x):
            return x
        
        self.assertEqual(self.manager.get_cache_size(), 0)
        
        func(1)
        self.assertEqual(self.manager.get_cache_size(), 1)
        
        func(2)
        self.assertEqual(self.manager.get_cache_size(), 2)
        
        func(1)  # Cached, size should not change
        self.assertEqual(self.manager.get_cache_size(), 2)
    
    def test_module_level_cache_alias(self):
        """Test that the module-level 'cache' alias works correctly."""
        call_count = {'count': 0}
        
        @cache()
        def aliased_function(x):
            call_count['count'] += 1
            return x * 4
        
        # First call
        result1 = aliased_function(3)
        self.assertEqual(result1, 12)
        self.assertEqual(call_count['count'], 1)
        
        # Second call should use cache
        result2 = aliased_function(3)
        self.assertEqual(result2, 12)
        self.assertEqual(call_count['count'], 1)
    
    def test_module_level_cache_alias_with_ttl(self):
        """Test that the module-level 'cache' alias works with TTL."""
        call_count = {'count': 0}
        
        @cache(ttl=1)
        def aliased_timed_function(x):
            call_count['count'] += 1
            return x * 5
        
        # First call
        result1 = aliased_timed_function(2)
        self.assertEqual(result1, 10)
        self.assertEqual(call_count['count'], 1)
        
        # Immediate call should use cache
        result2 = aliased_timed_function(2)
        self.assertEqual(result2, 10)
        self.assertEqual(call_count['count'], 1)
        
        # Wait for expiration
        time.sleep(1.1)
        
        # Call after TTL should execute again
        result3 = aliased_timed_function(2)
        self.assertEqual(result3, 10)
        self.assertEqual(call_count['count'], 2)
    
    def test_function_with_no_args(self):
        """Test caching function with no arguments."""
        call_count = {'count': 0}
        
        @self.manager.cache_data()
        def no_args_function():
            call_count['count'] += 1
            return 42
        
        result1 = no_args_function()
        self.assertEqual(result1, 42)
        self.assertEqual(call_count['count'], 1)
        
        result2 = no_args_function()
        self.assertEqual(result2, 42)
        self.assertEqual(call_count['count'], 1)  # Should use cache


if __name__ == '__main__':
    unittest.main()

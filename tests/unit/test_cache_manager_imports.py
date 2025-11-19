"""Tests for cache_manager imports and caching behavior."""
import unittest
from unittest.mock import patch, MagicMock
import sys


class TestCacheManagerImports(unittest.TestCase):
    """Test CacheManager import and caching functionality."""
    
    def test_import_cache_manager(self):
        """Test that CacheManager can be imported."""
        from src.core.cache_manager import CacheManager
        self.assertIsNotNone(CacheManager)
        self.assertTrue(hasattr(CacheManager, 'cache_data'))
    
    def test_import_cache_alias(self):
        """Test that cache alias can be imported."""
        from src.core.cache_manager import cache
        self.assertIsNotNone(cache)
    
    def test_import_from_core_module(self):
        """Test that imports work from core module."""
        from src.core import CacheManager, cache
        self.assertIsNotNone(CacheManager)
        self.assertIsNotNone(cache)
    
    def test_cache_is_alias_to_cache_data(self):
        """Test that cache is an alias to CacheManager.cache_data."""
        from src.core.cache_manager import CacheManager, cache
        self.assertEqual(cache, CacheManager.cache_data)
    
    @patch('streamlit.cache_data')
    def test_cache_data_decorator_without_ttl(self, mock_st_cache_data):
        """Test cache_data decorator without TTL parameter."""
        from src.core.cache_manager import CacheManager
        
        # Mock the streamlit cache_data to return a passthrough decorator
        def passthrough_decorator(*args, **kwargs):
            def decorator(func):
                return func
            return decorator
        
        mock_st_cache_data.side_effect = passthrough_decorator
        
        # Apply the decorator
        @CacheManager.cache_data()
        def test_function(x):
            return x * 2
        
        # Verify the function works
        result = test_function(5)
        self.assertEqual(result, 10)
        
        # Verify streamlit's cache_data was called
        mock_st_cache_data.assert_called()
    
    @patch('streamlit.cache_data')
    def test_cache_data_decorator_with_ttl(self, mock_st_cache_data):
        """Test cache_data decorator with TTL parameter."""
        from src.core.cache_manager import CacheManager
        
        # Mock the streamlit cache_data
        def passthrough_decorator(*args, **kwargs):
            def decorator(func):
                return func
            return decorator
        
        mock_st_cache_data.side_effect = passthrough_decorator
        
        # Apply the decorator with TTL
        @CacheManager.cache_data(ttl=3600)
        def test_function(x):
            return x * 3
        
        # Verify the function works
        result = test_function(5)
        self.assertEqual(result, 15)
        
        # Verify streamlit's cache_data was called with ttl
        mock_st_cache_data.assert_called_with(ttl=3600)
    
    @patch('streamlit.cache_data')
    def test_cache_alias_decorator(self, mock_st_cache_data):
        """Test using cache alias as a decorator."""
        from src.core.cache_manager import cache
        
        # Mock the streamlit cache_data
        def passthrough_decorator(*args, **kwargs):
            def decorator(func):
                return func
            return decorator
        
        mock_st_cache_data.side_effect = passthrough_decorator
        
        # Apply the decorator using the alias
        @cache(ttl=1800)
        def test_function(x):
            return x * 4
        
        # Verify the function works
        result = test_function(5)
        self.assertEqual(result, 20)
        
        # Verify streamlit's cache_data was called
        mock_st_cache_data.assert_called_with(ttl=1800)
    
    @patch('streamlit.cache_data')
    def test_cache_data_with_additional_kwargs(self, mock_st_cache_data):
        """Test cache_data decorator with additional kwargs."""
        from src.core.cache_manager import CacheManager
        
        # Mock the streamlit cache_data
        def passthrough_decorator(*args, **kwargs):
            def decorator(func):
                return func
            return decorator
        
        mock_st_cache_data.side_effect = passthrough_decorator
        
        # Apply the decorator with multiple kwargs
        @CacheManager.cache_data(ttl=7200, show_spinner=False)
        def test_function(x):
            return x * 5
        
        # Verify the function works
        result = test_function(5)
        self.assertEqual(result, 25)
        
        # Verify streamlit's cache_data was called with all kwargs
        mock_st_cache_data.assert_called_with(ttl=7200, show_spinner=False)


if __name__ == '__main__':
    unittest.main()

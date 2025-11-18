"""
Unit tests for CacheManager import alias and cache_data behavior.

Tests verify:
1. Import of 'cache' alias from cache_manager module
2. Import of CacheManager.cache_data staticmethod
3. TTL conversion logic for expires_after parameter
4. Caching behavior with various configurations
"""

from datetime import timedelta
from src.core.cache_manager import CacheManager, cache


class TestCacheManagerImports:
    """Test import functionality for cache_manager module."""

    def test_import_cache_alias(self):
        """Test that 'cache' alias can be imported."""
        from src.core.cache_manager import cache as imported_cache
        assert imported_cache is not None
        assert callable(imported_cache)

    def test_import_cache_from_core(self):
        """Test that 'cache' can be imported from core module."""
        from src.core import cache as core_cache
        assert core_cache is not None
        assert callable(core_cache)

    def test_import_cache_manager(self):
        """Test that CacheManager can be imported."""
        from src.core.cache_manager import CacheManager as ImportedCacheManager
        assert ImportedCacheManager is not None

    def test_cache_data_exists(self):
        """Test that CacheManager.cache_data staticmethod exists."""
        assert hasattr(CacheManager, 'cache_data')
        assert callable(CacheManager.cache_data)

    def test_cache_alias_equals_cache_data(self):
        """Test that cache alias points to CacheManager.cache_data."""
        assert cache is CacheManager.cache_data


class TestCacheDataBehavior:
    """Test CacheManager.cache_data functionality."""

    def setup_method(self):
        """Clear cache before each test."""
        CacheManager.clear_cache()

    def teardown_method(self):
        """Clear cache after each test."""
        CacheManager.clear_cache()

    def test_cache_data_basic_decorator(self):
        """Test basic caching without TTL."""
        call_count = 0

        @CacheManager.cache_data()
        def test_func():
            nonlocal call_count
            call_count += 1
            return "result"

        # First call should execute function
        result1 = test_func()
        assert result1 == "result"
        assert call_count == 1

        # Second call should use cached result
        result2 = test_func()
        assert result2 == "result"
        assert call_count == 1  # Function not called again

    def test_cache_data_with_int_ttl(self):
        """Test caching with integer TTL (seconds)."""
        @CacheManager.cache_data(expires_after=60)
        def test_func():
            return "cached_result"

        result = test_func()
        assert result == "cached_result"

        # Verify cache entry exists
        assert 'test_func' in CacheManager._cache_store
        assert CacheManager._cache_store['test_func']['ttl'] == 60.0

    def test_cache_data_with_float_ttl(self):
        """Test caching with float TTL (seconds)."""
        @CacheManager.cache_data(expires_after=30.5)
        def test_func():
            return "cached_result"

        result = test_func()
        assert result == "cached_result"

        # Verify cache entry exists with float TTL
        assert 'test_func' in CacheManager._cache_store
        assert CacheManager._cache_store['test_func']['ttl'] == 30.5

    def test_cache_data_with_timedelta_ttl(self):
        """Test caching with timedelta TTL - TTL conversion logic."""
        ttl_delta = timedelta(minutes=5)

        @CacheManager.cache_data(expires_after=ttl_delta)
        def test_func():
            return "cached_result"

        result = test_func()
        assert result == "cached_result"

        # Verify TTL is converted to seconds (5 minutes = 300 seconds)
        assert 'test_func' in CacheManager._cache_store
        assert CacheManager._cache_store['test_func']['ttl'] == 300.0

    def test_cache_data_with_custom_key(self):
        """Test caching with custom cache key."""
        @CacheManager.cache_data(key="custom_key")
        def test_func():
            return "result"

        result = test_func()
        assert result == "result"

        # Verify custom key is used
        assert 'custom_key' in CacheManager._cache_store
        assert 'test_func' not in CacheManager._cache_store

    def test_cache_data_with_args(self):
        """Test that cache works with function arguments."""
        call_count = 0

        @CacheManager.cache_data()
        def test_func(x, y):
            nonlocal call_count
            call_count += 1
            return x + y

        result1 = test_func(1, 2)
        assert result1 == 3
        assert call_count == 1

        # Second call with same args should use cache
        result2 = test_func(1, 2)
        assert result2 == 3
        assert call_count == 1

    def test_cache_data_no_ttl(self):
        """Test caching without TTL (cache never expires)."""
        @CacheManager.cache_data()
        def test_func():
            return "persistent_result"

        result = test_func()
        assert result == "persistent_result"

        # Verify TTL is None
        assert 'test_func' in CacheManager._cache_store
        assert CacheManager._cache_store['test_func']['ttl'] is None


class TestCacheAliasBehavior:
    """Test cache alias functionality."""

    def setup_method(self):
        """Clear cache before each test."""
        CacheManager.clear_cache()

    def teardown_method(self):
        """Clear cache after each test."""
        CacheManager.clear_cache()

    def test_cache_alias_basic_usage(self):
        """Test basic usage of cache alias."""
        call_count = 0

        @cache()
        def test_func():
            nonlocal call_count
            call_count += 1
            return "aliased_result"

        result1 = test_func()
        assert result1 == "aliased_result"
        assert call_count == 1

        result2 = test_func()
        assert result2 == "aliased_result"
        assert call_count == 1

    def test_cache_alias_with_ttl(self):
        """Test cache alias with TTL parameter."""
        @cache(expires_after=120)
        def test_func():
            return "result"

        result = test_func()
        assert result == "result"
        assert CacheManager._cache_store['test_func']['ttl'] == 120.0

    def test_cache_alias_with_timedelta(self):
        """Test cache alias with timedelta parameter."""
        @cache(expires_after=timedelta(hours=1))
        def test_func():
            return "result"

        result = test_func()
        assert result == "result"
        # 1 hour = 3600 seconds
        assert CacheManager._cache_store['test_func']['ttl'] == 3600.0


class TestClearCache:
    """Test cache clearing functionality."""

    def setup_method(self):
        """Clear cache before each test."""
        CacheManager.clear_cache()

    def test_clear_specific_cache_key(self):
        """Test clearing specific cache key."""
        @CacheManager.cache_data(key="key1")
        def func1():
            return "result1"

        @CacheManager.cache_data(key="key2")
        def func2():
            return "result2"

        func1()
        func2()

        assert 'key1' in CacheManager._cache_store
        assert 'key2' in CacheManager._cache_store

        CacheManager.clear_cache(key="key1")

        assert 'key1' not in CacheManager._cache_store
        assert 'key2' in CacheManager._cache_store

    def test_clear_all_cache(self):
        """Test clearing all cache."""
        @CacheManager.cache_data()
        def func1():
            return "result1"

        @CacheManager.cache_data()
        def func2():
            return "result2"

        func1()
        func2()

        assert len(CacheManager._cache_store) > 0

        CacheManager.clear_cache()

        assert len(CacheManager._cache_store) == 0


class TestTTLConversionLogic:
    """Test TTL conversion logic for different input types."""

    def setup_method(self):
        """Clear cache before each test."""
        CacheManager.clear_cache()

    def teardown_method(self):
        """Clear cache after each test."""
        CacheManager.clear_cache()

    def test_ttl_int_conversion(self):
        """Test TTL conversion from int to float."""
        @CacheManager.cache_data(expires_after=100)
        def test_func():
            return "result"

        test_func()
        stored_ttl = CacheManager._cache_store['test_func']['ttl']
        assert isinstance(stored_ttl, float)
        assert stored_ttl == 100.0

    def test_ttl_float_preservation(self):
        """Test TTL float value is preserved."""
        @CacheManager.cache_data(expires_after=99.99)
        def test_func():
            return "result"

        test_func()
        stored_ttl = CacheManager._cache_store['test_func']['ttl']
        assert isinstance(stored_ttl, float)
        assert stored_ttl == 99.99

    def test_ttl_timedelta_seconds_conversion(self):
        """Test timedelta conversion to seconds."""
        @CacheManager.cache_data(expires_after=timedelta(seconds=45))
        def test_func():
            return "result"

        test_func()
        stored_ttl = CacheManager._cache_store['test_func']['ttl']
        assert stored_ttl == 45.0

    def test_ttl_timedelta_minutes_conversion(self):
        """Test timedelta minutes conversion to seconds."""
        @CacheManager.cache_data(expires_after=timedelta(minutes=10))
        def test_func():
            return "result"

        test_func()
        stored_ttl = CacheManager._cache_store['test_func']['ttl']
        assert stored_ttl == 600.0

    def test_ttl_timedelta_hours_conversion(self):
        """Test timedelta hours conversion to seconds."""
        @CacheManager.cache_data(expires_after=timedelta(hours=2))
        def test_func():
            return "result"

        test_func()
        stored_ttl = CacheManager._cache_store['test_func']['ttl']
        assert stored_ttl == 7200.0

    def test_ttl_timedelta_days_conversion(self):
        """Test timedelta days conversion to seconds."""
        @CacheManager.cache_data(expires_after=timedelta(days=1))
        def test_func():
            return "result"

        test_func()
        stored_ttl = CacheManager._cache_store['test_func']['ttl']
        assert stored_ttl == 86400.0

    def test_ttl_timedelta_complex_conversion(self):
        """Test complex timedelta conversion to seconds."""
        # 1 day, 2 hours, 30 minutes, 15 seconds
        complex_delta = timedelta(days=1, hours=2, minutes=30, seconds=15)

        @CacheManager.cache_data(expires_after=complex_delta)
        def test_func():
            return "result"

        test_func()
        stored_ttl = CacheManager._cache_store['test_func']['ttl']
        # 86400 + 7200 + 1800 + 15 = 95415 seconds
        assert stored_ttl == 95415.0

    def test_ttl_none_no_conversion(self):
        """Test that None TTL remains None (no expiration)."""
        @CacheManager.cache_data(expires_after=None)
        def test_func():
            return "result"

        test_func()
        stored_ttl = CacheManager._cache_store['test_func']['ttl']
        assert stored_ttl is None

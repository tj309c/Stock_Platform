from src.core.cache_manager import CacheManager

def test_cache_market_data_decorator_cache():
    calls = {"count": 0}
    @CacheManager.cache_market_data
    def add(x):
        calls["count"] += 1
        return x + 1

    assert add(1) == 2
    assert add(1) == 2
    assert calls["count"] == 1

def test_cache_market_data_decorator_with_ttl():
    calls = {"count": 0}
    @CacheManager.cache_market_data(ttl=1)
    def add(x):
        calls["count"] += 1
        return x + 1

    assert add(2) == 3
    assert add(2) == 3
    assert calls["count"] == 1
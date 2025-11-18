# Stock_Platform

ADVANCED PLATFORM with caching capabilities

## Features

- **CacheManager**: A flexible caching system with decorator-based API
- **cache_data decorator**: Cache function results with optional TTL and key prefixes
- **Module-level alias**: Import `cache` directly for convenient usage

## Installation

```bash
# Clone the repository
git clone https://github.com/tj309c/Stock_Platform.git
cd Stock_Platform
```

## Usage

### Class-based approach

```python
from src.cache_manager import CacheManager

manager = CacheManager()

@manager.cache_data(ttl=60)  # Cache for 60 seconds
def fetch_stock_price(symbol):
    # Expensive operation
    return get_price_from_api(symbol)
```

### Module-level alias

```python
from src.cache_manager import cache

@cache(ttl=60, key_prefix="stocks")
def calculate_portfolio_value(stocks):
    # Expensive calculation
    return sum(stocks.values())
```

## API Reference

### CacheManager

#### `cache_data(ttl=None, key_prefix=None)`

Decorator to cache function results.

**Parameters:**
- `ttl` (int, optional): Time to live in seconds. Cache expires after this duration.
- `key_prefix` (str, optional): Prefix for cache keys to avoid collisions.

**Returns:**
- A decorator function that caches the wrapped function's results.

#### `clear_cache()`

Clear all cached data.

#### `get_cache_size()`

Get the number of items currently in the cache.

**Returns:**
- Number of cached items (int).

### Module-level alias

The `cache` function is a convenient alias for the default CacheManager's `cache_data` method:

```python
from src.cache_manager import cache
```

## Running Tests

```bash
python -m unittest tests.test_cache_manager -v
```

## Example

See `example_usage.py` for a complete working example.

```bash
python example_usage.py
```

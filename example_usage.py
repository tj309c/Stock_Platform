"""Example usage of CacheManager and cache decorator.

Demonstrates both the class-based and module-level alias approaches.
"""

from src.cache_manager import CacheManager, cache


def example_class_based():
    """Example using CacheManager class."""
    print("=== Example: Class-based CacheManager ===")
    
    manager = CacheManager()
    
    @manager.cache_data(ttl=5)
    def fetch_stock_price(symbol):
        """Simulates fetching stock price (expensive operation)."""
        print(f"  -> Fetching price for {symbol}...")
        return {"symbol": symbol, "price": 150.25}
    
    # First call - will execute function
    print("\n1. First call to fetch_stock_price('AAPL'):")
    result1 = fetch_stock_price("AAPL")
    print(f"   Result: {result1}")
    
    # Second call - will use cache
    print("\n2. Second call to fetch_stock_price('AAPL'):")
    result2 = fetch_stock_price("AAPL")
    print(f"   Result: {result2} (from cache)")
    
    print(f"\n   Cache size: {manager.get_cache_size()}")


def example_module_level_alias():
    """Example using module-level cache alias."""
    print("\n\n=== Example: Module-level cache alias ===")
    
    @cache(key_prefix="stock")
    def calculate_portfolio_value(stocks, prices):
        """Calculate total portfolio value."""
        print(f"  -> Calculating portfolio value...")
        return sum(stocks[s] * prices[s] for s in stocks)
    
    stocks = {"AAPL": 10, "GOOGL": 5}
    prices = {"AAPL": 150.25, "GOOGL": 2800.50}
    
    # First call - will execute function
    print("\n1. First call to calculate_portfolio_value:")
    result1 = calculate_portfolio_value(stocks, prices)
    print(f"   Total value: ${result1:.2f}")
    
    # Second call - will use cache
    print("\n2. Second call with same arguments:")
    result2 = calculate_portfolio_value(stocks, prices)
    print(f"   Total value: ${result2:.2f} (from cache)")


if __name__ == "__main__":
    example_class_based()
    example_module_level_alias()
    print("\n" + "="*50)
    print("✓ All examples completed successfully!")

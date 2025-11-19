import ccxt
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Prefer Binance as the default exchange, but accept coinbase env names for backwards compatibility
exchange = ccxt.kraken(
    {
    'apiKey': os.getenv('KRAKEN_API_KEY') or os.getenv('KRAKEN_API_NAME') or os.getenv('KRAKEN_KEY') or os.getenv('BINANCE_API_KEY') or os.getenv('BINANCE_API_NAME') or os.getenv('BINANCE_KEY') or os.getenv('COINBASE_API_NAME') or os.getenv('COINBASE_API_KEY') or os.getenv('COINBASE_KEY'),
    'secret': os.getenv('KRAKEN_API_SECRET') or os.getenv('KRAKEN_PRIVATE_KEY') or os.getenv('KRAKEN_SECRET') or os.getenv('BINANCE_API_SECRET') or os.getenv('BINANCE_PRIVATE_KEY') or os.getenv('BINANCE_SECRET') or os.getenv('COINBASE_PRIVATE_KEY') or os.getenv('COINBASE_API_SECRET') or os.getenv('COINBASE_SECRET'),
    'password': os.getenv('KRAKEN_API_PASSWORD') or os.getenv('KRAKEN_PASSWORD') or os.getenv('KRAKEN_PASSPHRASE') or os.getenv('BINANCE_API_PASSWORD') or os.getenv('BINANCE_PASSWORD') or os.getenv('BINANCE_PASSPHRASE') or os.getenv('COINBASE_API_PASSWORD') or os.getenv('COINBASE_PASSWORD') or os.getenv('COINBASE_PASSPHRASE'),
     'enableRateLimit': True})

exchange.verbose = True
print(exchange.fetch_balance()) 
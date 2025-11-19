import ccxt
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

exchange = ccxt.coinbase(
    {
     'apiKey': os.getenv('COINBASE_API_NAME') or os.getenv('COINBASE_API_KEY') or os.getenv('COINBASE_KEY'),
     'secret': os.getenv('COINBASE_PRIVATE_KEY') or os.getenv('COINBASE_API_SECRET') or os.getenv('COINBASE_SECRET'),
     'password': os.getenv('COINBASE_API_PASSWORD') or os.getenv('COINBASE_PASSWORD') or os.getenv('COINBASE_PASSPHRASE'),
     'enableRateLimit': True})

exchange.verbose = True
print(exchange.fetch_balance()) 
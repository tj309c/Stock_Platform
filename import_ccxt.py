import ccxt
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

exchange = ccxt.coinbase(
    {
     'apiKey': os.getenv('COINBASE_API_KEY'),
     'secret': os.getenv('COINBASE_SECRET'),
     'enableRateLimit': True})

exchange.verbose = True
print(exchange.fetch_balance()) 
import unittest
from unittest.mock import patch, MagicMock
import ccxt
import pandas as pd
from src.pipelines.get_crypto_data import CryptoDataPipeline

class TestCryptoDataPipeline(unittest.TestCase):

    @patch('src.pipelines.get_crypto_data.get_secret')
    @patch('ccxt.kraken')
    def test_get_exchange_with_creds(self, mock_ccxt_kraken, mock_get_secret):
        """
        Test that the exchange is initialized with API credentials when they are found.
        """
        # Arrange: Mock secrets and the ccxt exchange class
        mock_get_secret.side_effect = ['test_api_key', 'test_api_secret']
        mock_exchange_instance = MagicMock()
        mock_ccxt_kraken.return_value = mock_exchange_instance

        # Act: Initialize the pipeline
        pipeline = CryptoDataPipeline(exchange_id='kraken')

        # Assert: Check that the exchange was initialized with the correct config
        self.assertIsNotNone(pipeline.exchange)
        mock_ccxt_kraken.assert_called_with({
            'apiKey': 'test_api_key',
            'secret': 'test_api_secret',
        })

    @patch('src.pipelines.get_crypto_data.get_secret')
    @patch('ccxt.kraken')
    def test_get_exchange_public_mode(self, mock_ccxt_kraken, mock_get_secret):
        """
        Test that the exchange is initialized in public mode when no credentials are found.
        """
        # Arrange: Mock secrets to return None
        mock_get_secret.return_value = None
        mock_exchange_instance = MagicMock()
        mock_ccxt_kraken.return_value = mock_exchange_instance

        # Act: Initialize the pipeline
        pipeline = CryptoDataPipeline(exchange_id='kraken')

        # Assert: Check that the exchange was initialized without arguments
        self.assertIsNotNone(pipeline.exchange)
        mock_ccxt_kraken.assert_called_with()

    def test_get_crypto_price_success(self):
        """
        Test successful fetching and processing of OHLCV data.
        """
        # Arrange: Create a pipeline instance without initializing the exchange
        # We can do this by patching the __init__ method or just creating it and replacing the exchange property
        with patch.object(CryptoDataPipeline, '_get_exchange', return_value=None):
            pipeline = CryptoDataPipeline(exchange_id='kraken')

        mock_exchange = MagicMock()
        
        # Sample data that fetch_ohlcv would return
        mock_ohlcv_data = [
            [1672531200000, 16500, 16600, 16400, 16550, 1000], # [timestamp, open, high, low, close, volume]
            [1672617600000, 16550, 16700, 16500, 16650, 1200],
        ]
        mock_exchange.fetch_ohlcv.return_value = mock_ohlcv_data
        pipeline.exchange = mock_exchange

        # Act: Call the method to get crypto prices
        df = pipeline.get_crypto_price(symbol='BTC/USD')

        # Assert: Check that the DataFrame is structured correctly
        self.assertIsInstance(df, pd.DataFrame)
        self.assertFalse(df.empty)
        self.assertEqual(len(df), 2)
        self.assertListEqual(list(df.columns), ['Open', 'High', 'Low', 'Close', 'Volume'])
        self.assertEqual(df.index.name, 'timestamp')
        self.assertEqual(df['Close'].iloc[0], 16550)

    def test_get_crypto_price_api_error(self):
        """
        Test that the method returns None when the API call fails.
        """
        # Arrange: Create a pipeline and mock the exchange to raise an error
        with patch.object(CryptoDataPipeline, '_get_exchange', return_value=None):
            pipeline = CryptoDataPipeline(exchange_id='kraken')

        mock_exchange = MagicMock()
        mock_exchange.fetch_ohlcv.side_effect = ccxt.NetworkError("API is down")
        pipeline.exchange = mock_exchange

        # Act: Call the method to get crypto prices
        df = pipeline.get_crypto_price(symbol='BTC/USD')

        # Assert: Check that the result is None
        self.assertIsNone(df)
        # Verify that our mock was called
        mock_exchange.fetch_ohlcv.assert_called_once_with('BTC/USD', timeframe='1d', limit=365)


if __name__ == '__main__':
    unittest.main()
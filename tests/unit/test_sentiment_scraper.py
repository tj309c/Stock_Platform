import pytest

from src.pipelines.get_sentiment_scraper import SentimentScraper


def test_get_sentiment_for_ticker_returns_structure():
    s = SentimentScraper()
    result = s.get_sentiment_for_ticker('AAPL')
    assert isinstance(result, dict)
    assert 'score' in result
    assert 'num_headlines' in result
    assert 'headlines' in result

import pytest
from src.pipelines.get_sentiment_scraper import SentimentScraper


def test_keyword_fallback_scoring():
    s = SentimentScraper()
    s.set_scoring_mode('keyword')
    sc_neg = s._score_headline('Company misses revenue and cuts guidance')
    sc_pos = s._score_headline('Company raises guidance and reports profit gains')
    assert isinstance(sc_neg, float)
    assert isinstance(sc_pos, float)
    assert sc_neg <= 0
    assert sc_pos >= 0


def test_vader_scoring_if_available(monkeypatch):
    # Skip this test if VADER is not installed
    pytest.importorskip('vaderSentiment.vaderSentiment')
    s = SentimentScraper()
    s.set_scoring_mode('vader')
    sc_pos = s._score_headline('Company raises guidance and reports profit gains')
    sc_neg = s._score_headline('Company misses revenue and issues a downward guidance')
    assert isinstance(sc_pos, float)
    assert isinstance(sc_neg, float)
    assert sc_pos > sc_neg


def test_textblob_scoring_if_available(monkeypatch):
    pytest.importorskip('textblob')
    s = SentimentScraper()
    s.set_scoring_mode('textblob')
    sc_pos = s._score_headline('Company raises guidance and reports profit gains')
    sc_neg = s._score_headline('Company misses revenue and issues a downward guidance')
    assert isinstance(sc_pos, float)
    assert isinstance(sc_neg, float)
    assert sc_pos > sc_neg

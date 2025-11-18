import pytest
from src.pipelines.get_sentiment_scraper import SentimentScraper
from src.core.config import AppConfig


def test_scoring_mode_persistence(tmp_path, monkeypatch):
    monkeypatch.setattr(AppConfig, 'DATA_DIR', tmp_path)
    monkeypatch.setattr(AppConfig, 'CACHE_DIR', tmp_path / 'cache')
    s = SentimentScraper()
    assert s.get_scoring_mode() == 'auto'
    assert s.set_scoring_mode('llm', scope='equity')
    assert s.get_scoring_mode(scope='equity') == 'llm'


def test_llm_mode_fallback_to_vader(monkeypatch):
    s = SentimentScraper()
    # Make VADER available if not real; monkeypatch analyzer so we get deterministic output
    class DummyAnalyzer:
        def polarity_scores(self, text):
            return {'compound': 0.6}
    monkeypatch.setattr(s, 'analyzer', DummyAnalyzer())
    # Force scoring_mode to llm
    s.scoring_mode = 'llm'

    # Monkeypatch the LLM scorer to return None to force fallback
    import src.pipelines.llm_scoring as llm
    monkeypatch.setattr(llm, 'score_text_with_llm', lambda text: None)
    # Ensure TextBlob is not used in fallback to avoid mixed averages
    import src.pipelines.get_sentiment_scraper as gs
    monkeypatch.setattr(gs, 'HAS_TEXTBLOB', False)
    # Should fall back to VADER and produce a score ~0.6
    score = s._score_headline('Company beats expectations')
    assert abs(score - 0.6) < 1e-6

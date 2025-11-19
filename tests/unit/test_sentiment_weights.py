from src.pipelines.get_sentiment_scraper import SentimentScraper, DEFAULT_SOURCE_WEIGHTS


def test_weighting_influence(monkeypatch):
    s = SentimentScraper()
    # MarketWatch is removed, so we'll use Yahoo as the negative source
    headlines = [
        {'source': 'Finviz', 'title': 'Company beats expectations'},
        {'source': 'Yahoo', 'title': 'Company reports losses and layoffs'},
    ]

    # First: default weights roughly equal => score around neutral
    agg_default = s._aggregate_scores(headlines)
    default_score = agg_default['overall']

    # Now set weights strongly to Finviz only
    high_finviz_weights = {'Finviz': 1.0, 'Yahoo': 0.0, 'SEC': 0.0} # noqa
    agg_f = s._aggregate_scores(headlines, source_weights=high_finviz_weights)
    assert abs(agg_f['overall'] - agg_f['per_source']['Finviz']['score']) < 1e-6

    # Now set weights strongly to Yahoo only
    high_mw_weights = {'Finviz': 0.0, 'Yahoo': 1.0, 'SEC': 0.0} # noqa
    agg_mw = s._aggregate_scores(headlines, source_weights=high_mw_weights)
    assert abs(agg_mw['overall'] - agg_mw['per_source']['Yahoo']['score']) < 1e-6

    # Ensure default score is between the extremes
    assert min(agg_f['overall'], agg_mw['overall']) <= default_score <= max(agg_f['overall'], agg_mw['overall'])


def test_load_and_save_weights_persistence(tmp_path, monkeypatch):
    # Ensure we use a temp directory for DATA_DIR for persistence to avoid impacting user data
    from src.core.config import AppConfig
    monkeypatch.setattr(AppConfig, 'DATA_DIR', tmp_path)
    monkeypatch.setattr(AppConfig, 'CACHE_DIR', tmp_path / 'cache')
    # Create a new scraper and ensure defaults are present
    s = SentimentScraper()
    weights = s.get_weights()
    assert isinstance(weights, dict)
    assert set(weights.keys()) == set(DEFAULT_SOURCE_WEIGHTS.keys())

    # Save custom weights and verify they persist across new instances
    custom = {'Finviz': 0.7, 'Yahoo': 0.2, 'SEC': 0.1} # noqa
    assert s.set_weights(custom)

    s2 = SentimentScraper()
    loaded = s2.get_weights()
    # numeric equality
    for k in custom:
        assert abs(loaded[k] - custom[k]) < 1e-6

    # Reset to default
    assert s2.reset_weights_to_default()
    s3 = SentimentScraper()
    loaded2 = s3.get_weights()
    for k, v in DEFAULT_SOURCE_WEIGHTS.items():
        assert abs(loaded2[k] - v) < 1e-6


def test_set_weights_rejects_all_zero(tmp_path, monkeypatch):
    from src.core.config import AppConfig
    monkeypatch.setattr(AppConfig, 'DATA_DIR', tmp_path)
    monkeypatch.setattr(AppConfig, 'CACHE_DIR', tmp_path / 'cache')
    s = SentimentScraper()
    zero_weights = {'Finviz': 0.0, 'Yahoo': 0.0, 'SEC': 0.0} # noqa
    assert s.set_weights(zero_weights) is False


def test_aggregate_uses_persisted_weights(tmp_path, monkeypatch):
    from src.core.config import AppConfig
    monkeypatch.setattr(AppConfig, 'DATA_DIR', tmp_path)
    monkeypatch.setattr(AppConfig, 'CACHE_DIR', tmp_path / 'cache')
    s = SentimentScraper()
    # Two headlines: Finviz positive, Yahoo negative
    headlines = [
        {'source': 'Finviz', 'title': 'Company raises guidance and beats'},
        {'source': 'Yahoo', 'title': 'Company reports losses and layoffs'}
    ]
    # Capture default for comparison
    agg_default = s._aggregate_scores(headlines)
    # Save weights to favor Finviz
    weights = {'Finviz': 0.9, 'Yahoo': 0.08, 'SEC': 0.02} # noqa
    assert s.set_weights(weights)
    # Now run aggregate without passing explicit weights
    agg = s._aggregate_scores(headlines)
    # The overall should be roughly equal to Finviz per_source score when heavily weighted
    finviz_score = agg['per_source']['Finviz']['score']
    # The these weighted aggregated value should be closer to finviz score than the default
    assert abs(agg['overall'] - finviz_score) <= abs(agg_default['overall'] - finviz_score)


def test_saving_weights_changes_reported_sentiment(tmp_path, monkeypatch):
    from src.core.config import AppConfig
    monkeypatch.setattr(AppConfig, 'DATA_DIR', tmp_path)
    monkeypatch.setattr(AppConfig, 'CACHE_DIR', tmp_path / 'cache')
    s = SentimentScraper()
    # Monkeypatch the gather headlines to return a fixed set of headlines
    def fake_gather_with_status(self, ticker, sources=None):
        headlines = [
            {'source': 'Finviz', 'title': 'Company beats expectations', 'score': 0.5},
            {'source': 'Yahoo', 'title': 'Company reports losses and layoffs', 'score': -0.5},
        ]
        return headlines, {h['source']: {'state': 'ok'} for h in headlines}
    monkeypatch.setattr(SentimentScraper, '_gather_headlines_with_status', fake_gather_with_status)

    # Begin with defaults
    res1 = s.get_sentiment_for_ticker('AAPL')
    default_score = res1['score']

    # Save weights favoring Finviz strongly
    weights = {'Finviz': 1.0, 'Yahoo': 0.0, 'SEC': 0.0} # noqa
    assert s.set_weights(weights)
    # Clear cache to force recompute
    s.clear_cache()
    res2 = s.get_sentiment_for_ticker('AAPL')
    assert abs(res2['score'] - res2['per_source']['Finviz']['score']) < 1e-6
    # Score should now be close to finviz score and might differ from default_score
    assert abs(res2['score'] - default_score) > 1e-6


def test_sentimentscraper_scope_gets_saved_weights(tmp_path, monkeypatch):
    from src.core.config import AppConfig
    monkeypatch.setattr(AppConfig, 'DATA_DIR', tmp_path)
    monkeypatch.setattr(AppConfig, 'CACHE_DIR', tmp_path / 'cache')
    s = SentimentScraper()
    # Save equity scope weights using SentimentScraper.set_weights
    weights = {'Finviz': 0.8, 'Yahoo': 0.15, 'SEC': 0.05} # noqa
    assert s.set_weights(weights, scope='equity')
    s2 = SentimentScraper()
    # Even though the instance uses 'global' by default, get_weights with scope should return equity weights
    loaded = s2.get_weights(scope='equity')
    assert abs(loaded['Finviz'] - 0.8) < 1e-6

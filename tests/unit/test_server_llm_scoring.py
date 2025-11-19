import pytest
from src.server import settings_server
from src.pipelines import llm_scoring
from src.core.config import AppConfig


def test_server_score_endpoint(monkeypatch, tmp_path):
    # point server cache to a temporary file to avoid influencing other tests
    monkeypatch.setattr(settings_server, 'LLM_CACHE_FILE', tmp_path / 'llm_cache.json')
    client = settings_server.app.test_client()

    # fake LLM scoring to ensure non-empty results
    def fake_batch_score(texts):
        return [0.1 * (i + 1) for i in range(len(texts))]
    monkeypatch.setattr(llm_scoring, 'score_texts_with_llm', fake_batch_score)

    r = client.post('/score', json={'texts': ['a', 'b']})
    assert r.status_code == 200
    data = r.get_json()
    assert 'scores' in data
    assert len(data['scores']) == 2
    assert data['scores'][0] == 0.1

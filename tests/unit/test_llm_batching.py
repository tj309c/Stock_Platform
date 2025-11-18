import pytest
from src.pipelines.llm_scoring import score_texts_with_llm


def test_llm_batch_parsing(monkeypatch):
    # Simulate OpenAI's response as multiple lines of numerical scores
    def fake_chat_create(model, messages, max_tokens):
        # Return a JSON with scores
        return {'choices': [{'message': {'content': '{"scores": [0.6, -0.2, 0.1]}'}}]}

    monkeypatch.setattr('openai.ChatCompletion.create', fake_chat_create)

    texts = ['a', 'b', 'c']
    res = score_texts_with_llm(texts)
    assert isinstance(res, list)
    assert len(res) == 3
    assert res[0] == 0.6
    assert res[1] == -0.2
    assert res[2] == 0.1

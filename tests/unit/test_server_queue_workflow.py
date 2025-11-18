import time
import threading
from src.server import settings_server as server
from src.core.queue_manager import QueueManager
from src.server.llm_worker import Worker
import src.pipelines.llm_scoring as llm_scoring
import json


def test_queue_endpoint_with_worker(monkeypatch, tmp_path):
    qm = QueueManager(queue_dir=tmp_path)
    monkeypatch.setattr(server, 'get_global_queue_manager', lambda: qm)

    # monkeypatch llm scoring to produce deterministic outputs
    def fake_score_texts_with_llm(texts):
        return [0.42 for _ in texts]
    monkeypatch.setattr(llm_scoring, 'score_texts_with_llm', fake_score_texts_with_llm)

    client = server.app.test_client()
    resp = client.post('/score/submit', data=json.dumps({'texts': ['alpha', 'beta']}), content_type='application/json')
    assert resp.status_code == 200
    job_id = resp.get_json()['job_id']

    w = Worker(queue_manager=qm, max_batch=4, wait_timeout=0.01)

    t = threading.Thread(target=w.process_once)
    t.start()
    t.join(timeout=2)

    # poll until complete
    attempts = 0
    status = None
    while attempts < 20:
        p = client.get(f'/score/poll/{job_id}')
        body = p.get_json()
        status = body['status']
        if status == 'complete':
            break
        attempts += 1
        time.sleep(0.05)
    assert status == 'complete'
    res = body['result']
    assert 'scores' in res
    assert len(res['scores']) == 2

from src.server import settings_server as server
from src.core.queue_manager import QueueManager
import json


def test_submit_and_poll_job(monkeypatch, tmp_path):
    # Use a fresh queue manager directory and monkeypatch the global get_global_queue_manager
    qm = QueueManager(queue_dir=tmp_path)
    monkeypatch.setattr(server, 'get_global_queue_manager', lambda: qm)

    client = server.app.test_client()
    resp = client.post('/score/submit', data=json.dumps({'texts': ['alpha', 'beta']}), content_type='application/json')
    assert resp.status_code == 200
    body = resp.get_json()
    job_id = body.get('job_id')
    assert job_id

    # poll job: initially queued
    p = client.get(f'/score/poll/{job_id}')
    assert p.status_code == 200
    pb = p.get_json()
    assert pb['status'] in ('queued', 'processing', 'complete')

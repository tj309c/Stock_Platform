import pytest
from pathlib import Path
from src.core.queue_manager import QueueManager


def test_queue_enqueue_pop_complete_and_fail(tmp_path):
    qm = QueueManager(queue_dir=tmp_path)
    job_id = qm.enqueue({'texts': ['hello', 'world']})
    assert isinstance(job_id, str)
    j = qm.get_job(job_id)
    assert j is not None
    assert j['status'] == 'queued'

    # pop and claim
    claimed = qm.pop_next()
    assert claimed is not None
    assert claimed['id'] == job_id
    assert claimed['status'] == 'processing'
    assert claimed['attempts'] == 1

    # complete job
    ok = qm.complete_job(job_id, {'scores': [0.1, -0.1]})
    assert ok
    t = qm.get_job(job_id)
    assert t['status'] == 'complete'
    assert t['result']['scores'][0] == 0.1

    # enqueue another job and fail it
    job_id2 = qm.enqueue({'texts': ['failcase']})
    claimed2 = qm.pop_next()
    assert claimed2['id'] == job_id2
    qm.fail_job(job_id2, 'test failure')
    fj = qm.get_job(job_id2)
    assert fj['status'] == 'failed'

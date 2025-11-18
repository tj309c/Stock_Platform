from src.server.llm_worker import Worker
from src.core.queue_manager import QueueManager
import src.pipelines.llm_scoring as llm_scoring


def test_worker_batches_and_writes_results(monkeypatch, tmp_path):
    qm = QueueManager(queue_dir=tmp_path)
    job1 = qm.enqueue({'texts': ['t1', 't2']})
    job2 = qm.enqueue({'texts': ['t3']})

    # monkeypatch llm scoring to produce deterministic outputs
    def fake_score_texts_with_llm(texts):
        return [0.1 * (i+1) for i,_ in enumerate(texts)]
    monkeypatch.setattr(llm_scoring, 'score_texts_with_llm', fake_score_texts_with_llm)

    w = Worker(queue_manager=qm, max_batch=4)
    processed = w.process_once()
    assert processed == 2
    # check job1 result
    j1 = qm.get_job(job1)
    assert j1['status'] == 'complete'
    assert j1['result']['scores'] == [0.1, 0.2]
    j2 = qm.get_job(job2)
    assert j2['result']['scores'] == [0.30000000000000004] or j2['result']['scores'] == [0.3]


def test_worker_run_once_exits_and_processes_one_batch(monkeypatch, tmp_path):
    from time import perf_counter
    qm = QueueManager(queue_dir=tmp_path)
    job1 = qm.enqueue({'texts': ['hello']})

    # monkeypatch llm scoring to produce deterministic outputs
    def fake_score_texts_with_llm(texts):
        return [0.42 for _ in texts]
    monkeypatch.setattr(llm_scoring, 'score_texts_with_llm', fake_score_texts_with_llm)

    w = Worker(queue_manager=qm, max_batch=8)
    start = perf_counter()
    # Run once should process the available job then exit quickly
    w.run(once=True)
    elapsed = perf_counter() - start
    assert elapsed < 2, "once-mode should return quickly"
    j1 = qm.get_job(job1)
    assert j1['status'] == 'complete'
    assert j1['result']['scores'] == [0.42]

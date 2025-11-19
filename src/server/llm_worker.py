"""
llm_worker.py

Background worker that polls the QueueManager and handles LLM scoring jobs. Exposes a `Worker`
class with a `process_once` method used for single-iteration processing (great for tests) and a
`run` loop for continuous processing.
"""
from __future__ import annotations

import time
import logging
from typing import List, Dict, Any

from src.core.queue_manager import get_global_queue_manager, QueueManager
import src.pipelines.llm_scoring as llm_scoring

logger = logging.getLogger(__name__)


class Worker:
    def __init__(self, queue_manager: QueueManager = None, max_batch: int = 8, wait_timeout: float = 0.25):
        self.qm = queue_manager or get_global_queue_manager()
        self.max_batch = max_batch
        self.wait_timeout = wait_timeout
        self.running = False

    def _gather_batch(self) -> List[Dict[str, Any]]:
        batch = []
        # pop at most max_batch jobs
        while len(batch) < self.max_batch:
            j = self.qm.pop_next()
            if not j:
                break
            batch.append(j)
            # short wait to allow other producers
            time.sleep(0)
        return batch

    def process_once(self):
        batch = self._gather_batch()
        if not batch:
            return 0
        # flatten texts and track indices
        texts = []
        mapping = []  # list of tuples (job_id, index_within_job)
        for job in batch:
            payload = job.get('payload') or {}
            tlist = payload.get('texts') or (payload.get('text') and [payload.get('text')]) or []
            for idx, t in enumerate(tlist):
                mapping.append((job['id'], idx))
                texts.append(t)
        if not texts:
            # nothing to score; mark as complete
            for job in batch:
                self.qm.complete_job(job['id'], {'scores': []})
            return len(batch)

        try:
            scores = llm_scoring.score_texts_with_llm(texts)
            # partition results by job
            # build mapping from job -> list
            per_job: Dict[str, List[Any]] = {}
            for (job_id, idx), s in zip(mapping, scores):
                per_job.setdefault(job_id, []).append(s)
            # write results
            for job in batch:
                self.qm.complete_job(job['id'], {'scores': per_job.get(job['id'], [])})
        except Exception as ex:
            logger.exception("LLM worker failed to score batch: %s", ex)
            # Fail each job
            for job in batch:
                self.qm.fail_job(job['id'], str(ex))
        return len(batch)

    def run(self, once: bool = False):
        """
        Run the worker loop. If once=True, run a single pass via process_once() then exit (useful for tests/CI).
        """
        if once:
            # single iteration and exit
            try:
                processed = self.process_once()
                logger.info("Once-mode: processed %s job(s)", processed)
            except Exception as ex:
                logger.exception("Exception while processing single-run worker: %s", ex)
            return

        self.running = True
        while self.running:
            try:
                processed = self.process_once()
                if processed == 0:
                    time.sleep(self.wait_timeout)
            except KeyboardInterrupt:
                break

    def stop(self):
        self.running = False

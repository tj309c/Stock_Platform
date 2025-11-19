"""
queue_manager.py

A simple disk-backed job queue manager suitable for development & test use. Jobs are stored
as JSON files in a queue directory (default: data/queue). Each job has an id, status and
payload and is visible through API methods. The implementation is intentionally simple
(atomic file write + claim by updating job status) and intended for local or single-worker
usage; production use should swap-in Redis or a true message queue.
"""
from __future__ import annotations

import json
import uuid
from pathlib import Path
from typing import Any, Dict, Optional, List
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class QueueManager:
    def __init__(self, queue_dir: Optional[Path] = None, redis_url: Optional[str] = None):
        base = Path(__file__).parent.parent
        self.queue_dir = (queue_dir or base / 'data' / 'queue')
        self.queue_dir.mkdir(parents=True, exist_ok=True)
        self.redis_url = redis_url
        self.redis_client = None
        # Try to initialize a Redis client if redis_url provided
        if redis_url:
            try:
                import redis
                self.redis_client = redis.from_url(redis_url, decode_responses=True)
                # quick test
                self.redis_client.ping()
                self.backend = 'redis'
            except Exception as ex:
                logger.warning("Failed to connect to Redis at %s; falling back to disk queue: %s", redis_url, ex)
                self.redis_client = None
                self.backend = 'disk'
        else:
            self.backend = 'disk'

    def _job_path(self, job_id: str) -> Path:
        return self.queue_dir / f"{job_id}.json"

    def enqueue(self, payload: Dict[str, Any]) -> str:
        job_id = str(uuid.uuid4())
        job = {
            'id': job_id,
            'status': 'queued',
            'payload': payload,
            'result': None,
            'attempts': 0,
            'created_at': datetime.utcnow().isoformat(),
            'updated_at': datetime.utcnow().isoformat(),
        }
        if self.backend == 'redis' and self.redis_client is not None:
            # Store job JSON in Redis and push id to queue list
            self.redis_client.set(f"job:{job_id}", json.dumps(job))
            self.redis_client.lpush('queue', job_id)
        else:
            with open(self._job_path(job_id), 'w', encoding='utf-8') as fh:
                json.dump(job, fh)
        return job_id

    def get_job(self, job_id: str) -> Optional[Dict[str, Any]]:
        if self.backend == 'redis' and self.redis_client is not None:
            val = self.redis_client.get(f"job:{job_id}")
            if not val:
                return None
            try:
                return json.loads(val)
            except Exception:
                return None
        p = self._job_path(job_id)
        if not p.exists():
            return None
        try:
            with open(p, 'r', encoding='utf-8') as fh:
                return json.load(fh)
        except Exception:
            return None

    def get_status(self, job_id: str) -> Optional[str]:
        j = self.get_job(job_id)
        return j.get('status') if j else None

    def list_jobs(self, status: Optional[str] = None) -> List[Dict[str, Any]]:
        jobs = []
        if self.backend == 'redis' and self.redis_client is not None:
            # Redis: list all jobs keys directly (not ideal for large systems)
            for key in self.redis_client.scan_iter(match='job:*'):
                try:
                    j = json.loads(self.redis_client.get(key))
                except Exception:
                    continue
                if status is None or j.get('status') == status:
                    jobs.append(j)
        else:
            for f in self.queue_dir.glob('*.json'):
                try:
                    with open(f, 'r', encoding='utf-8') as fh:
                        j = json.load(fh)
                    if status is None or j.get('status') == status:
                        jobs.append(j)
                except Exception:
                    continue
        return jobs

    def _write_job(self, job: Dict[str, Any]):
        # persist to selected backend
        job['updated_at'] = datetime.utcnow().isoformat()
        if self.backend == 'redis' and self.redis_client is not None:
            self.redis_client.set(f"job:{job['id']}", json.dumps(job))
        else:
            p = self._job_path(job['id'])
            with open(p, 'w', encoding='utf-8') as fh:
                json.dump(job, fh)

    def pop_next(self) -> Optional[Dict[str, Any]]:
        # Find oldest queued job and claim it by setting status=processing
        if self.backend == 'redis' and self.redis_client is not None:
            # Attempt a fast non-blocking pop from Redis queue
            job_id = None
            try:
                job_id = self.redis_client.rpoplpush('queue', 'processing')
            except Exception:
                # If redis pop fails, fall back to disk
                job_id = None
            if not job_id:
                return None
            job = self.get_job(job_id)
            if not job:
                return None
            job['status'] = 'processing'
            job['attempts'] = job.get('attempts', 0) + 1
            self._write_job(job)
            return job
        else:
            queued = self.list_jobs(status='queued')
            if not queued:
                return None
            queued.sort(key=lambda j: j.get('created_at') or '')
            job = queued[0]
            # update status
            job['status'] = 'processing'
            job['attempts'] = job.get('attempts', 0) + 1
            self._write_job(job)
            return job

    def complete_job(self, job_id: str, result: Any):
        job = self.get_job(job_id)
        if not job:
            return False
        job['status'] = 'complete'
        job['result'] = result
        self._write_job(job)
        if self.backend == 'redis' and self.redis_client is not None:
            try:
                # Remove job_id from processing list
                self.redis_client.lrem('processing', 0, job_id)
                # Add to completed list for reference
                self.redis_client.lpush('completed', job_id)
            except Exception:
                pass
        return True

    def fail_job(self, job_id: str, reason: str = ''):
        job = self.get_job(job_id)
        if not job:
            return False
        job['status'] = 'failed'
        job['result'] = {'error': reason}
        self._write_job(job)
        if self.backend == 'redis' and self.redis_client is not None:
            try:
                self.redis_client.lrem('processing', 0, job_id)
                self.redis_client.lpush('failed', job_id)
            except Exception:
                pass
        return True


# instantiate a default global queue for convenience
_global_queue_manager: Optional[QueueManager] = None

def get_global_queue_manager() -> QueueManager:
    global _global_queue_manager
    if _global_queue_manager is None:
        _global_queue_manager = QueueManager()
    return _global_queue_manager

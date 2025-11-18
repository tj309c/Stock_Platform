import os
import sys
import tempfile

# Ensure project root is on sys.path when running from scripts folder
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from src.core.queue_manager import QueueManager
from src.server.llm_worker import Worker
import src.pipelines.llm_scoring as llm_scoring

def main():
    from pathlib import Path
    qm = QueueManager(queue_dir=Path(tempfile.mkdtemp()))
    job = qm.enqueue({'texts': ['hello-world']})

    # monkeypatch the scoring function quickly
    llm_scoring.score_texts_with_llm = lambda texts: [0.42 for _ in texts]

    w = Worker(queue_manager=qm, max_batch=8)
    print('Starting worker in once mode...')
    w.run(once=True)
    j = qm.get_job(job)
    print('Job status:', j.get('status'), 'scores:', j.get('result', {}).get('scores'))

if __name__ == '__main__':
    import os, sys
    if os.environ.get('RUN_DEBUG_SCRIPTS') != '1':
        print("Developer-only script. Set RUN_DEBUG_SCRIPTS=1 to run this file.")
        sys.exit(0)
    main()

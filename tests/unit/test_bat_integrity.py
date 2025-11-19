import subprocess
import sys
import os
from pathlib import Path


def test_bat_files_integrity():
    repo_root = Path(__file__).resolve().parents[2]
    script = repo_root / 'scripts' / 'check_bat_files.py'
    assert script.exists(), 'Missing check script under scripts/'
    res = subprocess.run([sys.executable, str(script)], cwd=str(repo_root), capture_output=True, text=True)
    print(res.stdout)
    print(res.stderr)
    assert res.returncode == 0, 'check_bat_files.py reported issues with .bat files'

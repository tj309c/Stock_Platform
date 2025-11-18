"""
Quick pre-push checks for Git operations:
- Reports if current branch, uncommitted changes, and whether local branch differs from remote.
- Detects large files in the repo working tree > 50MB (warns but doesn't remove).
- Checks that common unwanted paths are ignored in .gitignore (venv, data/backups, .env, .streamlit/secrets.toml)
- Suggests recommended steps to create a backup branch and push safely.

This script is meant to be run locally by developers before pushing to GitHub. It is non-destructive.
"""
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

LARGE_FILE_THRESHOLD = 50 * 1024 * 1024  # 50 MB


def run_cmd(cmd):
    try:
        res = subprocess.check_output(cmd, stderr=subprocess.STDOUT, text=True)
        return res.strip()
    except Exception as e:
        return None


def check_git_status():
    status = run_cmd(["git", "status", "--porcelain", "--branch"])
    if status is None:
        print("Git not found or not available in PATH. Skipping git checks.")
        return
    print("--- Git Status ---")
    print(status)


def find_large_files():
    print("\n--- Large Files (> 50MB) ---")
    found = []
    for root, dirs, files in os.walk(ROOT):
        # skip typical directories that we don't care about
        if any(p in root for p in ['.git', '.venv', 'venv', 'data/cache', '__pycache__']):
            continue
        for f in files:
            try:
                fp = Path(root) / f
                if fp.stat().st_size > LARGE_FILE_THRESHOLD:
                    found.append((fp, fp.stat().st_size))
            except Exception:
                pass
    if not found:
        print("No very large files detected.")
    else:
        for fp, sz in sorted(found, key=lambda x: -x[1]):
            print(f"{fp} - {sz/1024/1024:.1f} MB")


def check_git_ignored_paths():
    print("\n--- .gitignore Checks ---")
    gi_path = ROOT / '.gitignore'
    if not gi_path.exists():
        print("No .gitignore file found.")
        return
    ignore_text = gi_path.read_text()
    required = ['venv/', '.venv/', 'data/backups/', '.streamlit/secrets.toml', '.env', '*.zip']
    for r in required:
        if r in ignore_text:
            print(f"OK: {r} present in .gitignore")
        else:
            print(f"WARNING: {r} not found in .gitignore")


def check_tracked_large_files():
    print("\n--- Tracked Large Files (git ls-files) ---")
    tracked = run_cmd(["git", "ls-files"]) or ''
    if not tracked:
        print("git ls-files could not be executed or repo has no tracked files. Skipping.")
        return
    tracked_files = tracked.splitlines()
    found = []
    for f in tracked_files:
        fp = Path(ROOT) / f
        if fp.exists():
            try:
                if fp.stat().st_size > LARGE_FILE_THRESHOLD:
                    found.append((fp, fp.stat().st_size))
            except Exception:
                pass
    if not found:
        print("No large tracked files detected.")
    else:
        for fp, sz in sorted(found, key=lambda x: -x[1]):
            print(f"TRACKED: {fp} - {sz/1024/1024:.1f} MB")


if __name__ == '__main__':
    print("Pre-push checks for Stock_Platform")
    check_git_status()
    find_large_files()
    check_git_ignored_paths()
    check_tracked_large_files()
    print('\nRecommended steps:')
    print(' 1) Save all work and commit to a local branch:')
    print('    git checkout -b backup/before-github && git add -A && git commit -m "Checkpoint before push"')
    print(' 2) Verify remote: git remote -v')
    print(" 3) Push the backup branch: git push -u origin backup/before-github")
    print(' 4) If you encounter large-file errors, remove or move large files out of the repo and add them to .gitignore.')
    print(' 5) If you have authentication problems, create a Personal Access Token (PAT) and configure credentials.')

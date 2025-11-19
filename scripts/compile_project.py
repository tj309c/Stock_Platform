"""
Compile project python files to detect syntax errors excluding .venv and other vendor dirs.
"""
from pathlib import Path
import py_compile
import sys

ROOT = Path(__file__).resolve().parents[1]
EXCLUDE_DIRS = {'.venv', 'venv', '.git', '__pycache__', '.pytest_cache'}

errors = []
for p in ROOT.rglob('*.py'):
    # skip files in excluded dirs and site-packages
    if any(part in EXCLUDE_DIRS for part in p.parts):
        continue
    try:
        py_compile.compile(str(p), doraise=True)
    except py_compile.PyCompileError as e:
        errors.append((p, str(e)))

if not errors:
    print('No syntax errors detected in project files.')
else:
    print('Syntax errors found:')
    for fn, err in errors:
        print(f'- {fn}:')
        print(err)
    sys.exit(2)

"""
Developer-only debug script: debug_numpy_import.py
Purpose: Print Python/NumPy environment info; developer-only utility. Run with RUN_DEBUG_SCRIPTS=1.
"""

import os, sys, traceback

def main():
    print('EXE:', sys.executable)
    print('CWD:', os.getcwd())
    print('sys.path[0]:', sys.path[0])
    print('PYTHONPATH:', os.environ.get('PYTHONPATH'))
    try:
        import numpy as np
        print('NUMPY FILE:', np.__file__)
        print('NUMPY VERSION:', np.__version__)
    except Exception:
        traceback.print_exc()

if __name__ == '__main__':
    if os.environ.get('RUN_DEBUG_SCRIPTS') != '1':
        print("Developer-only script. Set RUN_DEBUG_SCRIPTS=1 to run this file.")
        sys.exit(0)
    main()
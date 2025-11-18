import os, sys, traceback

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
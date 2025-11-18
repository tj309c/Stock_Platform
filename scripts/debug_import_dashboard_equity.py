"""
Developer-only debug script: debug_import_dashboard_equity.py
Purpose: Quick import test for the Equity dashboard module. To run, set RUN_DEBUG_SCRIPTS=1.
"""

import os
import importlib
import sys
import traceback

if __name__ == '__main__':
    if os.environ.get('RUN_DEBUG_SCRIPTS') != '1':
        print("Developer-only script. Set RUN_DEBUG_SCRIPTS=1 to run this file.")
        sys.exit(0)
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

    try:
        importlib.invalidate_caches()
        from src.dashboards import dashboard_equity
        print('Imported OK')
    except Exception:
        traceback.print_exc()

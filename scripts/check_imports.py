import sys
import os

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

def main():
    try:
        import src.server.settings_server as ss
        import src.dashboards.dashboard_debug as db
        import src.server.llm_worker as lw
        print('OK: Imported settings_server, dashboard_debug, llm_worker')
    except Exception as e:
        print('Import failed:', e)
        raise

if __name__ == '__main__':
    main()

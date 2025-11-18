import os
import sys

# Ensure no plugin autoload
os.environ['PYTEST_DISABLE_PLUGIN_AUTOLOAD'] = '1'

def main():
    # Ensure project root is available for test imports
    ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    if ROOT not in sys.path:
        sys.path.insert(0, ROOT)
    import pytest
    sys.exit(pytest.main(['-q', 'tests/unit/test_llm_worker.py']))

if __name__ == '__main__':
    main()

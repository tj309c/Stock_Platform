Export Project State (Backups)
--------------------------------

This folder contains a small utility to create a ZIP backup of the project workspace.

Usage (Windows):
1. Activate the project's venv, or rely on system Python if venv isn't present.
2. Run the Python script:

```
%CD%\.venv\Scripts\python.exe scripts\export_project_state.py
```

Alternatively use the included batch wrapper:

```
scripts\export_project_state.bat
```

Output:
- The generated zip is written to `data/backups` with filename `analysis_master_backup_<timestamp>.zip`.
- The script excludes the following directories: `.venv`, `.git`, and `data/backups` itself to avoid recursion.

Notes:
- The script will skip files that cannot be written due to metadata issues and safely continue.
- You can edit the `EXCLUDE_DIRS` constant inside the script to add more folders to ignore.

Developer Utilities (Debugging)
--------------------------------
This folder also contains a set of developer-only debugging scripts that help with troubleshooting local
environment, imports, and quick functional checks. These scripts are not meant for production usage and may
depend on local system configuration or network access.

To prevent accidental execution in CI or production environments, run developer scripts with the
environment variable `RUN_DEBUG_SCRIPTS` set to `1`. For example (Windows CMD):

```
SET RUN_DEBUG_SCRIPTS=1
python scripts/debug_pe.py
```

The available developer debug scripts include:
- `debug_pe.py` - Inspect yfinance attributes related to EPS and financials.
- `debug_import_dashboard_equity.py` - Quick import test for the Equity dashboard module.
- `debug_sentiment.py` - Local debug harness for the SentimentScraper pipeline with synthetic headlines.
- `debug_run_worker_once.py` - Run the worker once locally with a fake job queue for testing LLM scoring.
- `debug_weight_test.py` - Test SentimentScraper weight setting and cache behavior with monkeypatched headlines.
- `debug_numpy_import.py` - Prints numpy environment details (path, version) for troubleshooting.

If you want to permanently enable any of these scripts, set `RUN_DEBUG_SCRIPTS=1` or edit the files locally.

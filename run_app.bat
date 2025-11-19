@echo off
REM Analysis Master - Startup Script
REM Usage: run_app.bat [dev] [migrate]
REM  - dev: Install dev requirements and download NLTK VADER lexicon
REM  - migrate: If a repo-root secrets.toml exists, copy to .streamlit/secrets.toml (uses scripts/migrate_repo_secrets_to_dotstreamlit.py)

cd /d "%~dp0"

echo.
echo =========================================  REM header
echo    🔥 Analysis Master - Starting App 🔥
echo =========================================  REM press Ctrl+C separator
echo.

REM Setup venv helper and set VENV_PY/VENV_ACTIVATION
call "scripts\venv_helpers.bat"
IF DEFINED VENV_ACTIVATION (
    echo [INFO] Activating virtual environment...
    call "%VENV_ACTIVATION%"
) ELSE (
    echo [WARNING] Virtual environment activation script not found; continuing with system Python.
)

REM Check for a --skip-install flag in args; if present, skip installing requirements
set SKIP_INSTALL=0
set ARGS=%*
if defined ARGS (
    for %%A in (%ARGS%) do (
        if /I "%%A"=="--skip-install" set SKIP_INSTALL=1
    )
)

if "%SKIP_INSTALL%"=="1" (
    echo [INFO] --skip-install detected; skipping install of requirements.
) else (
    REM Install base requirements
    echo [INFO] Installing base requirements (requirements.txt)...
    pip install -r requirements.txt
    echo.

    echo [INFO] Downloading NLTK VADER lexicon (used by sentiment analysis)...
    python -m nltk.downloader -q vader_lexicon || (
        echo [WARNING] NLTK downloader failed; sentiment analysis may be impacted.
    )
    echo.
)

REM Developer mode: install dev requirements and additional setup
call "scripts\venv_helpers.bat" activate
IF /I "%~1"=="dev" (
    echo [INFO] Dev mode detected. Installing dev requirements (requirements-dev.txt)...
    pip install -r requirements-dev.txt
    echo.
)

REM Optional migration: copy repo-root secrets to .streamlit
IF /I "%~2"=="migrate" (
    echo [INFO] Attempting to migrate repo-root secrets.toml to .streamlit/secrets.toml (dry-run suppressed)...
    python scripts\migrate_repo_secrets_to_dotstreamlit.py --force || (
        echo [WARNING] Migration script failed or not available; check scripts/migrate_repo_secrets_to_dotstreamlit.py
    )
    echo.
)

echo [INFO] Starting Streamlit from virtual environment...
echo [INFO] App will open at: http://localhost:8501
echo [INFO] Network URL will be displayed below
echo.
echo =========================================  REM Start/Stop separators
echo Press Ctrl+C to stop the server
echo =========================================  REM end of header
echo.

REM Check for .streamlit/secrets.toml and warn if missing (do not mutate)
IF NOT EXIST ".streamlit\secrets.toml" (
    echo [WARNING] .streamlit\secrets.toml was not found in the repo root.
    echo [WARNING] Public endpoints will still work; authenticated features may not.
    echo [WARNING] To add credentials, create .streamlit\secrets.toml or pass env vars.
    echo.
)
streamlit run main.py

echo.
echo [INFO] Server stopped.
pause

@echo off
REM Start the dev environment for the Stock Platform
REM This script will open three new command windows:
REM  - Streamlit UI (main app)
REM  - Settings Server (Flask)
REM  - LLM Worker (queue worker)

REM Optionally update the following environment variables before starting
SET "SETTINGS_SERVER_PORT=5001"
SET "STREAMLIT_PORT=8501"
REM Prefer venv python if available and set VENV_PY via helper
call "%~dp0\venv_helpers.bat"

echo Starting dev environment...

REM Start Streamlit in a new window
start "Streamlit" cmd /k "%VENV_PY% -m streamlit run main.py --server.port %STREAMLIT_PORT%"

REM Start Settings Server (Flask)
start "SettingsServer" cmd /k "%VENV_PY% -m src.server.settings_server"

REM Start LLM Worker
start "LLMWorker" cmd /k "%VENV_PY% scripts\run_llm_worker.py"

echo Dev environment started. Press any key to exit this launcher window.
pause >nul
REM Check secrets file and warn if missing to avoid silent auth failures (no migration)
IF NOT EXIST "%CD%\.streamlit\secrets.toml" (
	echo.
	echo [WARNING] .streamlit\secrets.toml not found. Authenticated features may not work.
	echo [TIP] Use scripts\run_app_with_venv.bat dev migrate to migrate repo-root secrets if you need a quick import.
)

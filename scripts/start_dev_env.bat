@echo off
REM Start the dev environment for the Stock Platform
REM This script will open three new command windows:
REM  - Streamlit UI (main app)
REM  - Settings Server (Flask)
REM  - LLM Worker (queue worker)

REM Optionally update the following environment variables before starting
SET "SETTINGS_SERVER_PORT=5001"
SET "STREAMLIT_PORT=8501"
REM Prefer venv python if available
SET "SCRIPT_DIR=%~dp0"
REM Check common virtual environment names
SET "VENV_PY=%SCRIPT_DIR%..\.venv\Scripts\python.exe"
IF NOT EXIST "%VENV_PY%" (
	SET "VENV_PY=%SCRIPT_DIR%..\venv\Scripts\python.exe"
)
IF NOT EXIST "%VENV_PY%" (
	SET "VENV_PY=python"
)

echo Starting dev environment...

REM Start Streamlit in a new window
start "Streamlit" cmd /k "%VENV_PY% -m streamlit run main.py --server.port %STREAMLIT_PORT%"

REM Start Settings Server (Flask)
start "SettingsServer" cmd /k "%VENV_PY% -m src.server.settings_server"

REM Start LLM Worker
start "LLMWorker" cmd /k "%VENV_PY% scripts\run_llm_worker.py"

echo Dev environment started. Press any key to exit this launcher window.
pause >nul

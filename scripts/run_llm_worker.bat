@echo off
REM Activate venv if present and run the LLM worker script
SET "SCRIPT_DIR=%~dp0"
call "%~dp0\venv_helpers.bat" activate

python scripts\run_llm_worker.py %*
exit /B %ERRORLEVEL%

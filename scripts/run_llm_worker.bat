@echo off
REM Activate venv if present and run the LLM worker script
SET "SCRIPT_DIR=%~dp0"
IF EXIST "%SCRIPT_DIR%..\.venv\Scripts\activate.bat" (
	call "%SCRIPT_DIR%..\.venv\Scripts\activate.bat"
) ELSE IF EXIST "%SCRIPT_DIR%..\venv\Scripts\activate.bat" (
	call "%SCRIPT_DIR%..\venv\Scripts\activate.bat"
) ELSE (
	echo No virtual environment activation script found; using system python
)

python scripts\run_llm_worker.py %*
exit /B %ERRORLEVEL%

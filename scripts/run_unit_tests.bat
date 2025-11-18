@echo off
REM Run unit tests using the project's venv (Windows CMD)
IF NOT EXIST "%CD%\.venv\Scripts\python.exe" (
  echo Virtual environment not found at %CD%\.venv. Please create or point to your venv.
  exit /b 1
)
REM Activate virtualenv for the session and run pytest command via python.exe to avoid shell nuance
%CD%\.venv\Scripts\python.exe -m pytest tests/unit -q
exit /b %ERRORLEVEL%

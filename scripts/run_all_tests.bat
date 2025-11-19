@echo off
REM Run all tests (unit + e2e) using the project's venv (Windows CMD)
call "%~dp0\venv_helpers.bat"
IF "%VENV_PY%"=="python" (
  echo Virtual environment not found; falling back to system python. Tests may behave differently.
)
REM Run unit tests first
REM Check for secrets and warn but continue
IF NOT EXIST "%CD%\.streamlit\secrets.toml" (
  echo [WARNING] .streamlit\secrets.toml not found. Some tests use authenticated endpoints.
)

REM Optionally install dev requirements and NLTK for tests
IF "%~1"=="dev" (
  "%VENV_PY%" -m pip install -r requirements-dev.txt
  "%VENV_PY%" -m nltk.downloader -q vader_lexicon
)

"%VENV_PY%" -m pytest tests/unit -q
IF %ERRORLEVEL% NEQ 0 (
  echo Unit tests failed; aborting.
  exit /b %ERRORLEVEL%
)
REM Run e2e tests (if playwright installed) - optionally install playwright browsers first.
"%VENV_PY%" -m pip install playwright pytest-playwright
"%VENV_PY%" -m playwright install
"%VENV_PY%" -m pytest tests/e2e -q
exit /b %ERRORLEVEL%

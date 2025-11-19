@echo off
REM Setup minimal test environment for unit tests (Windows CMD)
IF NOT EXIST "%CD%\.venv\Scripts\python.exe" (
  echo Virtual environment not found at %CD%\.venv. Please create or point to your venv.
  exit /b 1
)
%CD%\.venv\Scripts\python.exe -m pip install --upgrade pip
REM Install pytest and test-related packages (fast / minimal)
%CD%\.venv\Scripts\python.exe -m pip install pytest pytest-playwright flask requests beautifulsoup4 lxml pandas numpy vaderSentiment textblob nltk openai
echo Test environment setup complete.
exit /b 0

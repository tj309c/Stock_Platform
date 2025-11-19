@echo off
REM dev.bat - simplified, clean development helper
REM Usage: dev.bat <command> [args]

cd /d " %~dp0\
call \scripts\\venv_helpers.bat\

if \%~1\==\\ goto :_help
set \CMD=%~1\
shift

if /I \%CMD%\==\help\ goto :_help

if /I \%CMD%\==\start\ (
 call scripts\\run_app_with_venv.bat %*
 exit /B %ERRORLEVEL%
)

if /I \%CMD%\==\test\ (
 set \OPT=%~1\
 shift
 call scripts\\run_all_tests.bat %OPT% %*
 exit /B %ERRORLEVEL%
)

if /I \%CMD%\==\setup-venv\ (
 call scripts\\setup_venv.bat
 exit /B %ERRORLEVEL%
)

if /I \%CMD%\==\check-env\ (
 call scripts\\check_env.bat
 exit /B %ERRORLEVEL%
)

if /I \%CMD%\==\worker\ (
 call scripts\\run_llm_worker.bat %*
 exit /B %ERRORLEVEL%
)

echo Unknown command: %CMD%
echo Use: dev.bat help
exit /B 1

:_help
echo Usage: dev.bat <command> [args]
echo.
echo Commands:
echo start Run the Streamlit app (via scripts/run_app_with_venv.bat)
echo test [dev] Run all tests (use 'dev' optionally to install dev deps)
echo setup-venv Initialize virtual environment
echo check-env Run environment checks
echo worker Run the LLM worker
echo help Show this message
exit /B 0

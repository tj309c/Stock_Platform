@echo off
REM If you've accidentally committed .streamlit/secrets.toml to source control, run this script
REM to remove it from the git index while leaving it on disk locally (git rm --cached).
REM Note: This requires Git to be available on PATH.

echo Untracking .streamlit/secrets.toml from git (keeps local file)...
git rm --cached .streamlit/secrets.toml 2>nul
IF %ERRORLEVEL% EQU 0 (
    echo .streamlit/secrets.toml untracked from git.
    echo Please commit the change and add your local secrets back into .streamlit/secrets.toml.
) ELSE (
    echo Nothing to untrack or an error occurred. If the file is tracked, run the following command manually:
    echo     git rm --cached .streamlit/secrets.toml
)

pause >nul

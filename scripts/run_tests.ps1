# PowerShell helper to run tests using the project venv
$venvPath = Join-Path $PWD ".venv\Scripts\python.exe"
if (-Not (Test-Path $venvPath)) {
    Write-Error "Virtual environment not found at $PWD\.venv. Please create or point to your venv."
    exit 1
}
& $venvPath -m pytest tests/unit -q
exit $LASTEXITCODE

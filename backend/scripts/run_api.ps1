# Start FastAPI (run from repository root or backend/)
Set-Location $PSScriptRoot\..
$env:PYTHONPATH = (Get-Location).Path
python -m uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000

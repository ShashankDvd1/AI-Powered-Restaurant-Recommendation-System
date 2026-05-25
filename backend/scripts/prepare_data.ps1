# Download and preprocess Zomato dataset (requires network)
Set-Location $PSScriptRoot\..
$env:PYTHONPATH = (Get-Location).Path
python -m src.ingestion.prepare_data

# Start Backend Script
Write-Host "Starting Backend Server..." -ForegroundColor Green
Set-Location "$PSScriptRoot\..\backend"
.\venv\Scripts\python.exe -m src.main
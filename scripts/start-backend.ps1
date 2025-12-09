# Start backend server for Maxfrio Appointment Scheduling System

Write-Host "Starting backend server..." -ForegroundColor Green

# Check if virtual environment exists
if (-not (Test-Path "backend/venv")) {
    Write-Host "Virtual environment not found. Please run scripts/setup.ps1 first." -ForegroundColor Red
    exit 1
}

# Activate virtual environment and start server
Set-Location backend
.\venv\Scripts\Activate
Write-Host "Starting FastAPI server on http://localhost:8000" -ForegroundColor Cyan
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
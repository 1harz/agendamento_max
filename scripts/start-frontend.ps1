# Start frontend server for Maxfrio Appointment Scheduling System

Write-Host "Starting frontend server..." -ForegroundColor Green

# Check if node_modules exists
if (-not (Test-Path "frontend/node_modules")) {
    Write-Host "Node modules not found. Please run scripts/setup.ps1 first." -ForegroundColor Red
    exit 1
}

# Start frontend development server
Set-Location frontend
Write-Host "Starting Vite development server on http://localhost:3000" -ForegroundColor Cyan
npm run dev
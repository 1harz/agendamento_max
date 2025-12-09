# Setup script for Maxfrio Appointment Scheduling System

Write-Host "Setting up Maxfrio Appointment Scheduling System..." -ForegroundColor Cyan

# 1. Setup Backend
Write-Host "`n[1/3] Setting up Backend..." -ForegroundColor Yellow
Set-Location "$PSScriptRoot\..\backend"

# Create virtual environment if it doesn't exist
if (-not (Test-Path "venv")) {
    Write-Host "Creating Python virtual environment..."
    python -m venv venv
}

# Install dependencies
Write-Host "Installing Python dependencies..."
.\venv\Scripts\python.exe -m pip install -r requirements.txt

# Create .env if it doesn't exist
if (-not (Test-Path ".env")) {
    Write-Host "Creating .env file..."
    New-Item -ItemType File -Path ".env" -Value "GEMINI_API_KEY=your-api-key-here" -Force
}

# 2. Setup Frontend
Write-Host "`n[2/3] Setting up Frontend..." -ForegroundColor Yellow
Set-Location "$PSScriptRoot\..\frontend"

# Install Node.js dependencies
Write-Host "Installing Node.js dependencies..."
npm install

# 3. Setup Data
Write-Host "`n[3/3] Setting up Data..." -ForegroundColor Yellow
Set-Location "$PSScriptRoot\.."

# Create data directory if it doesn't exist
if (-not (Test-Path "backend\data")) {
    New-Item -ItemType Directory -Path "backend\data" -Force
}

# Create appointments.txt if it doesn't exist
if (-not (Test-Path "backend\data\appointments.txt")) {
    $initialData = '{"appointments": [], "metadata": {"last_updated": "", "version": "1.0", "total_appointments": 0}}'
    Set-Content -Path "backend\data\appointments.txt" -Value $initialData
}

Write-Host "`nSetup complete! You can now run the application using:" -ForegroundColor Green
Write-Host ".\scripts\start-backend.ps1" -ForegroundColor Cyan
Write-Host ".\scripts\start-frontend.ps1" -ForegroundColor Cyan
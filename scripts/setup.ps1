# Setup script for Maxfrio Appointment Scheduling System
# This script sets up the development environment

Write-Host "Setting up Maxfrio Appointment Scheduling System..." -ForegroundColor Green

# Check if Python is installed
try {
    $pythonVersion = python --version 2>&1
    Write-Host "Python found: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "Python is not installed. Please install Python 3.11+ first." -ForegroundColor Red
    exit 1
}

# Check if Node.js is installed
try {
    $nodeVersion = node --version
    Write-Host "Node.js found: $nodeVersion" -ForegroundColor Green
} catch {
    Write-Host "Node.js is not installed. Please install Node.js first." -ForegroundColor Red
    exit 1
}

# Check and install Rust toolchain (required for pydantic-core)
Write-Host "Checking for Rust toolchain..." -ForegroundColor Yellow
try {
    # Check if rustup is installed
    if (-not (Get-Command rustup -ErrorAction SilentlyContinue)) {
        Write-Host "rustup not found. Installing Rust toolchain..." -ForegroundColor Yellow
        # Download and run rustup-init
        Invoke-WebRequest -Uri "https://static.rust-lang.org/rustup/dist/x86_64-pc-windows-msvc/rustup-init.exe" -OutFile "rustup-init.exe"
        .\rustup-init.exe -y --profile minimal --default-toolchain stable-x86_64-pc-windows-msvc --target x86_64-pc-windows-msvc
        Remove-Item "rustup-init.exe"
        
        # Add cargo to PATH for current session
        $env:Path += ";$HOME\.cargo\bin"
    } else {
        Write-Host "Rust toolchain (rustup) found." -ForegroundColor Green
    }
    
    # Verify cargo is installed
    if (-not (Get-Command cargo -ErrorAction SilentlyContinue)) {
        Write-Host "Cargo not found after rustup install. Please ensure Rust is properly installed." -ForegroundColor Red
        exit 1
    } else {
        Write-Host "Cargo found." -ForegroundColor Green
    }
} catch {
    Write-Host "Error checking/installing Rust toolchain: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host "Please install Rust (https://rustup.rs/) manually and re-run the setup script." -ForegroundColor Red
    exit 1
}

# Setup Python backend
Write-Host "Setting up Python backend..." -ForegroundColor Yellow
Set-Location backend
python -m venv venv
.\venv\Scripts\Activate
pip install -r requirements.txt
Set-Location ..

# Setup Node.js frontend
Write-Host "Setting up Node.js frontend..." -ForegroundColor Yellow
Set-Location frontend
npm install
Set-Location ..

# Create .env file if it doesn't exist
if (-not (Test-Path ".env")) {
    Write-Host "Creating .env file..." -ForegroundColor Yellow
    New-Item -Path ".env" -ItemType File -Value "GOOGLE_API_KEY=your_api_key_here"
    Write-Host "Please update .env file with your Google API key" -ForegroundColor Cyan
}

Write-Host "Setup completed successfully!" -ForegroundColor Green
Write-Host "Run 'scripts/start-backend.ps1' to start the backend server"
Write-Host "Run 'scripts/start-frontend.ps1' to start the frontend server"
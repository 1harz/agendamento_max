# Quick Start Guide: Maxfrio Appointment Scheduling System

**Purpose**: Quick setup and deployment guide for the AI-powered appointment scheduling system  
**Target Audience**: Developers and system administrators  
**Date**: 2025-12-09

## Prerequisites

### System Requirements

- **Operating System**: Windows 10/11 (PowerShell 5.1+)
- **Python**: 3.11 or higher
- **Node.js**: 18.0 or higher
- **Memory**: Minimum 4GB RAM
- **Storage**: Minimum 1GB free space
- **Network**: Internet connection for AI API access

### Required Accounts

- **Google Gemini API**: Valid API key for Google Generative AI
  - Get yours at: https://ai.google.dev/
  - Select Gemini Pro model
  - Copy API key for configuration

## Installation Steps

### 1. Clone Repository

```powershell
# Clone the repository (replace with actual repository URL)
git clone <repository-url>
cd agendamento_max
```

### 2. Backend Setup

```powershell
# Navigate to backend directory
cd backend

# Create Python virtual environment
python -m venv venv

# Activate virtual environment
.\venv\Scripts\Activate.ps1

# Install Python dependencies
pip install -r requirements.txt

# Create data directory
New-Item -ItemType Directory -Path data -Force

# Create initial appointments file
New-Item -ItemType File -Path data\appointments.txt -Force
Set-Content data\appointments.txt '{"appointments": [], "metadata": {"last_updated": "", "version": "1.0", "total_appointments": 0}}'
```

### 3. Frontend Setup

```powershell
# Navigate to frontend directory (from repository root)
cd ..\frontend

# Install Node.js dependencies
npm install

# Build for development
npm run dev
```

### 4. Configuration

#### Backend Configuration

Create `backend\src\config.py`:

```python
import os
from datetime import timedelta

class Config:
    # API Configuration
    API_HOST = "0.0.0.0"
    API_PORT = 8000
    API_PREFIX = "/api/v1"
    
    # CORS Configuration
    CORS_ORIGINS = ["http://localhost:5173", "http://127.0.0.1:5173"]
    
    # File Storage Configuration
    DATA_DIR = "data"
    APPOINTMENTS_FILE = os.path.join(DATA_DIR, "appointments.txt")
    BACKUP_DIR = os.path.join(DATA_DIR, "backups")
    
    # AI Configuration
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "your-api-key-here")
    GEMINI_MODEL = "gemini-pro"
    AI_MAX_TOKENS = 1000
    AI_TEMPERATURE = 0.7
    
    # Business Logic Configuration
    MAX_APPOINTMENTS_PER_DAY = 50
    DEFAULT_RECOMMENDATION_COUNT = 3
    APPOINTMENT_PRIORITY_WEIGHTS = {
        "volatility": 0.6,
        "proximity": 0.4
    }
    
    # Performance Configuration
    CACHE_TTL = timedelta(minutes=5)
    MAX_FILE_SIZE_MB = 10
```

#### Environment Variables

Create `.env` file in backend directory:

```env
GEMINI_API_KEY=your-actual-gemini-api-key-here
```

#### Frontend Configuration

Update `frontend\src\services\api.js`:

```javascript
const API_BASE_URL = 'http://localhost:8000/api/v1';

// Export configuration
export const config = {
  apiBaseUrl: API_BASE_URL,
  timeout: 10000,
  retryAttempts: 3
};
```

## Running the Application

### Method 1: Using PowerShell Scripts (Recommended)

```powershell
# From repository root
# Start backend
.\scripts\start-backend.ps1

# In another terminal, start frontend
.\scripts\start-frontend.ps1
```

### Method 2: Manual Startup

#### Backend

```powershell
cd backend
.\venv\Scripts\Activate.ps1
python src\main.py
```

#### Frontend

```powershell
cd frontend
npm run dev
```

## Accessing the Application

- **Frontend**: http://localhost:5173
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs

## Initial Setup

### 1. Verify AI Integration

1. Open the application in your browser
2. Navigate to the AI Assistant section
3. Test with a simple message: "Olá, posso agendar um serviço?"
4. Verify you receive a response from the AI

### 2. Create First Appointment

1. Click "New Appointment" button
2. Fill in the required fields:
   - Customer Name: "Cliente Teste"
   - Service Date: Select a future date/time
   - Service Type: "Manutenção"
   - Volatility Level: "Medium"
3. Click "Save"
4. Verify the appointment appears in the list

### 3. Test AI Recommendations

1. Create a few more appointments with different dates
2. Use the AI Assistant: "Preciso cancelar o agendamento do Cliente Teste e encontrar uma alternativa"
3. Verify the AI suggests alternative appointments
4. Test accepting and rejecting recommendations

## Common Issues and Solutions

### Backend Issues

**Issue**: ModuleNotFoundError: No module named 'fastapi'
```powershell
# Solution: Install dependencies
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

**Issue**: Gemini API key not working
```powershell
# Solution: Verify API key in .env file
# Ensure key has proper permissions
# Check network connectivity to Google APIs
```

**Issue**: File access denied
```powershell
# Solution: Check file permissions
# Run PowerShell as Administrator
# Verify data directory exists and is writable
```

### Frontend Issues

**Issue**: Cannot connect to backend API
```powershell
# Solution: Check if backend is running
# Verify CORS configuration in backend
# Check API_BASE_URL in frontend config
```

**Issue**: Build fails with dependency errors
```powershell
# Solution: Clear node_modules and reinstall
Remove-Item -Recurse -Force node_modules
npm install
```

### General Issues

**Issue**: Application not responsive on mobile
```powershell
# Solution: Check browser developer tools
# Verify responsive CSS breakpoints
# Test with different screen sizes
```

## Development Workflow

### Making Changes

1. **Backend Changes**:
   - Modify Python files in `backend/src/`
   - Restart backend server
   - Test API changes with Swagger UI

2. **Frontend Changes**:
   - Modify React components in `frontend/src/`
   - Vite will automatically reload
   - Test changes in browser

3. **Configuration Changes**:
   - Update config files
   - Restart affected services
   - Verify changes take effect

### Debugging

#### Backend Debugging

```powershell
# Enable debug mode
$env:DEBUG = "true"
python src\main.py

# Check logs in terminal
# Use browser developer tools for API requests
```

#### Frontend Debugging

```powershell
# Open browser developer tools (F12)
# Check Console tab for errors
# Use Network tab to inspect API calls
```

## Production Deployment

### Security Considerations

1. **API Key Security**:
   - Never commit API keys to version control
   - Use environment variables in production
   - Regularly rotate API keys

2. **File Access**:
   - Restrict file permissions to application user only
   - Implement backup strategy
   - Monitor file access logs

3. **Network Security**:
   - Use HTTPS in production
   - Implement firewall rules
   - Consider VPN for internal access

### Performance Optimization

1. **Backend Optimization**:
   - Implement caching for frequent reads
   - Optimize file I/O operations
   - Monitor memory usage

2. **Frontend Optimization**:
   - Implement lazy loading for appointment lists
   - Optimize bundle size
   - Use browser caching effectively

### Backup Strategy

```powershell
# Automated backup script (run daily)
$backupPath = "backups\appointments_backup_$(Get-Date -Format 'yyyyMMdd_HHmmss').txt"
Copy-Item data\appointments.txt $backupPath

# Keep only last 30 days of backups
Get-ChildItem backups\*.txt | Where-Object CreationTime -lt (Get-Date).AddDays(-30) | Remove-Item
```

## Support and Maintenance

### Regular Maintenance Tasks

1. **Weekly**:
   - Check application logs for errors
   - Verify backup files are created
   - Monitor disk space usage

2. **Monthly**:
   - Update Python dependencies
   - Update Node.js dependencies
   - Review AI API usage and costs

3. **Quarterly**:
   - Review and rotate API keys
   - Performance optimization review
   - Security audit

### Getting Help

- **Documentation**: Check this guide and API documentation
- **Logs**: Review application logs for error details
- **Community**: Contact development team for support

### Troubleshooting Checklist

1. Verify all prerequisites are installed
2. Check configuration files for correct values
3. Review application logs for errors
4. Test individual components separately
5. Verify network connectivity
6. Check file permissions and disk space
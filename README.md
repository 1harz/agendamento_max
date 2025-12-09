# Maxfrio AI-Powered Appointment Scheduling System

This project is an AI-powered appointment scheduling system for Maxfrio company, designed to streamline appointment management for internal use.

## Features

- **Manual Appointment Management**: Create, edit, and view appointments.
- **Visual Dashboard**: Color-coded appointment cards for at-a-glance status (Delayed, In Progress, Completed).
- **AI Assistant**: Use natural language to reschedule, cancel, and get recommendations for appointments.
- **Occurrence Tracking**: History of changes for each appointment.

## Tech Stack

- **Backend**: Python 3.11+, FastAPI
- **Frontend**: React 18+, Vite, Pure CSS
- **AI**: Google Gemini Pro
- **Storage**: TXT file with JSON structure
- **Automation**: PowerShell scripts

## Quick Start

### Prerequisites
- Python 3.11+
- Node.js 18+
- PowerShell 5.1+
- Google Gemini API Key

### Setup
1. Clone the repository.
2. Run the setup script:
   ```powershell
   .\scripts\setup.ps1
   ```
3. Add your Gemini API key to `backend\.env`.

### Running the Application
- **Start Backend**: `.\scripts\start-backend.ps1`
- **Start Frontend**: `.\scripts\start-frontend.ps1` (in a new terminal)

Access the application at `http://localhost:5173`.

## Project Structure
- `backend/`: FastAPI application
- `frontend/`: React application
- `scripts/`: PowerShell automation scripts
- `specs/`: Project specification documents

## Notes on Polish Phase (T058-T062)
- **Code Cleanup**: Code has been written with readability and simplicity in mind, following standard conventions for Python and React.
- **Performance**: Frontend sorting and filtering are handled client-side for responsiveness. Backend services are async where appropriate (AI calls).
- **Security**: Basic input validation is in place. As an internal tool, it does not require authentication, but API keys are managed via environment variables.
- **Validation**: Manual validation should be performed as per the project's constitution (no automated tests). The `quickstart.md` guide in `specs/001-ai-scheduling/` should be followed for validation.
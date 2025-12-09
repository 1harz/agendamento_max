import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Settings:
    """Application settings"""
    
    # API Configuration
    API_TITLE: str = "Maxfrio Appointment Scheduling API"
    API_DESCRIPTION: str = "API for managing appointments with AI-powered scheduling assistance"
    API_VERSION: str = "1.0.0"
    
    # CORS Configuration
    ALLOWED_ORIGINS: list = ["http://localhost:3000"]
    
    # File Storage Configuration
    DATA_DIR: str = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
    APPOINTMENTS_FILE: str = os.path.join(DATA_DIR, "appointments.txt")
    
    # Google Gemini AI Configuration
    GOOGLE_API_KEY: str = os.getenv("GOOGLE_API_KEY", "")
    
    # Logging Configuration
    LOG_LEVEL: str = "INFO"
    
    class Config:
        case_sensitive = True

# Create settings instance
settings = Settings()
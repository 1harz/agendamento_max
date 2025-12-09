import os
from datetime import timedelta
from dotenv import load_dotenv

load_dotenv()

class Config:
    # API Configuration
    API_HOST = "0.0.0.0"
    API_PORT = 8000
    API_PREFIX = "/api/v1"
    
    # CORS Configuration
    CORS_ORIGINS = ["http://localhost:5173", "http://127.0.0.1:5173"]
    
    # File Storage Configuration
    DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")
    APPOINTMENTS_FILE = os.path.join(DATA_DIR, "appointments.txt")
    BACKUP_DIR = os.path.join(DATA_DIR, "backups")
    
    # AI Configuration
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
    GEMINI_MODEL = "gemini-2.5-flash"
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

    @classmethod
    def ensure_directories(cls):
        os.makedirs(cls.DATA_DIR, exist_ok=True)
        os.makedirs(cls.BACKUP_DIR, exist_ok=True)
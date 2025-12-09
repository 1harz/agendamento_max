from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Import middleware
from .api.middleware import (
    LoggingMiddleware,
    ErrorHandlingMiddleware,
    RequestValidationMiddleware,
    setup_logging
)

# Initialize logging
setup_logging()

# Create FastAPI application
app = FastAPI(
    title="Maxfrio Appointment Scheduling API",
    description="API for managing appointments with AI-powered scheduling assistance",
    version="1.0.0"
)

# Add custom middleware
app.add_middleware(RequestValidationMiddleware)
app.add_middleware(ErrorHandlingMiddleware)
app.add_middleware(LoggingMiddleware)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Import and include API routes
from .api.routes import router as api_router
app.include_router(api_router, prefix="/api")

@app.get("/")
async def root():
    """Root endpoint to verify API is running"""
    return {"message": "Maxfrio Appointment Scheduling API is running"}

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
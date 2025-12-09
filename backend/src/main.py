from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .config import Config
from .api.routes import router as api_router
from .api.middleware import error_handling_middleware

# Initialize configuration
Config.ensure_directories()

app = FastAPI(
    title="Maxfrio Appointment Scheduling API",
    description="API for managing appointments with AI-powered scheduling assistance",
    version="1.0.0"
)

# Register Middleware
app.middleware("http")(error_handling_middleware)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=Config.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {
        "message": "Maxfrio Appointment Scheduling API",
        "status": "online",
        "version": "1.0.0"
    }

app.include_router(api_router, prefix=Config.API_PREFIX)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("src.main:app", host=Config.API_HOST, port=Config.API_PORT, reload=True)
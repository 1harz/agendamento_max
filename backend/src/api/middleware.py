import logging
import time
from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from typing import Dict, Any

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("logs/api.log"),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)


class LoggingMiddleware(BaseHTTPMiddleware):
    """Middleware to log all requests and responses"""
    
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        
        # Log request
        logger.info(f"Request: {request.method} {request.url}")
        
        # Process request
        response = await call_next(request)
        
        # Calculate processing time
        process_time = time.time() - start_time
        
        # Log response
        logger.info(
            f"Response: {response.status_code} - "
            f"Process time: {process_time:.4f}s"
        )
        
        # Add processing time to response headers
        response.headers["X-Process-Time"] = str(process_time)
        
        return response


class ErrorHandlingMiddleware(BaseHTTPMiddleware):
    """Middleware to handle exceptions and format error responses"""
    
    async def dispatch(self, request: Request, call_next):
        try:
            response = await call_next(request)
            return response
        except HTTPException as e:
            # Handle HTTP exceptions
            logger.warning(f"HTTP Exception: {e.status_code} - {e.detail}")
            return JSONResponse(
                status_code=e.status_code,
                content={
                    "success": False,
                    "error": {
                        "code": self._get_error_code(e.status_code),
                        "message": e.detail,
                        "details": self._get_error_details(e)
                    }
                }
            )
        except Exception as e:
            # Handle unexpected exceptions
            logger.error(f"Unexpected error: {str(e)}", exc_info=True)
            return JSONResponse(
                status_code=500,
                content={
                    "success": False,
                    "error": {
                        "code": "INTERNAL_SERVER_ERROR",
                        "message": "An unexpected error occurred",
                        "details": []
                    }
                }
            )
    
    def _get_error_code(self, status_code: int) -> str:
        """Convert HTTP status code to error code string"""
        error_codes = {
            400: "BAD_REQUEST",
            401: "UNAUTHORIZED",
            403: "FORBIDDEN",
            404: "NOT_FOUND",
            405: "METHOD_NOT_ALLOWED",
            422: "VALIDATION_ERROR",
            429: "RATE_LIMIT_EXCEEDED",
            500: "INTERNAL_SERVER_ERROR",
            502: "BAD_GATEWAY",
            503: "SERVICE_UNAVAILABLE",
            504: "GATEWAY_TIMEOUT"
        }
        return error_codes.get(status_code, "UNKNOWN_ERROR")
    
    def _get_error_details(self, exception: HTTPException) -> list:
        """Extract error details from exception"""
        # FastAPI validation errors provide details in a specific format
        if hasattr(exception, 'errors') and exception.errors:
            return [error.get('msg', 'Validation error') for error in exception.errors()]
        
        # For simple string messages, return as single item list
        if isinstance(exception.detail, str):
            return [exception.detail]
        
        # For complex error messages, try to extract details
        if isinstance(exception.detail, dict):
            details = []
            for key, value in exception.detail.items():
                if isinstance(value, list):
                    details.extend([f"{key}: {item}" for item in value])
                else:
                    details.append(f"{key}: {value}")
            return details
        
        return []


class RequestValidationMiddleware(BaseHTTPMiddleware):
    """Middleware to validate and sanitize incoming requests"""
    
    async def dispatch(self, request: Request, call_next):
        # Log request details for debugging
        logger.info(f"Request headers: {dict(request.headers)}")
        
        # For POST/PUT requests, log request body size (not content for security)
        if request.method in ["POST", "PUT", "PATCH"]:
            content_length = request.headers.get("content-length", "0")
            logger.info(f"Request body size: {content_length} bytes")
        
        # Continue processing
        response = await call_next(request)
        
        return response


def setup_logging():
    """Setup logging configuration"""
    # Create logs directory if it doesn't exist
    import os
    os.makedirs("backend/logs", exist_ok=True)
    
    # Configure root logger
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.FileHandler("logs/api.log"),
            logging.StreamHandler()
        ]
    )
    
    # Set specific logger levels
    logging.getLogger("uvicorn").setLevel(logging.INFO)
    logging.getLogger("fastapi").setLevel(logging.INFO)
    
    logger.info("Logging system initialized")


def log_api_operation(operation: str, details: Dict[str, Any] = None):
    """Log API operations with details"""
    log_message = f"API Operation: {operation}"
    if details:
        log_message += f" - Details: {details}"
    logger.info(log_message)


def log_error(operation: str, error: Exception, details: Dict[str, Any] = None):
    """Log errors with operation context"""
    error_message = f"Error in {operation}: {str(error)}"
    if details:
        error_message += f" - Details: {details}"
    logger.error(error_message, exc_info=True)


def log_warning(operation: str, message: str, details: Dict[str, Any] = None):
    """Log warnings with operation context"""
    warning_message = f"Warning in {operation}: {message}"
    if details:
        warning_message += f" - Details: {details}"
    logger.warning(warning_message)
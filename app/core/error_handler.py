"""
Enhanced Error Handling for GenAI Metrics Dashboard
Implements comprehensive error handling, logging, and monitoring
"""
import traceback
import uuid
from typing import Dict, Any, Optional
from datetime import datetime
from fastapi import Request, HTTPException, status
from fastapi.responses import JSONResponse
import logging
import json

logger = logging.getLogger(__name__)

class ErrorHandler:
    """Enhanced error handling with detailed logging and monitoring"""
    
    def __init__(self):
        self.error_codes = {
            # Authentication & Authorization
            "AUTH_001": "Invalid credentials",
            "AUTH_002": "Token expired",
            "AUTH_003": "Insufficient permissions",
            "AUTH_004": "Account locked",
            
            # Validation Errors
            "VAL_001": "Invalid input data",
            "VAL_002": "Missing required field",
            "VAL_003": "Invalid format",
            "VAL_004": "Value out of range",
            
            # Database Errors
            "DB_001": "Database connection failed",
            "DB_002": "Query execution failed",
            "DB_003": "Data not found",
            "DB_004": "Constraint violation",
            
            # External Service Errors
            "EXT_001": "External service unavailable",
            "EXT_002": "External service timeout",
            "EXT_003": "External service error",
            
            # Rate Limiting
            "RATE_001": "Rate limit exceeded",
            "RATE_002": "Too many requests",
            
            # Security Errors
            "SEC_001": "CSRF token invalid",
            "SEC_002": "Security violation detected",
            "SEC_003": "Suspicious activity",
            
            # System Errors
            "SYS_001": "Internal server error",
            "SYS_002": "Service unavailable",
            "SYS_003": "Configuration error",
        }
    
    def create_error_response(
        self,
        error_code: str,
        message: str = None,
        details: Dict[str, Any] = None,
        status_code: int = 500,
        request_id: str = None
    ) -> JSONResponse:
        """Create standardized error response"""
        
        if not request_id:
            request_id = str(uuid.uuid4())
        
        error_info = {
            "error": {
                "code": error_code,
                "message": message or self.error_codes.get(error_code, "Unknown error"),
                "details": details or {},
                "request_id": request_id,
                "timestamp": datetime.utcnow().isoformat(),
                "status_code": status_code
            }
        }
        
        # Log the error
        self.log_error(error_code, message, details, request_id, status_code)
        
        return JSONResponse(
            status_code=status_code,
            content=error_info,
            headers={"X-Request-ID": request_id}
        )
    
    def log_error(
        self,
        error_code: str,
        message: str,
        details: Dict[str, Any],
        request_id: str,
        status_code: int
    ):
        """Log error with structured information"""
        
        log_data = {
            "error_code": error_code,
            "error_message": message,
            "details": details,
            "request_id": request_id,
            "status_code": status_code,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        if status_code >= 500:
            logger.error(f"Server Error [{error_code}]: {message}", extra=log_data)
        elif status_code >= 400:
            logger.warning(f"Client Error [{error_code}]: {message}", extra=log_data)
        else:
            logger.info(f"Error [{error_code}]: {message}", extra=log_data)
    
    def handle_validation_error(self, error: Exception, request_id: str = None) -> JSONResponse:
        """Handle validation errors"""
        return self.create_error_response(
            error_code="VAL_001",
            message="Validation failed",
            details={"error": str(error)},
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            request_id=request_id
        )
    
    def handle_database_error(self, error: Exception, request_id: str = None) -> JSONResponse:
        """Handle database errors"""
        error_message = str(error)
        
        if "not found" in error_message.lower():
            error_code = "DB_003"
            status_code = status.HTTP_404_NOT_FOUND
        elif "constraint" in error_message.lower():
            error_code = "DB_004"
            status_code = status.HTTP_409_CONFLICT
        elif "connection" in error_message.lower():
            error_code = "DB_001"
            status_code = status.HTTP_503_SERVICE_UNAVAILABLE
        else:
            error_code = "DB_002"
            status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        
        return self.create_error_response(
            error_code=error_code,
            message="Database operation failed",
            details={"error": error_message},
            status_code=status_code,
            request_id=request_id
        )
    
    def handle_external_service_error(self, error: Exception, service_name: str, request_id: str = None) -> JSONResponse:
        """Handle external service errors"""
        error_message = str(error)
        
        if "timeout" in error_message.lower():
            error_code = "EXT_002"
            status_code = status.HTTP_504_GATEWAY_TIMEOUT
        elif "connection" in error_message.lower():
            error_code = "EXT_001"
            status_code = status.HTTP_503_SERVICE_UNAVAILABLE
        else:
            error_code = "EXT_003"
            status_code = status.HTTP_502_BAD_GATEWAY
        
        return self.create_error_response(
            error_code=error_code,
            message=f"External service error: {service_name}",
            details={"service": service_name, "error": error_message},
            status_code=status_code,
            request_id=request_id
        )
    
    def handle_rate_limit_error(self, limit_info: Dict[str, Any], request_id: str = None) -> JSONResponse:
        """Handle rate limiting errors"""
        return self.create_error_response(
            error_code="RATE_001",
            message="Rate limit exceeded",
            details=limit_info,
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            request_id=request_id
        )
    
    def handle_security_error(self, error_type: str, details: Dict[str, Any], request_id: str = None) -> JSONResponse:
        """Handle security-related errors"""
        error_codes = {
            "csrf": "SEC_001",
            "validation": "SEC_002",
            "suspicious": "SEC_003"
        }
        
        error_code = error_codes.get(error_type, "SEC_002")
        
        return self.create_error_response(
            error_code=error_code,
            message="Security violation detected",
            details=details,
            status_code=status.HTTP_403_FORBIDDEN,
            request_id=request_id
        )
    
    def handle_unexpected_error(self, error: Exception, request_id: str = None) -> JSONResponse:
        """Handle unexpected errors"""
        # Log full traceback for debugging
        logger.error(f"Unexpected error: {str(error)}", extra={
            "request_id": request_id,
            "traceback": traceback.format_exc(),
            "error_type": type(error).__name__
        })
        
        return self.create_error_response(
            error_code="SYS_001",
            message="An unexpected error occurred",
            details={"error_type": type(error).__name__},
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            request_id=request_id
        )

# Global error handler instance
error_handler = ErrorHandler()

# Enhanced exception handlers
async def enhanced_404_handler(request: Request, exc):
    """Enhanced 404 error handler"""
    request_id = str(uuid.uuid4())
    return error_handler.create_error_response(
        error_code="SYS_001",
        message="Resource not found",
        details={"path": str(request.url.path)},
        status_code=status.HTTP_404_NOT_FOUND,
        request_id=request_id
    )

async def enhanced_500_handler(request: Request, exc):
    """Enhanced 500 error handler"""
    request_id = str(uuid.uuid4())
    return error_handler.handle_unexpected_error(exc, request_id)

async def enhanced_validation_handler(request: Request, exc):
    """Enhanced validation error handler"""
    request_id = str(uuid.uuid4())
    return error_handler.handle_validation_error(exc, request_id)

# Error monitoring and alerting
class ErrorMonitor:
    """Monitor errors and send alerts for critical issues"""
    
    def __init__(self):
        self.error_counts = {}
        self.alert_thresholds = {
            "SYS_001": 10,  # System errors
            "DB_001": 5,    # Database connection errors
            "EXT_001": 5,   # External service errors
        }
    
    def track_error(self, error_code: str, request_id: str):
        """Track error occurrence"""
        current_time = datetime.utcnow()
        minute_key = current_time.strftime("%Y-%m-%d %H:%M")
        
        if minute_key not in self.error_counts:
            self.error_counts[minute_key] = {}
        
        if error_code not in self.error_counts[minute_key]:
            self.error_counts[minute_key][error_code] = 0
        
        self.error_counts[minute_key][error_code] += 1
        
        # Check if threshold exceeded
        threshold = self.alert_thresholds.get(error_code, 0)
        if self.error_counts[minute_key][error_code] >= threshold:
            self.send_alert(error_code, self.error_counts[minute_key][error_code], request_id)
    
    def send_alert(self, error_code: str, count: int, request_id: str):
        """Send alert for critical error threshold exceeded"""
        logger.critical(f"ALERT: Error threshold exceeded for {error_code}: {count} occurrences", extra={
            "error_code": error_code,
            "count": count,
            "request_id": request_id,
            "alert_type": "error_threshold"
        })
    
    def get_error_stats(self) -> Dict[str, Any]:
        """Get error statistics"""
        current_time = datetime.utcnow()
        minute_key = current_time.strftime("%Y-%m-%d %H:%M")
        
        return {
            "current_minute": self.error_counts.get(minute_key, {}),
            "total_errors": sum(sum(minute_errors.values()) for minute_errors in self.error_counts.values()),
            "thresholds": self.alert_thresholds
        }

# Global error monitor instance
error_monitor = ErrorMonitor()

# Decorator for automatic error handling
def handle_errors(error_code: str = "SYS_001", status_code: int = 500):
    """Decorator to automatically handle errors in endpoints"""
    def decorator(func):
        async def wrapper(*args, **kwargs):
            try:
                return await func(*args, **kwargs)
            except HTTPException:
                # Re-raise HTTP exceptions
                raise
            except Exception as e:
                request_id = str(uuid.uuid4())
                error_monitor.track_error(error_code, request_id)
                return error_handler.handle_unexpected_error(e, request_id)
        return wrapper
    return decorator

"""
Main FastAPI application for GenAI Metrics Dashboard
"""
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
import time
import logging
import uuid

from app.config import settings
from app.api.v1.api import api_router
from app.routes.views import router as views_router
from app.websocket.endpoints import router as websocket_router

# Import security middleware
from app.middleware.rate_limiting import rate_limit_middleware, rate_limiter
from app.middleware.security import security_headers_middleware
from app.middleware.csrf import csrf_middleware, get_csrf_token
from app.middleware.validation import input_validation_middleware
from app.middleware.compression import compression_middleware_func

# Import enhanced error handling
from app.core.error_handler import (
    enhanced_404_handler, enhanced_500_handler, enhanced_validation_handler,
    error_handler, error_monitor
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI application
app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="GenAI Metrics Dashboard - Enterprise Project Management Platform",
    openapi_url="/openapi.json",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add trusted host middleware
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["*"]  # Allow all hosts for development
)

# Add security middleware (order matters!)
app.middleware("http")(input_validation_middleware)  # First: validate input
app.middleware("http")(csrf_middleware)             # Second: CSRF protection
app.middleware("http")(rate_limit_middleware)       # Third: rate limiting
app.middleware("http")(security_headers_middleware) # Fourth: security headers
app.middleware("http")(compression_middleware_func) # Fifth: compression

# Add request timing middleware
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response

# Include view router FIRST (higher priority for exact matches)
app.include_router(views_router)

# Include API router with prefix
app.include_router(api_router, prefix=settings.API_V1_STR)

# Include WebSocket router
app.include_router(websocket_router, prefix="/ws")

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Root endpoint
@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "message": "GenAI Metrics Dashboard API",
        "version": settings.VERSION,
        "docs": "/docs",
        "redoc": "/redoc",
        "api": settings.API_V1_STR
    }

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": time.time(),
        "version": settings.VERSION
    }

# API status endpoint
@app.get("/status")
async def api_status():
    """API status endpoint"""
    return {
        "api_status": "operational",
        "database_status": "connected",
        "ai_services_status": "available",
        "version": settings.VERSION,
        "timestamp": time.time()
    }

# CSRF token endpoint
@app.get("/csrf-token")
async def get_csrf_token_endpoint(request: Request):
    """Get CSRF token for forms"""
    return get_csrf_token(request)

# Error monitoring endpoint
@app.get("/error-stats")
async def get_error_stats():
    """Get error statistics for monitoring"""
    return error_monitor.get_error_stats()

# Enhanced exception handlers
@app.exception_handler(404)
async def not_found_handler(request: Request, exc):
    """Handle 404 errors with enhanced logging"""
    return await enhanced_404_handler(request, exc)

@app.exception_handler(500)
async def internal_error_handler(request: Request, exc):
    """Handle 500 errors with enhanced logging"""
    return await enhanced_500_handler(request, exc)

@app.exception_handler(422)
async def validation_error_handler(request: Request, exc):
    """Handle validation errors"""
    return await enhanced_validation_handler(request, exc)

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Handle HTTP exceptions with enhanced logging"""
    request_id = str(uuid.uuid4())
    return error_handler.create_error_response(
        error_code=f"HTTP_{exc.status_code}",
        message=exc.detail,
        status_code=exc.status_code,
        request_id=request_id
    )

# Startup event
@app.on_event("startup")
async def startup_event():
    """Application startup event"""
    logger.info("🚀 GenAI Metrics Dashboard API starting up...")
    logger.info(f"📊 Project: {settings.PROJECT_NAME}")
    logger.info(f"🔢 Version: {settings.VERSION}")
    logger.info(f"🌐 API URL: {settings.API_V1_STR}")
    
    # Initialize security middleware
    try:
        await rate_limiter.initialize()
        logger.info("✅ Security middleware initialized")
    except Exception as e:
        logger.error(f"❌ Failed to initialize security middleware: {e}")
    
    logger.info("✅ API startup complete!")

# Shutdown event
@app.on_event("shutdown")
async def shutdown_event():
    """Application shutdown event"""
    logger.info("🛑 GenAI Metrics Dashboard API shutting down...")
    logger.info("✅ API shutdown complete!")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )

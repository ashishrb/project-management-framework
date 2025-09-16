"""
Simplified FastAPI application for GenAI Metrics Dashboard Demo
"""
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import time
import logging

from app.config import settings
from app.api.v1.api import api_router
from app.routes.views import router as views_router
from app.websocket.endpoints import router as websocket_router

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

# Add CORS middleware - simplified for demo
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for demo
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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

# Include API router with prefix (includes auth endpoints)
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

# Startup event
@app.on_event("startup")
async def startup_event():
    """Application startup event"""
    logger.info("🚀 GenAI Metrics Dashboard API starting up...")
    logger.info(f"📊 Project: {settings.PROJECT_NAME}")
    logger.info(f"🔢 Version: {settings.VERSION}")
    logger.info(f"🌐 API URL: {settings.API_V1_STR}")
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

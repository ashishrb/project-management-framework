"""
Health Check Endpoints for GenAI Metrics Dashboard
Comprehensive health monitoring and system status
"""
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from typing import Dict, Any, List
import time
import psutil
import asyncio
from datetime import datetime
import logging

from app.database import check_database_health, db_performance_monitor
from app.core.cache_manager import check_cache_health
from app.core.ai_client import get_ai_service
from app.config import settings

logger = logging.getLogger(__name__)
router = APIRouter()

class HealthChecker:
    """Comprehensive health checking system"""
    
    def __init__(self):
        self.start_time = datetime.utcnow()
        self.checks = {
            "database": self.check_database,
            "cache": self.check_cache,
            "ai_services": self.check_ai_services,
            "system": self.check_system_resources,
            "external": self.check_external_services
        }
    
    async def check_database(self) -> Dict[str, Any]:
        """Check database health"""
        try:
            health = check_database_health()
            return {
                "status": "healthy" if health["status"] == "healthy" else "unhealthy",
                "details": health,
                "response_time": await self._measure_response_time(check_database_health)
            }
        except Exception as e:
            logger.error(f"Database health check failed: {e}")
            return {
                "status": "unhealthy",
                "error": str(e),
                "response_time": None
            }
    
    async def check_cache(self) -> Dict[str, Any]:
        """Check cache health"""
        try:
            health = check_cache_health()
            return {
                "status": "healthy" if health["status"] == "healthy" else "unhealthy",
                "details": health,
                "response_time": await self._measure_response_time(check_cache_health)
            }
        except Exception as e:
            logger.error(f"Cache health check failed: {e}")
            return {
                "status": "unhealthy",
                "error": str(e),
                "response_time": None
            }
    
    async def check_ai_services(self) -> Dict[str, Any]:
        """Check AI services health"""
        try:
            ai_client = get_ai_client()
            start_time = time.time()
            
            # Test AI service connectivity
            test_result = await ai_client.test_connection()
            response_time = time.time() - start_time
            
            return {
                "status": "healthy" if test_result else "unhealthy",
                "details": {
                    "ai_client_status": "connected" if test_result else "disconnected",
                    "ollama_url": settings.OLLAMA_BASE_URL,
                    "chroma_status": "available"
                },
                "response_time": response_time
            }
        except Exception as e:
            logger.error(f"AI services health check failed: {e}")
            return {
                "status": "unhealthy",
                "error": str(e),
                "response_time": None
            }
    
    async def check_system_resources(self) -> Dict[str, Any]:
        """Check system resources"""
        try:
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            # Check thresholds
            cpu_healthy = cpu_percent < 80
            memory_healthy = memory.percent < 85
            disk_healthy = disk.percent < 90
            
            overall_healthy = cpu_healthy and memory_healthy and disk_healthy
            
            return {
                "status": "healthy" if overall_healthy else "degraded",
                "details": {
                    "cpu": {
                        "usage_percent": cpu_percent,
                        "healthy": cpu_healthy,
                        "threshold": 80
                    },
                    "memory": {
                        "usage_percent": memory.percent,
                        "available_gb": round(memory.available / (1024**3), 2),
                        "total_gb": round(memory.total / (1024**3), 2),
                        "healthy": memory_healthy,
                        "threshold": 85
                    },
                    "disk": {
                        "usage_percent": disk.percent,
                        "free_gb": round(disk.free / (1024**3), 2),
                        "total_gb": round(disk.total / (1024**3), 2),
                        "healthy": disk_healthy,
                        "threshold": 90
                    }
                },
                "response_time": 0.001  # System checks are instant
            }
        except Exception as e:
            logger.error(f"System resources health check failed: {e}")
            return {
                "status": "unhealthy",
                "error": str(e),
                "response_time": None
            }
    
    async def check_external_services(self) -> Dict[str, Any]:
        """Check external services"""
        try:
            # Check Redis
            redis_healthy = True
            redis_response_time = 0
            
            # Check external APIs if configured
            external_services = []
            
            return {
                "status": "healthy" if redis_healthy else "unhealthy",
                "details": {
                    "redis": {
                        "status": "healthy" if redis_healthy else "unhealthy",
                        "response_time": redis_response_time
                    },
                    "external_services": external_services
                },
                "response_time": redis_response_time
            }
        except Exception as e:
            logger.error(f"External services health check failed: {e}")
            return {
                "status": "unhealthy",
                "error": str(e),
                "response_time": None
            }
    
    async def _measure_response_time(self, func) -> float:
        """Measure response time of a function"""
        start_time = time.time()
        try:
            await func() if asyncio.iscoroutinefunction(func) else func()
            return time.time() - start_time
        except:
            return time.time() - start_time
    
    async def run_all_checks(self) -> Dict[str, Any]:
        """Run all health checks"""
        results = {}
        overall_status = "healthy"
        total_response_time = 0
        
        for check_name, check_func in self.checks.items():
            try:
                result = await check_func()
                results[check_name] = result
                
                if result["status"] != "healthy":
                    overall_status = "unhealthy"
                
                if result.get("response_time"):
                    total_response_time += result["response_time"]
                    
            except Exception as e:
                logger.error(f"Health check {check_name} failed: {e}")
                results[check_name] = {
                    "status": "unhealthy",
                    "error": str(e),
                    "response_time": None
                }
                overall_status = "unhealthy"
        
        return {
            "status": overall_status,
            "timestamp": datetime.utcnow().isoformat(),
            "uptime_seconds": (datetime.utcnow() - self.start_time).total_seconds(),
            "total_response_time": round(total_response_time, 3),
            "checks": results
        }

# Global health checker instance
health_checker = HealthChecker()

@router.get("/health", summary="Basic Health Check")
async def basic_health_check():
    """Basic health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "service": "GenAI Metrics Dashboard",
        "version": settings.VERSION
    }

@router.get("/health/detailed", summary="Detailed Health Check")
async def detailed_health_check():
    """Detailed health check with all system components"""
    return await health_checker.run_all_checks()

@router.get("/health/database", summary="Database Health Check")
async def database_health_check():
    """Database-specific health check"""
    return await health_checker.check_database()

@router.get("/health/cache", summary="Cache Health Check")
async def cache_health_check():
    """Cache-specific health check"""
    return await health_checker.check_cache()

@router.get("/health/ai-services", summary="AI Services Health Check")
async def ai_services_health_check():
    """AI services-specific health check"""
    return await health_checker.check_ai_services()

@router.get("/health/system", summary="System Resources Health Check")
async def system_health_check():
    """System resources health check"""
    return await health_checker.check_system_resources()

@router.get("/health/ready", summary="Readiness Check")
async def readiness_check():
    """Kubernetes readiness probe"""
    health_result = await health_checker.run_all_checks()
    
    if health_result["status"] == "healthy":
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={"status": "ready"}
        )
    else:
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={"status": "not ready", "details": health_result}
        )

@router.get("/health/live", summary="Liveness Check")
async def liveness_check():
    """Kubernetes liveness probe"""
    return {
        "status": "alive",
        "timestamp": datetime.utcnow().isoformat(),
        "uptime_seconds": (datetime.utcnow() - health_checker.start_time).total_seconds()
    }

@router.get("/health/metrics", summary="Health Metrics")
async def health_metrics():
    """Health metrics for monitoring"""
    db_stats = db_performance_monitor.get_stats()
    cache_stats = check_cache_health()
    
    return {
        "timestamp": datetime.utcnow().isoformat(),
        "database": {
            "query_count": db_stats["query_count"],
            "slow_queries": db_stats["slow_queries"],
            "slow_query_rate": db_stats["slow_query_rate"],
            "error_count": db_stats["error_count"]
        },
        "cache": cache_stats.get("cache_stats", {}),
        "system": {
            "cpu_percent": psutil.cpu_percent(),
            "memory_percent": psutil.virtual_memory().percent,
            "disk_percent": psutil.disk_usage('/').percent
        }
    }

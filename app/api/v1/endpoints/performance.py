"""
Performance Monitoring API Endpoints
Provides real-time performance metrics and monitoring
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Dict, Any, List
import asyncio
import time
from datetime import datetime, timedelta

from app.database import get_db, db_performance_monitor, check_database_health
from app.core.cache import cache_manager
from app.core.memory_manager import memory_monitor, websocket_manager, resource_manager, optimization_service
from app.core.logging import get_logger, log_api_endpoint

logger = get_logger("api.performance")

router = APIRouter()


@router.get("/health", response_model=Dict[str, Any])
def get_system_health():
    """Get overall system health status"""
    try:
        # Database health
        db_health = check_database_health()
        
        # Memory health
        memory_stats = memory_monitor.get_memory_usage()
        memory_healthy = memory_stats["rss"] < 500 * 1024 * 1024  # 500MB threshold
        
        # WebSocket health
        ws_stats = websocket_manager.get_connection_stats()
        ws_healthy = ws_stats["stats"]["active_connections"] < 800  # 80% of limit
        
        # Cache health
        try:
            cache_stats = cache_manager.cache.get_stats()
            cache_healthy = cache_stats.get("hit_rate", 0) > 50  # 50% hit rate threshold
        except:
            cache_stats = {"hit_rate": 0}
            cache_healthy = False
        
        # Overall health
        overall_healthy = all([
            db_health["status"] == "healthy",
            memory_healthy,
            ws_healthy,
            cache_healthy
        ])
        
        return {
            "status": "healthy" if overall_healthy else "degraded",
            "timestamp": datetime.now().isoformat(),
            "components": {
                "database": {
                    "status": db_health["status"],
                    "pool_status": db_health.get("pool_status", {}),
                    "healthy": db_health["status"] == "healthy"
                },
                "memory": {
                    "status": "healthy" if memory_healthy else "high_usage",
                    "usage_mb": memory_stats["rss"] / 1024 / 1024,
                    "percent": memory_stats["percent"],
                    "healthy": memory_healthy
                },
                "websockets": {
                    "status": "healthy" if ws_healthy else "high_connections",
                    "active_connections": ws_stats["stats"]["active_connections"],
                    "limit": ws_stats["limits"]["total"],
                    "healthy": ws_healthy
                },
                "cache": {
                    "status": "healthy" if cache_healthy else "low_hit_rate",
                    "hit_rate": cache_stats.get("hit_rate", 0),
                    "healthy": cache_healthy
                }
            },
            "overall_healthy": overall_healthy
        }
        
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(status_code=500, detail=f"Health check failed: {str(e)}")


@router.get("/metrics", response_model=Dict[str, Any])
@log_api_endpoint("api.performance")
async def get_performance_metrics():
    """Get comprehensive performance metrics"""
    try:
        # Database metrics
        db_stats = db_performance_monitor.get_stats()
        db_health = check_database_health()
        
        # Memory metrics
        memory_stats = memory_monitor.get_memory_summary()
        
        # WebSocket metrics
        ws_stats = websocket_manager.get_connection_stats()
        
        # Cache metrics
        cache_stats = await cache_manager.cache.get_stats()
        
        # Resource metrics
        resource_stats = resource_manager.get_resource_stats()
        
        return {
            "timestamp": datetime.now().isoformat(),
            "database": {
                "query_count": db_stats["query_count"],
                "slow_queries": db_stats["slow_queries"],
                "slow_query_rate": db_stats["slow_query_rate"],
                "connection_count": db_stats["connection_count"],
                "error_count": db_stats["error_count"],
                "pool_status": db_health.get("pool_status", {})
            },
            "memory": {
                "current_usage_mb": memory_stats["current"]["rss"] / 1024 / 1024,
                "peak_usage_mb": memory_stats["peak"] / 1024 / 1024,
                "usage_percent": memory_stats["current"]["percent"],
                "available_mb": memory_stats["current"]["available"] / 1024 / 1024,
                "threshold_exceeded": memory_stats["threshold_exceeded"],
                "cleanup_needed": memory_stats["cleanup_needed"]
            },
            "websockets": {
                "active_connections": ws_stats["stats"]["active_connections"],
                "total_connections": ws_stats["stats"]["total_connections"],
                "peak_connections": ws_stats["stats"]["peak_connections"],
                "cleaned_connections": ws_stats["stats"]["cleaned_connections"],
                "connections_by_user": ws_stats["connections_by_user"],
                "connections_by_room": ws_stats["connections_by_room"]
            },
            "cache": {
                "hit_rate": cache_stats.get("hit_rate", 0),
                "keyspace_hits": cache_stats.get("keyspace_hits", 0),
                "keyspace_misses": cache_stats.get("keyspace_misses", 0),
                "used_memory": cache_stats.get("used_memory", "0B"),
                "db_size": cache_stats.get("db_size", 0),
                "connected_clients": cache_stats.get("connected_clients", 0)
            },
            "resources": {
                "total_resources": resource_stats["total_resources"],
                "resources_by_age": resource_stats["resources_by_age"]
            }
        }
        
    except Exception as e:
        logger.error(f"Performance metrics failed: {e}")
        raise HTTPException(status_code=500, detail=f"Performance metrics failed: {str(e)}")


@router.get("/database/performance", response_model=Dict[str, Any])
@log_api_endpoint("api.performance")
async def get_database_performance():
    """Get detailed database performance metrics"""
    try:
        db_stats = db_performance_monitor.get_stats()
        db_health = check_database_health()
        
        return {
            "timestamp": datetime.now().isoformat(),
            "performance": db_stats,
            "health": db_health,
            "recommendations": _get_database_recommendations(db_stats, db_health)
        }
        
    except Exception as e:
        logger.error(f"Database performance check failed: {e}")
        raise HTTPException(status_code=500, detail=f"Database performance check failed: {str(e)}")


@router.get("/memory/usage", response_model=Dict[str, Any])
@log_api_endpoint("api.performance")
async def get_memory_usage():
    """Get detailed memory usage information"""
    try:
        memory_stats = memory_monitor.get_memory_summary()
        
        return {
            "timestamp": datetime.now().isoformat(),
            "memory": memory_stats,
            "recommendations": _get_memory_recommendations(memory_stats)
        }
        
    except Exception as e:
        logger.error(f"Memory usage check failed: {e}")
        raise HTTPException(status_code=500, detail=f"Memory usage check failed: {str(e)}")


@router.get("/cache/stats", response_model=Dict[str, Any])
@log_api_endpoint("api.performance")
async def get_cache_statistics():
    """Get detailed cache statistics"""
    try:
        cache_stats = await cache_manager.cache.get_stats()
        
        return {
            "timestamp": datetime.now().isoformat(),
            "cache": cache_stats,
            "recommendations": _get_cache_recommendations(cache_stats)
        }
        
    except Exception as e:
        logger.error(f"Cache statistics failed: {e}")
        raise HTTPException(status_code=500, detail=f"Cache statistics failed: {str(e)}")


@router.post("/optimize/memory")
@log_api_endpoint("api.performance")
async def optimize_memory():
    """Trigger memory optimization"""
    try:
        # Force garbage collection
        freed_memory, collected_objects = memory_monitor.force_garbage_collection()
        
        # Clean up WebSocket connections
        await websocket_manager.cleanup_inactive_connections()
        
        # Clean up resources
        await resource_manager.cleanup_unused_resources()
        
        return {
            "success": True,
            "timestamp": datetime.now().isoformat(),
            "optimization": {
                "freed_memory_mb": freed_memory / 1024 / 1024,
                "collected_objects": collected_objects,
                "websocket_cleanup": "completed",
                "resource_cleanup": "completed"
            }
        }
        
    except Exception as e:
        logger.error(f"Memory optimization failed: {e}")
        raise HTTPException(status_code=500, detail=f"Memory optimization failed: {str(e)}")


@router.post("/optimize/cache")
@log_api_endpoint("api.performance")
async def optimize_cache():
    """Trigger cache optimization"""
    try:
        # Clear old cache entries
        from app.core.cache import clear_all_cache
        cleared_count = await clear_all_cache()
        
        return {
            "success": True,
            "timestamp": datetime.now().isoformat(),
            "optimization": {
                "cleared_entries": cleared_count,
                "cache_optimization": "completed"
            }
        }
        
    except Exception as e:
        logger.error(f"Cache optimization failed: {e}")
        raise HTTPException(status_code=500, detail=f"Cache optimization failed: {str(e)}")


@router.get("/alerts", response_model=List[Dict[str, Any]])
@log_api_endpoint("api.performance")
async def get_performance_alerts():
    """Get current performance alerts"""
    try:
        alerts = []
        
        # Database alerts
        db_stats = db_performance_monitor.get_stats()
        if db_stats["slow_query_rate"] > 10:  # 10% slow query rate
            alerts.append({
                "type": "database",
                "severity": "warning",
                "message": f"High slow query rate: {db_stats['slow_query_rate']:.1f}%",
                "timestamp": datetime.now().isoformat()
            })
        
        # Memory alerts
        memory_stats = memory_monitor.get_memory_usage()
        if memory_stats["rss"] > 400 * 1024 * 1024:  # 400MB
            alerts.append({
                "type": "memory",
                "severity": "warning",
                "message": f"High memory usage: {memory_stats['rss'] / 1024 / 1024:.1f}MB",
                "timestamp": datetime.now().isoformat()
            })
        
        # WebSocket alerts
        ws_stats = websocket_manager.get_connection_stats()
        if ws_stats["stats"]["active_connections"] > 800:  # 80% of limit
            alerts.append({
                "type": "websocket",
                "severity": "warning",
                "message": f"High WebSocket connections: {ws_stats['stats']['active_connections']}",
                "timestamp": datetime.now().isoformat()
            })
        
        # Cache alerts
        cache_stats = await cache_manager.cache.get_stats()
        if cache_stats.get("hit_rate", 0) < 50:  # 50% hit rate
            alerts.append({
                "type": "cache",
                "severity": "warning",
                "message": f"Low cache hit rate: {cache_stats.get('hit_rate', 0):.1f}%",
                "timestamp": datetime.now().isoformat()
            })
        
        return alerts
        
    except Exception as e:
        logger.error(f"Performance alerts failed: {e}")
        raise HTTPException(status_code=500, detail=f"Performance alerts failed: {str(e)}")


def _get_database_recommendations(db_stats: Dict, db_health: Dict) -> List[str]:
    """Get database optimization recommendations"""
    recommendations = []
    
    if db_stats["slow_query_rate"] > 10:
        recommendations.append("Consider adding database indexes for frequently queried columns")
    
    if db_stats["slow_query_rate"] > 20:
        recommendations.append("Review and optimize slow queries")
    
    pool_status = db_health.get("pool_status", {})
    if pool_status.get("overflow", 0) > 10:
        recommendations.append("Consider increasing database connection pool size")
    
    if db_stats["error_count"] > 0:
        recommendations.append("Investigate database connection errors")
    
    return recommendations


def _get_memory_recommendations(memory_stats: Dict) -> List[str]:
    """Get memory optimization recommendations"""
    recommendations = []
    
    if memory_stats["threshold_exceeded"]:
        recommendations.append("Memory usage is high - consider optimizing data structures")
    
    if memory_stats["cleanup_needed"]:
        recommendations.append("Trigger garbage collection and resource cleanup")
    
    if memory_stats["current"]["percent"] > 80:
        recommendations.append("Consider increasing available memory or optimizing memory usage")
    
    return recommendations


def _get_cache_recommendations(cache_stats: Dict) -> List[str]:
    """Get cache optimization recommendations"""
    recommendations = []
    
    hit_rate = cache_stats.get("hit_rate", 0)
    if hit_rate < 50:
        recommendations.append("Cache hit rate is low - consider increasing cache TTL")
    
    if hit_rate < 30:
        recommendations.append("Review cache key strategies and data access patterns")
    
    db_size = cache_stats.get("db_size", 0)
    if db_size > 1000:
        recommendations.append("Cache size is large - consider implementing cache eviction policies")
    
    return recommendations

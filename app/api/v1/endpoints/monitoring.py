"""
Monitoring and Observability Endpoints for GenAI Metrics Dashboard
Comprehensive monitoring, metrics, and observability features
"""
from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.responses import JSONResponse
from typing import Dict, Any, List, Optional
import time
import psutil
import asyncio
from datetime import datetime, timedelta
import logging
from collections import defaultdict, deque
import json

from app.database import db_performance_monitor, check_database_health
from app.core.cache_manager import cache_manager
from app.core.error_handler import error_monitor
from app.config import settings

logger = logging.getLogger(__name__)
router = APIRouter()

class MetricsCollector:
    """Collect and aggregate application metrics"""
    
    def __init__(self):
        self.request_metrics = defaultdict(list)
        self.response_times = deque(maxlen=1000)
        self.error_counts = defaultdict(int)
        self.endpoint_usage = defaultdict(int)
        self.start_time = datetime.utcnow()
        self.metrics_history = deque(maxlen=100)  # Keep last 100 metric snapshots
    
    def record_request(self, endpoint: str, method: str, response_time: float, status_code: int):
        """Record request metrics"""
        self.endpoint_usage[f"{method} {endpoint}"] += 1
        self.response_times.append(response_time)
        
        if status_code >= 400:
            self.error_counts[f"{status_code}"] += 1
        
        # Store detailed metrics
        self.request_metrics[endpoint].append({
            "timestamp": datetime.utcnow().isoformat(),
            "method": method,
            "response_time": response_time,
            "status_code": status_code
        })
    
    def get_metrics_summary(self) -> Dict[str, Any]:
        """Get comprehensive metrics summary"""
        current_time = datetime.utcnow()
        uptime = (current_time - self.start_time).total_seconds()
        
        # Calculate response time statistics
        response_times = list(self.response_times)
        avg_response_time = sum(response_times) / len(response_times) if response_times else 0
        p95_response_time = sorted(response_times)[int(len(response_times) * 0.95)] if response_times else 0
        p99_response_time = sorted(response_times)[int(len(response_times) * 0.99)] if response_times else 0
        
        # Calculate request rate
        total_requests = sum(self.endpoint_usage.values())
        request_rate = total_requests / uptime if uptime > 0 else 0
        
        # Get top endpoints
        top_endpoints = sorted(
            self.endpoint_usage.items(),
            key=lambda x: x[1],
            reverse=True
        )[:10]
        
        return {
            "timestamp": current_time.isoformat(),
            "uptime_seconds": uptime,
            "requests": {
                "total": total_requests,
                "rate_per_second": round(request_rate, 2),
                "top_endpoints": top_endpoints
            },
            "response_times": {
                "average_ms": round(avg_response_time * 1000, 2),
                "p95_ms": round(p95_response_time * 1000, 2),
                "p99_ms": round(p99_response_time * 1000, 2),
                "min_ms": round(min(response_times) * 1000, 2) if response_times else 0,
                "max_ms": round(max(response_times) * 1000, 2) if response_times else 0
            },
            "errors": dict(self.error_counts),
            "system": {
                "cpu_percent": psutil.cpu_percent(),
                "memory_percent": psutil.virtual_memory().percent,
                "disk_percent": psutil.disk_usage('/').percent
            }
        }
    
    def get_endpoint_metrics(self, endpoint: str) -> Dict[str, Any]:
        """Get metrics for a specific endpoint"""
        if endpoint not in self.request_metrics:
            return {"error": "Endpoint not found"}
        
        metrics = self.request_metrics[endpoint]
        if not metrics:
            return {"error": "No metrics available"}
        
        # Calculate statistics
        response_times = [m["response_time"] for m in metrics]
        status_codes = [m["status_code"] for m in metrics]
        
        return {
            "endpoint": endpoint,
            "total_requests": len(metrics),
            "average_response_time_ms": round(sum(response_times) / len(response_times) * 1000, 2),
            "status_code_distribution": dict(zip(*np.unique(status_codes, return_counts=True))),
            "recent_requests": metrics[-10:]  # Last 10 requests
        }

# Global metrics collector
metrics_collector = MetricsCollector()

# Middleware to collect request metrics
async def collect_request_metrics(request: Request, call_next):
    """Middleware to collect request metrics"""
    start_time = time.time()
    
    try:
        response = await call_next(request)
        response_time = time.time() - start_time
        
        # Record metrics
        metrics_collector.record_request(
            endpoint=str(request.url.path),
            method=request.method,
            response_time=response_time,
            status_code=response.status_code
        )
        
        return response
    except Exception as e:
        response_time = time.time() - start_time
        metrics_collector.record_request(
            endpoint=str(request.url.path),
            method=request.method,
            response_time=response_time,
            status_code=500
        )
        raise

@router.get("/metrics", summary="Application Metrics")
async def get_metrics():
    """Get comprehensive application metrics"""
    return metrics_collector.get_metrics_summary()

@router.get("/metrics/endpoint/{endpoint:path}", summary="Endpoint Metrics")
async def get_endpoint_metrics(endpoint: str):
    """Get metrics for a specific endpoint"""
    return metrics_collector.get_endpoint_metrics(endpoint)

@router.get("/metrics/database", summary="Database Metrics")
async def get_database_metrics():
    """Get database performance metrics"""
    db_stats = db_performance_monitor.get_stats()
    db_health = check_database_health()
    
    return {
        "performance": db_stats,
        "health": db_health,
        "timestamp": datetime.utcnow().isoformat()
    }

@router.get("/metrics/cache", summary="Cache Metrics")
async def get_cache_metrics():
    """Get cache performance metrics"""
    cache_stats = cache_manager.get_stats()
    cache_health = check_cache_health()
    
    return {
        "performance": cache_stats,
        "health": cache_health,
        "timestamp": datetime.utcnow().isoformat()
    }

@router.get("/metrics/errors", summary="Error Metrics")
async def get_error_metrics():
    """Get error tracking metrics"""
    error_stats = error_monitor.get_error_stats()
    
    return {
        "error_tracking": error_stats,
        "timestamp": datetime.utcnow().isoformat()
    }

@router.get("/metrics/system", summary="System Metrics")
async def get_system_metrics():
    """Get system resource metrics"""
    cpu_percent = psutil.cpu_percent(interval=1)
    memory = psutil.virtual_memory()
    disk = psutil.disk_usage('/')
    
    # Network stats
    network_io = psutil.net_io_counters()
    
    # Process stats
    process = psutil.Process()
    process_memory = process.memory_info()
    
    return {
        "timestamp": datetime.utcnow().isoformat(),
        "cpu": {
            "usage_percent": cpu_percent,
            "count": psutil.cpu_count(),
            "frequency": psutil.cpu_freq().current if psutil.cpu_freq() else None
        },
        "memory": {
            "total_gb": round(memory.total / (1024**3), 2),
            "available_gb": round(memory.available / (1024**3), 2),
            "used_gb": round(memory.used / (1024**3), 2),
            "usage_percent": memory.percent,
            "process_memory_mb": round(process_memory.rss / (1024**2), 2)
        },
        "disk": {
            "total_gb": round(disk.total / (1024**3), 2),
            "free_gb": round(disk.free / (1024**3), 2),
            "used_gb": round(disk.used / (1024**3), 2),
            "usage_percent": disk.percent
        },
        "network": {
            "bytes_sent": network_io.bytes_sent,
            "bytes_recv": network_io.bytes_recv,
            "packets_sent": network_io.packets_sent,
            "packets_recv": network_io.packets_recv
        }
    }

@router.get("/metrics/performance", summary="Performance Metrics")
async def get_performance_metrics():
    """Get detailed performance metrics"""
    metrics_summary = metrics_collector.get_metrics_summary()
    
    # Add additional performance indicators
    performance_metrics = {
        **metrics_summary,
        "performance_indicators": {
            "high_response_time_requests": len([
                rt for rt in metrics_collector.response_times 
                if rt > 1.0  # Requests taking more than 1 second
            ]),
            "error_rate": (
                sum(metrics_collector.error_counts.values()) / 
                sum(metrics_collector.endpoint_usage.values()) * 100
            ) if metrics_collector.endpoint_usage else 0,
            "throughput_per_minute": (
                sum(metrics_collector.endpoint_usage.values()) / 
                (metrics_summary["uptime_seconds"] / 60)
            ) if metrics_summary["uptime_seconds"] > 0 else 0
        }
    }
    
    return performance_metrics

@router.get("/metrics/alerts", summary="Alert Metrics")
async def get_alert_metrics():
    """Get alerting metrics and thresholds"""
    metrics_summary = metrics_collector.get_metrics_summary()
    
    # Define alert thresholds
    thresholds = {
        "cpu_percent": 80,
        "memory_percent": 85,
        "disk_percent": 90,
        "response_time_ms": 1000,
        "error_rate_percent": 5
    }
    
    # Check for alerts
    alerts = []
    
    if metrics_summary["system"]["cpu_percent"] > thresholds["cpu_percent"]:
        alerts.append({
            "type": "cpu_high",
            "message": f"CPU usage is {metrics_summary['system']['cpu_percent']}%",
            "severity": "warning"
        })
    
    if metrics_summary["system"]["memory_percent"] > thresholds["memory_percent"]:
        alerts.append({
            "type": "memory_high",
            "message": f"Memory usage is {metrics_summary['system']['memory_percent']}%",
            "severity": "warning"
        })
    
    if metrics_summary["response_times"]["p95_ms"] > thresholds["response_time_ms"]:
        alerts.append({
            "type": "response_time_high",
            "message": f"P95 response time is {metrics_summary['response_times']['p95_ms']}ms",
            "severity": "warning"
        })
    
    return {
        "thresholds": thresholds,
        "alerts": alerts,
        "timestamp": datetime.utcnow().isoformat()
    }

@router.get("/metrics/history", summary="Metrics History")
async def get_metrics_history(hours: int = 1):
    """Get historical metrics"""
    # This would typically query a time-series database
    # For now, return current metrics with timestamp
    return {
        "period_hours": hours,
        "current_metrics": metrics_collector.get_metrics_summary(),
        "note": "Historical metrics would be stored in a time-series database"
    }

@router.post("/metrics/reset", summary="Reset Metrics")
async def reset_metrics():
    """Reset all metrics (for testing purposes)"""
    metrics_collector.request_metrics.clear()
    metrics_collector.response_times.clear()
    metrics_collector.error_counts.clear()
    metrics_collector.endpoint_usage.clear()
    metrics_collector.start_time = datetime.utcnow()
    
    return {
        "message": "Metrics reset successfully",
        "timestamp": datetime.utcnow().isoformat()
    }

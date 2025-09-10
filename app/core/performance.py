"""
Performance Optimization Module for GenAI Metrics Dashboard
Implements various performance optimizations and monitoring
"""
import time
import asyncio
import functools
import logging
from typing import Any, Callable, Dict, List, Optional, Union
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
import psutil
import gc
from datetime import datetime, timedelta
from collections import defaultdict, deque
import json

logger = logging.getLogger(__name__)

class PerformanceOptimizer:
    """Performance optimization utilities"""
    
    def __init__(self):
        self.thread_pool = ThreadPoolExecutor(max_workers=4)
        self.process_pool = ProcessPoolExecutor(max_workers=2)
        self.cache_stats = defaultdict(int)
        self.query_stats = defaultdict(list)
        self.start_time = time.time()
    
    def async_timeout(self, timeout_seconds: float = 30):
        """Decorator to add timeout to async functions"""
        def decorator(func):
            @functools.wraps(func)
            async def wrapper(*args, **kwargs):
                try:
                    return await asyncio.wait_for(
                        func(*args, **kwargs),
                        timeout=timeout_seconds
                    )
                except asyncio.TimeoutError:
                    logger.warning(f"Function {func.__name__} timed out after {timeout_seconds}s")
                    raise
            return wrapper
        return decorator
    
    def cache_result(self, ttl_seconds: int = 300):
        """Decorator to cache function results"""
        def decorator(func):
            cache = {}
            
            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                # Create cache key
                key = str(hash(str(args) + str(sorted(kwargs.items()))))
                
                # Check cache
                if key in cache:
                    cache_entry = cache[key]
                    if time.time() - cache_entry['timestamp'] < ttl_seconds:
                        self.cache_stats['hits'] += 1
                        return cache_entry['result']
                    else:
                        del cache[key]
                
                # Execute function and cache result
                result = func(*args, **kwargs)
                cache[key] = {
                    'result': result,
                    'timestamp': time.time()
                }
                self.cache_stats['misses'] += 1
                
                return result
            return wrapper
        return decorator
    
    def batch_operations(self, batch_size: int = 100):
        """Decorator to batch database operations"""
        def decorator(func):
            @functools.wraps(func)
            async def wrapper(*args, **kwargs):
                # If args[0] is a list, batch it
                if args and isinstance(args[0], list):
                    items = args[0]
                    results = []
                    
                    for i in range(0, len(items), batch_size):
                        batch = items[i:i + batch_size]
                        batch_args = (batch,) + args[1:]
                        batch_result = await func(*batch_args, **kwargs)
                        results.extend(batch_result)
                    
                    return results
                else:
                    return await func(*args, **kwargs)
            return wrapper
        return decorator
    
    def connection_pooling(self, max_connections: int = 20):
        """Configure connection pooling for database"""
        # This would typically be configured in the database module
        logger.info(f"Configuring connection pooling with max {max_connections} connections")
    
    def query_optimization(self, func):
        """Decorator to optimize database queries"""
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            start_time = time.time()
            
            try:
                result = await func(*args, **kwargs)
                
                # Log query performance
                execution_time = time.time() - start_time
                self.query_stats[func.__name__].append(execution_time)
                
                if execution_time > 1.0:  # Slow query threshold
                    logger.warning(f"Slow query detected: {func.__name__} took {execution_time:.3f}s")
                
                return result
                
            except Exception as e:
                execution_time = time.time() - start_time
                logger.error(f"Query failed: {func.__name__} after {execution_time:.3f}s - {e}")
                raise
        
        return wrapper
    
    def memory_optimization(self):
        """Optimize memory usage"""
        # Force garbage collection
        collected = gc.collect()
        logger.info(f"Garbage collection freed {collected} objects")
        
        # Log memory usage
        memory_info = psutil.virtual_memory()
        logger.info(f"Memory usage: {memory_info.percent}% ({memory_info.used / 1024**3:.2f}GB used)")
        
        return {
            "gc_collected": collected,
            "memory_percent": memory_info.percent,
            "memory_used_gb": memory_info.used / 1024**3
        }
    
    def cpu_optimization(self):
        """Optimize CPU usage"""
        cpu_percent = psutil.cpu_percent(interval=1)
        
        if cpu_percent > 80:
            logger.warning(f"High CPU usage detected: {cpu_percent}%")
        
        return {
            "cpu_percent": cpu_percent,
            "cpu_count": psutil.cpu_count(),
            "load_average": psutil.getloadavg() if hasattr(psutil, 'getloadavg') else None
        }
    
    def get_performance_stats(self) -> Dict[str, Any]:
        """Get comprehensive performance statistics"""
        uptime = time.time() - self.start_time
        
        # Calculate query statistics
        query_stats = {}
        for func_name, times in self.query_stats.items():
            if times:
                query_stats[func_name] = {
                    "count": len(times),
                    "avg_time": sum(times) / len(times),
                    "min_time": min(times),
                    "max_time": max(times),
                    "total_time": sum(times)
                }
        
        # Calculate cache statistics
        total_cache_requests = self.cache_stats['hits'] + self.cache_stats['misses']
        cache_hit_rate = (self.cache_stats['hits'] / total_cache_requests * 100) if total_cache_requests > 0 else 0
        
        return {
            "uptime_seconds": uptime,
            "cache_stats": {
                "hits": self.cache_stats['hits'],
                "misses": self.cache_stats['misses'],
                "hit_rate_percent": cache_hit_rate
            },
            "query_stats": query_stats,
            "system_stats": {
                "memory": psutil.virtual_memory()._asdict(),
                "cpu": {
                    "percent": psutil.cpu_percent(),
                    "count": psutil.cpu_count()
                },
                "disk": psutil.disk_usage('/')._asdict()
            }
        }

# Global performance optimizer
performance_optimizer = PerformanceOptimizer()

class DatabaseOptimizer:
    """Database-specific optimizations"""
    
    @staticmethod
    def optimize_query(query: str) -> str:
        """Optimize SQL query"""
        # Basic query optimizations
        optimized = query.strip()
        
        # Remove unnecessary whitespace
        optimized = ' '.join(optimized.split())
        
        # Add query hints for PostgreSQL
        if 'SELECT' in optimized.upper():
            # Add index hints if needed
            pass
        
        return optimized
    
    @staticmethod
    def create_indexes_for_common_queries():
        """Create indexes for common query patterns"""
        common_indexes = [
            "CREATE INDEX IF NOT EXISTS idx_projects_status_created ON projects(status, created_at)",
            "CREATE INDEX IF NOT EXISTS idx_features_project_status ON features(project_id, status)",
            "CREATE INDEX IF NOT EXISTS idx_resources_project_type ON resources(project_id, resource_type)",
            "CREATE INDEX IF NOT EXISTS idx_risks_project_level ON risks(project_id, risk_level)",
            "CREATE INDEX IF NOT EXISTS idx_analytics_project_metric ON analytics(project_id, metric_type)",
        ]
        
        return common_indexes
    
    @staticmethod
    def analyze_query_performance(query: str) -> Dict[str, Any]:
        """Analyze query performance"""
        # This would typically use EXPLAIN ANALYZE
        return {
            "query": query,
            "estimated_cost": "N/A",
            "execution_time": "N/A",
            "rows_returned": "N/A",
            "indexes_used": []
        }

class APIOptimizer:
    """API-specific optimizations"""
    
    @staticmethod
    def compress_response(data: Any) -> bytes:
        """Compress API response data"""
        import gzip
        import json
        
        json_data = json.dumps(data, default=str).encode('utf-8')
        compressed = gzip.compress(json_data)
        
        compression_ratio = len(compressed) / len(json_data)
        logger.info(f"Response compressed by {compression_ratio:.2%}")
        
        return compressed
    
    @staticmethod
    def paginate_large_datasets(data: List[Any], page: int = 1, size: int = 20) -> Dict[str, Any]:
        """Paginate large datasets efficiently"""
        total = len(data)
        start = (page - 1) * size
        end = start + size
        
        paginated_data = data[start:end]
        
        return {
            "data": paginated_data,
            "pagination": {
                "page": page,
                "size": size,
                "total": total,
                "pages": (total + size - 1) // size,
                "has_next": end < total,
                "has_prev": page > 1
            }
        }
    
    @staticmethod
    def batch_api_calls(requests: List[Dict[str, Any]], batch_size: int = 10) -> List[Any]:
        """Batch API calls for better performance"""
        results = []
        
        for i in range(0, len(requests), batch_size):
            batch = requests[i:i + batch_size]
            # Process batch concurrently
            batch_results = asyncio.gather(*[
                asyncio.create_task(process_request(req)) for req in batch
            ])
            results.extend(batch_results)
        
        return results

class MemoryOptimizer:
    """Memory optimization utilities"""
    
    @staticmethod
    def optimize_data_structures(data: Any) -> Any:
        """Optimize data structures for memory usage"""
        if isinstance(data, list):
            # Use generators for large lists
            if len(data) > 1000:
                return (item for item in data)
        
        elif isinstance(data, dict):
            # Remove None values
            return {k: v for k, v in data.items() if v is not None}
        
        return data
    
    @staticmethod
    def clear_unused_cache():
        """Clear unused cache entries"""
        # This would typically integrate with the cache manager
        logger.info("Clearing unused cache entries")
    
    @staticmethod
    def monitor_memory_usage():
        """Monitor memory usage and alert if high"""
        memory_info = psutil.virtual_memory()
        
        if memory_info.percent > 85:
            logger.warning(f"High memory usage: {memory_info.percent}%")
            return {
                "status": "warning",
                "memory_percent": memory_info.percent,
                "recommendation": "Consider clearing cache or optimizing data structures"
            }
        
        return {
            "status": "normal",
            "memory_percent": memory_info.percent
        }

class PerformanceMonitor:
    """Performance monitoring and alerting"""
    
    def __init__(self):
        self.metrics_history = deque(maxlen=1000)
        self.alert_thresholds = {
            "response_time_ms": 1000,
            "memory_percent": 85,
            "cpu_percent": 80,
            "error_rate_percent": 5
        }
    
    def record_metric(self, metric_name: str, value: float, timestamp: datetime = None):
        """Record a performance metric"""
        if timestamp is None:
            timestamp = datetime.now()
        
        self.metrics_history.append({
            "name": metric_name,
            "value": value,
            "timestamp": timestamp.isoformat()
        })
    
    def check_alerts(self) -> List[Dict[str, Any]]:
        """Check for performance alerts"""
        alerts = []
        
        # Check recent metrics
        recent_metrics = list(self.metrics_history)[-100:]  # Last 100 metrics
        
        for metric in recent_metrics:
            metric_name = metric["name"]
            value = metric["value"]
            
            if metric_name in self.alert_thresholds:
                threshold = self.alert_thresholds[metric_name]
                
                if value > threshold:
                    alerts.append({
                        "type": f"{metric_name}_high",
                        "message": f"{metric_name} is {value} (threshold: {threshold})",
                        "severity": "warning",
                        "timestamp": metric["timestamp"]
                    })
        
        return alerts
    
    def get_performance_trends(self, hours: int = 1) -> Dict[str, Any]:
        """Get performance trends over time"""
        cutoff_time = datetime.now() - timedelta(hours=hours)
        
        recent_metrics = [
            m for m in self.metrics_history
            if datetime.fromisoformat(m["timestamp"]) > cutoff_time
        ]
        
        # Group metrics by name
        metrics_by_name = defaultdict(list)
        for metric in recent_metrics:
            metrics_by_name[metric["name"]].append(metric["value"])
        
        trends = {}
        for name, values in metrics_by_name.items():
            if values:
                trends[name] = {
                    "count": len(values),
                    "avg": sum(values) / len(values),
                    "min": min(values),
                    "max": max(values),
                    "trend": "increasing" if len(values) > 1 and values[-1] > values[0] else "decreasing"
                }
        
        return {
            "period_hours": hours,
            "trends": trends,
            "alerts": self.check_alerts()
        }

# Global performance monitor
performance_monitor = PerformanceMonitor()

# Performance decorators for easy use
def optimize_performance(func):
    """Decorator to apply performance optimizations"""
    return performance_optimizer.query_optimization(func)

def monitor_performance(metric_name: str):
    """Decorator to monitor function performance"""
    def decorator(func):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            start_time = time.time()
            
            try:
                result = await func(*args, **kwargs)
                execution_time = time.time() - start_time
                
                # Record metric
                performance_monitor.record_metric(
                    f"{metric_name}_execution_time",
                    execution_time * 1000  # Convert to milliseconds
                )
                
                return result
                
            except Exception as e:
                execution_time = time.time() - start_time
                performance_monitor.record_metric(
                    f"{metric_name}_error_rate",
                    1  # Record error
                )
                raise
        
        return wrapper
    return decorator

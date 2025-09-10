"""
Enhanced Cache Manager for GenAI Metrics Dashboard
Implements Redis-based caching with intelligent invalidation and performance optimization
"""
import json
import pickle
import hashlib
from typing import Any, Optional, Dict, List, Union, Callable
from datetime import datetime, timedelta
import redis
import logging
from functools import wraps
import asyncio

logger = logging.getLogger(__name__)

class CacheManager:
    """Enhanced cache manager with Redis backend"""
    
    def __init__(self, redis_url: str = "redis://localhost:6379"):
        self.redis_client = redis.from_url(redis_url, decode_responses=False)
        self.default_ttl = 300  # 5 minutes default
        self.cache_stats = {
            "hits": 0,
            "misses": 0,
            "sets": 0,
            "deletes": 0,
            "errors": 0
        }
    
    def _serialize(self, data: Any) -> bytes:
        """Serialize data for storage"""
        try:
            # Try JSON first for simple data types
            return json.dumps(data, default=str).encode('utf-8')
        except (TypeError, ValueError):
            # Fall back to pickle for complex objects
            return pickle.dumps(data)
    
    def _deserialize(self, data: bytes) -> Any:
        """Deserialize data from storage"""
        try:
            # Try JSON first
            return json.loads(data.decode('utf-8'))
        except (json.JSONDecodeError, UnicodeDecodeError):
            # Fall back to pickle
            return pickle.loads(data)
    
    def _generate_key(self, prefix: str, *args, **kwargs) -> str:
        """Generate cache key from arguments"""
        key_parts = [prefix]
        
        # Add positional arguments
        for arg in args:
            if isinstance(arg, (str, int, float, bool)):
                key_parts.append(str(arg))
            else:
                key_parts.append(hashlib.md5(str(arg).encode()).hexdigest()[:8])
        
        # Add keyword arguments
        for key, value in sorted(kwargs.items()):
            if isinstance(value, (str, int, float, bool)):
                key_parts.append(f"{key}:{value}")
            else:
                key_parts.append(f"{key}:{hashlib.md5(str(value).encode()).hexdigest()[:8]}")
        
        return ":".join(key_parts)
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        try:
            data = self.redis_client.get(key)
            if data is not None:
                self.cache_stats["hits"] += 1
                return self._deserialize(data)
            else:
                self.cache_stats["misses"] += 1
                return None
        except Exception as e:
            logger.error(f"Cache get error: {e}")
            self.cache_stats["errors"] += 1
            return None
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Set value in cache"""
        try:
            serialized_data = self._serialize(value)
            ttl = ttl or self.default_ttl
            
            result = self.redis_client.setex(key, ttl, serialized_data)
            if result:
                self.cache_stats["sets"] += 1
            return result
        except Exception as e:
            logger.error(f"Cache set error: {e}")
            self.cache_stats["errors"] += 1
            return False
    
    def delete(self, key: str) -> bool:
        """Delete key from cache"""
        try:
            result = self.redis_client.delete(key)
            if result:
                self.cache_stats["deletes"] += 1
            return bool(result)
        except Exception as e:
            logger.error(f"Cache delete error: {e}")
            self.cache_stats["errors"] += 1
            return False
    
    def delete_pattern(self, pattern: str) -> int:
        """Delete all keys matching pattern"""
        try:
            keys = self.redis_client.keys(pattern)
            if keys:
                result = self.redis_client.delete(*keys)
                self.cache_stats["deletes"] += result
                return result
            return 0
        except Exception as e:
            logger.error(f"Cache delete pattern error: {e}")
            self.cache_stats["errors"] += 1
            return 0
    
    def exists(self, key: str) -> bool:
        """Check if key exists in cache"""
        try:
            return bool(self.redis_client.exists(key))
        except Exception as e:
            logger.error(f"Cache exists error: {e}")
            self.cache_stats["errors"] += 1
            return False
    
    def ttl(self, key: str) -> int:
        """Get TTL for key"""
        try:
            return self.redis_client.ttl(key)
        except Exception as e:
            logger.error(f"Cache TTL error: {e}")
            self.cache_stats["errors"] += 1
            return -1
    
    def increment(self, key: str, amount: int = 1) -> Optional[int]:
        """Increment counter in cache"""
        try:
            return self.redis_client.incrby(key, amount)
        except Exception as e:
            logger.error(f"Cache increment error: {e}")
            self.cache_stats["errors"] += 1
            return None
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        total_requests = self.cache_stats["hits"] + self.cache_stats["misses"]
        hit_rate = (self.cache_stats["hits"] / total_requests * 100) if total_requests > 0 else 0
        
        return {
            **self.cache_stats,
            "hit_rate": round(hit_rate, 2),
            "total_requests": total_requests
        }
    
    def clear_stats(self):
        """Clear cache statistics"""
        self.cache_stats = {
            "hits": 0,
            "misses": 0,
            "sets": 0,
            "deletes": 0,
            "errors": 0
        }

# Global cache manager instance
cache_manager = CacheManager()

# Cache decorators
def cached(prefix: str, ttl: int = 300, key_func: Optional[Callable] = None):
    """Decorator to cache function results"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Generate cache key
            if key_func:
                cache_key = key_func(*args, **kwargs)
            else:
                cache_key = cache_manager._generate_key(prefix, *args, **kwargs)
            
            # Try to get from cache
            cached_result = cache_manager.get(cache_key)
            if cached_result is not None:
                logger.debug(f"Cache hit for {cache_key}")
                return cached_result
            
            # Execute function and cache result
            logger.debug(f"Cache miss for {cache_key}")
            result = func(*args, **kwargs)
            cache_manager.set(cache_key, result, ttl)
            return result
        
        return wrapper
    return decorator

def async_cached(prefix: str, ttl: int = 300, key_func: Optional[Callable] = None):
    """Decorator to cache async function results"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Generate cache key
            if key_func:
                cache_key = key_func(*args, **kwargs)
            else:
                cache_key = cache_manager._generate_key(prefix, *args, **kwargs)
            
            # Try to get from cache
            cached_result = cache_manager.get(cache_key)
            if cached_result is not None:
                logger.debug(f"Cache hit for {cache_key}")
                return cached_result
            
            # Execute function and cache result
            logger.debug(f"Cache miss for {cache_key}")
            result = await func(*args, **kwargs)
            cache_manager.set(cache_key, result, ttl)
            return result
        
        return wrapper
    return decorator

# Cache invalidation helpers
class CacheInvalidator:
    """Helper class for cache invalidation"""
    
    @staticmethod
    def invalidate_project_cache(project_id: int):
        """Invalidate all project-related cache"""
        patterns = [
            f"project:{project_id}:*",
            f"projects:*",
            f"dashboard:*",
            f"analytics:*"
        ]
        
        for pattern in patterns:
            cache_manager.delete_pattern(pattern)
        logger.info(f"Invalidated cache for project {project_id}")
    
    @staticmethod
    def invalidate_user_cache(user_id: int):
        """Invalidate all user-related cache"""
        patterns = [
            f"user:{user_id}:*",
            f"projects:*",
            f"dashboard:*"
        ]
        
        for pattern in patterns:
            cache_manager.delete_pattern(pattern)
        logger.info(f"Invalidated cache for user {user_id}")
    
    @staticmethod
    def invalidate_global_cache():
        """Invalidate all cache"""
        cache_manager.delete_pattern("*")
        logger.info("Invalidated all cache")

# Cache warming functions
class CacheWarmer:
    """Helper class for cache warming"""
    
    @staticmethod
    def warm_project_cache(project_id: int):
        """Warm cache for a specific project"""
        # This would typically call the actual functions to populate cache
        logger.info(f"Warming cache for project {project_id}")
    
    @staticmethod
    def warm_dashboard_cache():
        """Warm dashboard cache"""
        logger.info("Warming dashboard cache")
    
    @staticmethod
    def warm_analytics_cache():
        """Warm analytics cache"""
        logger.info("Warming analytics cache")

# Cache health check
def check_cache_health() -> Dict[str, Any]:
    """Check cache health"""
    try:
        # Test basic operations
        test_key = "health_check"
        test_value = {"timestamp": datetime.utcnow().isoformat()}
        
        # Test set
        set_result = cache_manager.set(test_key, test_value, 60)
        
        # Test get
        get_result = cache_manager.get(test_key)
        
        # Test delete
        delete_result = cache_manager.delete(test_key)
        
        # Get Redis info
        redis_info = cache_manager.redis_client.info()
        
        return {
            "status": "healthy" if all([set_result, get_result, delete_result]) else "unhealthy",
            "operations": {
                "set": set_result,
                "get": get_result is not None,
                "delete": delete_result
            },
            "redis_info": {
                "version": redis_info.get("redis_version"),
                "uptime": redis_info.get("uptime_in_seconds"),
                "connected_clients": redis_info.get("connected_clients"),
                "used_memory": redis_info.get("used_memory_human"),
                "keyspace": redis_info.get("db0", {})
            },
            "cache_stats": cache_manager.get_stats()
        }
        
    except Exception as e:
        logger.error(f"Cache health check failed: {e}")
        return {
            "status": "unhealthy",
            "error": str(e)
        }

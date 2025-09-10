"""
Redis Caching Infrastructure
Provides comprehensive caching capabilities for the application
"""

import json
import hashlib
import asyncio
from typing import Any, Optional, Dict, List, Union
from functools import wraps
import redis.asyncio as redis
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


class CacheConfig:
    """Cache configuration settings"""
    
    # Redis connection settings
    REDIS_HOST = "localhost"
    REDIS_PORT = 6379
    REDIS_DB = 0
    REDIS_PASSWORD = None
    REDIS_DECODE_RESPONSES = True
    
    # Cache TTL settings (in seconds)
    DEFAULT_TTL = 300  # 5 minutes
    CACHE_TTL = {
        "projects": 300,      # 5 minutes
        "features": 180,       # 3 minutes
        "backlogs": 180,       # 3 minutes
        "resources": 600,      # 10 minutes
        "dashboard": 60,      # 1 minute
        "reports": 900,       # 15 minutes
        "lookup_tables": 3600, # 1 hour
        "user_sessions": 1800, # 30 minutes
        "api_responses": 300,  # 5 minutes
        "ai_responses": 3600,  # 1 hour
        "fast_responses": 900  # 15 minutes
    }
    
    # Cache key prefixes
    KEY_PREFIXES = {
        "projects": "proj:",
        "features": "feat:",
        "backlogs": "back:",
        "resources": "res:",
        "dashboard": "dash:",
        "reports": "rep:",
        "lookup_tables": "lookup:",
        "user_sessions": "session:",
        "api_responses": "api:",
        "ai_responses": "ai:",
        "fast_responses": "fast:"
    }


class RedisCache:
    """Redis cache implementation with async support"""
    
    def __init__(self, config: CacheConfig = None):
        self.config = config or CacheConfig()
        self.redis_client = None
        self._connection_pool = None
    
    async def connect(self):
        """Initialize Redis connection"""
        try:
            self._connection_pool = redis.ConnectionPool(
                host=self.config.REDIS_HOST,
                port=self.config.REDIS_PORT,
                db=self.config.REDIS_DB,
                password=self.config.REDIS_PASSWORD,
                decode_responses=self.config.REDIS_DECODE_RESPONSES,
                max_connections=20
            )
            
            self.redis_client = redis.Redis(connection_pool=self._connection_pool)
            
            # Test connection
            await self.redis_client.ping()
            logger.info("✅ Redis cache connected successfully")
            
        except Exception as e:
            logger.error(f"❌ Failed to connect to Redis: {e}")
            raise
    
    async def disconnect(self):
        """Close Redis connection"""
        if self.redis_client:
            await self.redis_client.close()
            logger.info("🔌 Redis cache disconnected")
    
    def _generate_key(self, cache_type: str, identifier: str) -> str:
        """Generate cache key with prefix"""
        prefix = self.config.KEY_PREFIXES.get(cache_type, "cache:")
        return f"{prefix}{identifier}"
    
    def _serialize_data(self, data: Any) -> str:
        """Serialize data for caching"""
        try:
            return json.dumps(data, default=str)
        except Exception as e:
            logger.error(f"Failed to serialize data: {e}")
            return json.dumps({"error": "serialization_failed"})
    
    def _deserialize_data(self, data: str) -> Any:
        """Deserialize cached data"""
        try:
            return json.loads(data)
        except Exception as e:
            logger.error(f"Failed to deserialize data: {e}")
            return None
    
    async def get(self, cache_type: str, identifier: str) -> Optional[Any]:
        """Get data from cache"""
        if not self.redis_client:
            return None
        
        try:
            key = self._generate_key(cache_type, identifier)
            data = await self.redis_client.get(key)
            
            if data:
                logger.debug(f"📦 Cache hit: {key}")
                return self._deserialize_data(data)
            else:
                logger.debug(f"❌ Cache miss: {key}")
                return None
                
        except Exception as e:
            logger.error(f"Cache get error: {e}")
            return None
    
    async def set(self, cache_type: str, identifier: str, data: Any, ttl: Optional[int] = None) -> bool:
        """Set data in cache"""
        if not self.redis_client:
            return False
        
        try:
            key = self._generate_key(cache_type, identifier)
            serialized_data = self._serialize_data(data)
            
            # Use provided TTL or default for cache type
            if ttl is None:
                ttl = self.config.CACHE_TTL.get(cache_type, self.config.DEFAULT_TTL)
            
            await self.redis_client.setex(key, ttl, serialized_data)
            logger.debug(f"💾 Cache set: {key} (TTL: {ttl}s)")
            return True
            
        except Exception as e:
            logger.error(f"Cache set error: {e}")
            return False
    
    async def delete(self, cache_type: str, identifier: str) -> bool:
        """Delete data from cache"""
        if not self.redis_client:
            return False
        
        try:
            key = self._generate_key(cache_type, identifier)
            result = await self.redis_client.delete(key)
            logger.debug(f"🗑️ Cache delete: {key}")
            return bool(result)
            
        except Exception as e:
            logger.error(f"Cache delete error: {e}")
            return False
    
    async def clear_pattern(self, pattern: str) -> int:
        """Clear cache entries matching pattern"""
        if not self.redis_client:
            return 0
        
        try:
            keys = await self.redis_client.keys(pattern)
            if keys:
                result = await self.redis_client.delete(*keys)
                logger.info(f"🧹 Cleared {result} cache entries matching: {pattern}")
                return result
            return 0
            
        except Exception as e:
            logger.error(f"Cache clear pattern error: {e}")
            return 0
    
    async def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        if not self.redis_client:
            return {"error": "Redis not connected"}
        
        try:
            info = await self.redis_client.info()
            return {
                "connected_clients": info.get("connected_clients", 0),
                "used_memory": info.get("used_memory_human", "0B"),
                "total_commands_processed": info.get("total_commands_processed", 0),
                "keyspace_hits": info.get("keyspace_hits", 0),
                "keyspace_misses": info.get("keyspace_misses", 0),
                "hit_rate": self._calculate_hit_rate(info),
                "db_size": await self.redis_client.dbsize()
            }
        except Exception as e:
            logger.error(f"Cache stats error: {e}")
            return {"error": str(e)}
    
    def _calculate_hit_rate(self, info: Dict) -> float:
        """Calculate cache hit rate"""
        hits = info.get("keyspace_hits", 0)
        misses = info.get("keyspace_misses", 0)
        total = hits + misses
        return (hits / total * 100) if total > 0 else 0.0


class CacheManager:
    """Centralized cache management"""
    
    def __init__(self):
        self.cache = RedisCache()
        self._initialized = False
    
    async def initialize(self):
        """Initialize cache manager"""
        if not self._initialized:
            await self.cache.connect()
            self._initialized = True
    
    async def shutdown(self):
        """Shutdown cache manager"""
        if self._initialized:
            await self.cache.disconnect()
            self._initialized = False
    
    # Convenience methods
    async def get_project(self, project_id: int) -> Optional[Dict]:
        """Get cached project data"""
        return await self.cache.get("projects", str(project_id))
    
    async def set_project(self, project_id: int, data: Dict) -> bool:
        """Cache project data"""
        return await self.cache.set("projects", str(project_id), data)
    
    async def get_dashboard_data(self, user_id: int) -> Optional[Dict]:
        """Get cached dashboard data"""
        return await self.cache.get("dashboard", f"user_{user_id}")
    
    async def set_dashboard_data(self, user_id: int, data: Dict) -> bool:
        """Cache dashboard data"""
        return await self.cache.set("dashboard", f"user_{user_id}", data)
    
    async def clear_user_cache(self, user_id: int):
        """Clear all cache for a user"""
        patterns = [
            f"dash:user_{user_id}",
            f"session:user_{user_id}*",
            f"api:*user_{user_id}*"
        ]
        
        for pattern in patterns:
            await self.cache.clear_pattern(pattern)
    
    async def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        return await self.cache.get_stats()


# Global cache manager instance
cache_manager = CacheManager()


def cache_result(cache_type: str, ttl: Optional[int] = None, key_func: Optional[callable] = None):
    """
    Decorator for caching function results
    
    Args:
        cache_type: Type of cache (projects, features, etc.)
        ttl: Time to live in seconds
        key_func: Function to generate cache key from function arguments
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Generate cache key
            if key_func:
                cache_key = key_func(*args, **kwargs)
            else:
                # Default key generation
                key_data = str(args) + str(sorted(kwargs.items()))
                cache_key = hashlib.md5(key_data.encode()).hexdigest()
            
            # Try to get from cache
            cached_result = await cache_manager.cache.get(cache_type, cache_key)
            if cached_result is not None:
                logger.debug(f"🎯 Cache hit for {func.__name__}: {cache_key}")
                return cached_result
            
            # Execute function and cache result
            result = await func(*args, **kwargs)
            await cache_manager.cache.set(cache_type, cache_key, result, ttl)
            logger.debug(f"💾 Cached result for {func.__name__}: {cache_key}")
            
            return result
        
        return wrapper
    return decorator


def cache_invalidate(cache_type: str, key_func: Optional[callable] = None):
    """
    Decorator for invalidating cache after function execution
    
    Args:
        cache_type: Type of cache to invalidate
        key_func: Function to generate cache key from function arguments
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Execute function
            result = await func(*args, **kwargs)
            
            # Invalidate cache
            if key_func:
                cache_key = key_func(*args, **kwargs)
                await cache_manager.cache.delete(cache_type, cache_key)
                logger.debug(f"🗑️ Invalidated cache for {func.__name__}: {cache_key}")
            
            return result
        
        return wrapper
    return decorator


# Cache utility functions
async def warm_cache():
    """Warm up frequently accessed cache entries"""
    logger.info("🔥 Warming up cache...")
    
    # This would be implemented based on specific application needs
    # For example, pre-loading lookup tables, popular projects, etc.
    
    logger.info("✅ Cache warm-up completed")


async def clear_all_cache():
    """Clear all cache entries"""
    logger.info("🧹 Clearing all cache...")
    
    patterns = [
        "proj:*",
        "feat:*", 
        "back:*",
        "res:*",
        "dash:*",
        "rep:*",
        "lookup:*",
        "session:*",
        "api:*",
        "ai:*",
        "fast:*"
    ]
    
    total_cleared = 0
    for pattern in patterns:
        cleared = await cache_manager.cache.clear_pattern(pattern)
        total_cleared += cleared
    
    logger.info(f"✅ Cleared {total_cleared} cache entries")
    return total_cleared

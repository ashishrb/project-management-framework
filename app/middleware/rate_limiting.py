"""
Rate Limiting Middleware for GenAI Metrics Dashboard
Implements Redis-based rate limiting with different limits for different endpoints
"""
import time
import json
import hashlib
from typing import Dict, Optional
from fastapi import Request, HTTPException, status
from fastapi.responses import JSONResponse
import redis
import logging

from app.config import settings

logger = logging.getLogger(__name__)

class RateLimiter:
    """Redis-based rate limiter with configurable limits"""
    
    def __init__(self):
        self.redis_client = None
        self.rate_limits = {
            # General API limits
            "default": {"requests": 100, "window": 60},  # 100 requests per minute
            "auth": {"requests": 10, "window": 60},      # 10 auth attempts per minute
            "api": {"requests": 200, "window": 60},     # 200 API calls per minute
            "upload": {"requests": 20, "window": 60},    # 20 uploads per minute
            "export": {"requests": 10, "window": 60},    # 10 exports per minute
            "ai": {"requests": 50, "window": 60},        # 50 AI requests per minute
        }
        
    async def initialize(self):
        """Initialize Redis connection"""
        try:
            self.redis_client = redis.from_url(
                settings.REDIS_URL,
                decode_responses=True,
                socket_connect_timeout=5,
                socket_timeout=5,
                retry_on_timeout=True
            )
            # Test connection
            await self.redis_client.ping()
            logger.info("✅ Rate limiter Redis connection established")
        except Exception as e:
            logger.error(f"❌ Failed to connect to Redis for rate limiting: {e}")
            self.redis_client = None
    
    def get_client_ip(self, request: Request) -> str:
        """Extract client IP address"""
        # Check for forwarded IP first (for load balancers/proxies)
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()
        
        # Check for real IP header
        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip
        
        # Fallback to direct client IP
        return request.client.host if request.client else "unknown"
    
    def get_rate_limit_key(self, request: Request, limit_type: str = "default") -> str:
        """Generate rate limit key"""
        client_ip = self.get_client_ip(request)
        user_id = getattr(request.state, 'user_id', 'anonymous')
        
        # Create a hash of the key components
        key_data = f"{client_ip}:{user_id}:{limit_type}"
        key_hash = hashlib.md5(key_data.encode()).hexdigest()
        
        return f"rate_limit:{key_hash}"
    
    def get_limit_type(self, request: Request) -> str:
        """Determine rate limit type based on request path"""
        path = request.url.path
        
        if "/auth" in path or "/login" in path:
            return "auth"
        elif "/upload" in path:
            return "upload"
        elif "/export" in path:
            return "export"
        elif "/ai" in path or "/chat" in path:
            return "ai"
        elif path.startswith("/api/"):
            return "api"
        else:
            return "default"
    
    async def check_rate_limit(self, request: Request) -> Dict:
        """Check if request exceeds rate limit"""
        if not self.redis_client:
            # If Redis is not available, allow request but log warning
            logger.warning("Rate limiter Redis not available, allowing request")
            return {"allowed": True, "remaining": 999, "reset_time": 0}
        
        try:
            limit_type = self.get_limit_type(request)
            limits = self.rate_limits.get(limit_type, self.rate_limits["default"])
            
            key = self.get_rate_limit_key(request, limit_type)
            current_time = int(time.time())
            window_start = current_time - limits["window"]
            
            # Use Redis pipeline for atomic operations
            pipe = self.redis_client.pipeline()
            
            # Remove old entries
            pipe.zremrangebyscore(key, 0, window_start)
            
            # Count current requests
            pipe.zcard(key)
            
            # Add current request
            pipe.zadd(key, {str(current_time): current_time})
            
            # Set expiration
            pipe.expire(key, limits["window"])
            
            # Execute pipeline
            results = await pipe.execute()
            
            current_requests = results[1]
            
            if current_requests >= limits["requests"]:
                # Rate limit exceeded
                reset_time = current_time + limits["window"]
                
                logger.warning(f"Rate limit exceeded for {limit_type}: {current_requests}/{limits['requests']}")
                
                return {
                    "allowed": False,
                    "remaining": 0,
                    "reset_time": reset_time,
                    "limit": limits["requests"],
                    "window": limits["window"]
                }
            else:
                # Request allowed
                remaining = limits["requests"] - current_requests - 1
                reset_time = current_time + limits["window"]
                
                return {
                    "allowed": True,
                    "remaining": remaining,
                    "reset_time": reset_time,
                    "limit": limits["requests"],
                    "window": limits["window"]
                }
                
        except Exception as e:
            logger.error(f"Rate limiting error: {e}")
            # On error, allow request but log the issue
            return {"allowed": True, "remaining": 999, "reset_time": 0}
    
    def create_rate_limit_response(self, rate_limit_info: Dict) -> JSONResponse:
        """Create rate limit exceeded response"""
        return JSONResponse(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            content={
                "error": "Rate limit exceeded",
                "message": f"Too many requests. Limit: {rate_limit_info['limit']} per {rate_limit_info['window']} seconds",
                "remaining": rate_limit_info["remaining"],
                "reset_time": rate_limit_info["reset_time"],
                "retry_after": rate_limit_info["reset_time"] - int(time.time())
            },
            headers={
                "X-RateLimit-Limit": str(rate_limit_info["limit"]),
                "X-RateLimit-Remaining": str(rate_limit_info["remaining"]),
                "X-RateLimit-Reset": str(rate_limit_info["reset_time"]),
                "Retry-After": str(rate_limit_info["reset_time"] - int(time.time()))
            }
        )

# Global rate limiter instance
rate_limiter = RateLimiter()

async def rate_limit_middleware(request: Request, call_next):
    """Rate limiting middleware function"""
    # Check rate limit
    rate_limit_info = await rate_limiter.check_rate_limit(request)
    
    if not rate_limit_info["allowed"]:
        return rate_limiter.create_rate_limit_response(rate_limit_info)
    
    # Add rate limit headers to response
    response = await call_next(request)
    
    # Add rate limit headers
    response.headers["X-RateLimit-Limit"] = str(rate_limit_info["limit"])
    response.headers["X-RateLimit-Remaining"] = str(rate_limit_info["remaining"])
    response.headers["X-RateLimit-Reset"] = str(rate_limit_info["reset_time"])
    
    return response

# Rate limit decorator for specific endpoints
def rate_limit(limit_type: str = "default"):
    """Decorator to apply rate limiting to specific endpoints"""
    def decorator(func):
        async def wrapper(*args, **kwargs):
            # Extract request from args/kwargs
            request = None
            for arg in args:
                if isinstance(arg, Request):
                    request = arg
                    break
            
            if not request:
                # If no request found, call function normally
                return await func(*args, **kwargs)
            
            # Check rate limit
            rate_limit_info = await rate_limiter.check_rate_limit(request)
            
            if not rate_limit_info["allowed"]:
                return rate_limiter.create_rate_limit_response(rate_limit_info)
            
            # Call the original function
            response = await func(*args, **kwargs)
            
            # Add rate limit headers if response is a Response object
            if hasattr(response, 'headers'):
                response.headers["X-RateLimit-Limit"] = str(rate_limit_info["limit"])
                response.headers["X-RateLimit-Remaining"] = str(rate_limit_info["remaining"])
                response.headers["X-RateLimit-Reset"] = str(rate_limit_info["reset_time"])
            
            return response
        
        return wrapper
    return decorator

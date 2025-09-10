"""
CSRF Protection Middleware for GenAI Metrics Dashboard
Implements CSRF token generation, validation, and protection
"""
import secrets
import hashlib
import hmac
import time
from typing import Optional, Dict
from fastapi import Request, HTTPException, status
from fastapi.responses import JSONResponse
import logging

from app.config import settings

logger = logging.getLogger(__name__)

class CSRFProtection:
    """CSRF protection implementation"""
    
    def __init__(self):
        self.secret_key = settings.SECRET_KEY.encode('utf-8')
        self.token_length = 32
        self.token_expiry = 3600  # 1 hour
    
    def generate_token(self, session_id: str = None) -> str:
        """Generate a new CSRF token"""
        # Generate random token
        random_part = secrets.token_urlsafe(self.token_length)
        
        # Create timestamp
        timestamp = str(int(time.time()))
        
        # Create token data
        token_data = f"{random_part}:{timestamp}:{session_id or 'default'}"
        
        # Create HMAC signature
        signature = hmac.new(
            self.secret_key,
            token_data.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
        
        # Combine token data and signature
        token = f"{token_data}:{signature}"
        
        logger.debug(f"Generated CSRF token for session: {session_id}")
        return token
    
    def validate_token(self, token: str, session_id: str = None) -> bool:
        """Validate a CSRF token"""
        try:
            if not token:
                return False
            
            # Split token into parts
            parts = token.split(':')
            if len(parts) != 4:  # random:timestamp:session:signature
                return False
            
            random_part, timestamp, token_session_id, signature = parts
            
            # Check session ID match
            if session_id and token_session_id != session_id:
                logger.warning(f"CSRF token session mismatch: {token_session_id} != {session_id}")
                return False
            
            # Check token age
            try:
                token_time = int(timestamp)
                current_time = int(time.time())
                if current_time - token_time > self.token_expiry:
                    logger.warning(f"CSRF token expired: {current_time - token_time}s old")
                    return False
            except ValueError:
                logger.warning("Invalid timestamp in CSRF token")
                return False
            
            # Recreate token data
            token_data = f"{random_part}:{timestamp}:{token_session_id}"
            
            # Verify signature
            expected_signature = hmac.new(
                self.secret_key,
                token_data.encode('utf-8'),
                hashlib.sha256
            ).hexdigest()
            
            if not hmac.compare_digest(signature, expected_signature):
                logger.warning("CSRF token signature validation failed")
                return False
            
            logger.debug(f"CSRF token validated successfully for session: {session_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error validating CSRF token: {e}")
            return False
    
    def get_token_from_request(self, request: Request) -> Optional[str]:
        """Extract CSRF token from request"""
        # Check header first (preferred for AJAX requests)
        token = request.headers.get("X-CSRF-Token")
        if token:
            return token
        
        # Check form data
        if hasattr(request, '_form') and request._form:
            token = request._form.get("csrf_token")
            if token:
                return token
        
        # Check JSON body
        if hasattr(request, '_json') and request._json:
            token = request._json.get("csrf_token")
            if token:
                return token
        
        return None
    
    def get_session_id(self, request: Request) -> str:
        """Get session ID from request"""
        # Try to get from session cookie
        session_cookie = request.cookies.get("session_id")
        if session_cookie:
            return session_cookie
        
        # Try to get from user state
        if hasattr(request.state, 'user_id'):
            return str(request.state.user_id)
        
        # Fallback to client IP
        client_ip = request.client.host if request.client else "unknown"
        return f"ip_{client_ip}"
    
    def is_safe_method(self, method: str) -> bool:
        """Check if HTTP method is safe (doesn't require CSRF protection)"""
        safe_methods = {"GET", "HEAD", "OPTIONS", "TRACE"}
        return method.upper() in safe_methods
    
    def should_skip_csrf(self, request: Request) -> bool:
        """Check if CSRF protection should be skipped for this request"""
        path = request.url.path
        
        # Skip for safe methods
        if self.is_safe_method(request.method):
            return True
        
        # Skip for API endpoints that use proper authentication
        if path.startswith("/api/v1/auth/"):
            return True
        
        # Skip for health checks
        if path in ["/health", "/status"]:
            return True
        
        # Skip for static files
        if path.startswith("/static/"):
            return True
        
        # Skip for WebSocket connections
        if path.startswith("/ws/"):
            return True
        
        # Skip for frontend logging endpoints (internal logging)
        if path in ["/api/v1/logs/frontend", "/api/v1/logs/frontend/test"]:
            return True
        
        return False

# Global CSRF protection instance
csrf_protection = CSRFProtection()

async def csrf_middleware(request: Request, call_next):
    """CSRF protection middleware function"""
    # Skip CSRF check for certain requests
    if csrf_protection.should_skip_csrf(request):
        response = await call_next(request)
        return response
    
    # Get CSRF token from request
    token = csrf_protection.get_token_from_request(request)
    session_id = csrf_protection.get_session_id(request)
    
    # Validate token
    if not token or not csrf_protection.validate_token(token, session_id):
        logger.warning(f"CSRF validation failed for {request.method} {request.url.path}")
        
        return JSONResponse(
            status_code=status.HTTP_403_FORBIDDEN,
            content={
                "error": "CSRF token validation failed",
                "message": "Invalid or missing CSRF token",
                "code": "CSRF_TOKEN_INVALID"
            }
        )
    
    # Token is valid, proceed with request
    response = await call_next(request)
    
    # Add CSRF token to response headers for subsequent requests
    if request.method == "GET":
        new_token = csrf_protection.generate_token(session_id)
        response.headers["X-CSRF-Token"] = new_token
    
    return response

# CSRF token endpoint
def get_csrf_token(request: Request) -> Dict[str, str]:
    """Endpoint to get CSRF token"""
    session_id = csrf_protection.get_session_id(request)
    token = csrf_protection.generate_token(session_id)
    
    return {
        "csrf_token": token,
        "expires_in": csrf_protection.token_expiry
    }

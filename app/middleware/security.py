"""
Security Headers Middleware for GenAI Metrics Dashboard
Implements comprehensive security headers for production deployment
"""
from fastapi import Request
from fastapi.responses import Response
import logging

logger = logging.getLogger(__name__)

class SecurityHeadersMiddleware:
    """Middleware to add security headers to all responses"""
    
    def __init__(self):
        self.security_headers = {
            # Prevent clickjacking attacks
            "X-Frame-Options": "DENY",
            
            # Prevent MIME type sniffing
            "X-Content-Type-Options": "nosniff",
            
            # Enable XSS protection
            "X-XSS-Protection": "1; mode=block",
            
            # Force HTTPS (adjust max-age as needed)
            "Strict-Transport-Security": "max-age=31536000; includeSubDomains; preload",
            
            # Control referrer information
            "Referrer-Policy": "strict-origin-when-cross-origin",
            
            # Prevent DNS prefetching
            "X-DNS-Prefetch-Control": "off",
            
            # Disable IE compatibility mode
            "X-UA-Compatible": "IE=edge",
            
            # Permissions Policy (formerly Feature Policy)
            "Permissions-Policy": (
                "geolocation=(), "
                "microphone=(), "
                "camera=(), "
                "payment=(), "
                "usb=(), "
                "magnetometer=(), "
                "gyroscope=(), "
                "speaker=(), "
                "vibrate=(), "
                "fullscreen=(self), "
                "sync-xhr=()"
            ),
            
            # Cross-Origin policies
            "Cross-Origin-Embedder-Policy": "require-corp",
            "Cross-Origin-Opener-Policy": "same-origin",
            "Cross-Origin-Resource-Policy": "same-origin",
            
            # Cache control for sensitive endpoints
            "Cache-Control": "no-store, no-cache, must-revalidate, proxy-revalidate",
            "Pragma": "no-cache",
            "Expires": "0"
        }
    
    def add_security_headers(self, response: Response, request: Request = None) -> Response:
        """Add security headers to response"""
        try:
            # Add all security headers
            for header, value in self.security_headers.items():
                response.headers[header] = value
            
            # Add Content Security Policy (basic version)
            csp_policy = self._get_csp_policy(request)
            if csp_policy:
                response.headers["Content-Security-Policy"] = csp_policy
            
            # Add additional headers based on request
            if request:
                self._add_request_specific_headers(response, request)
            
            logger.debug("Security headers added to response")
            
        except Exception as e:
            logger.error(f"Error adding security headers: {e}")
        
        return response
    
    def _get_csp_policy(self, request: Request = None) -> str:
        """Generate Content Security Policy"""
        # Basic CSP policy - can be enhanced based on requirements
        csp_directives = [
            "default-src 'self'",
            "script-src 'self' 'unsafe-inline' 'unsafe-eval' https://cdn.jsdelivr.net https://cdnjs.cloudflare.com",
            "style-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net https://cdnjs.cloudflare.com https://fonts.googleapis.com",
            "font-src 'self' https://fonts.gstatic.com https://cdn.jsdelivr.net",
            "img-src 'self' data: https:",
            "connect-src 'self' ws: wss: https://cdn.jsdelivr.net https://cdnjs.cloudflare.com",
            "media-src 'self'",
            "object-src 'none'",
            "base-uri 'self'",
            "form-action 'self'",
            "frame-ancestors 'none'",
            "upgrade-insecure-requests"
        ]
        
        return "; ".join(csp_directives)
    
    def _add_request_specific_headers(self, response: Response, request: Request):
        """Add headers specific to the request type"""
        path = request.url.path
        
        # API endpoints get additional security
        if path.startswith("/api/"):
            response.headers["X-API-Version"] = "v1"
            response.headers["X-Content-Type-Options"] = "nosniff"
        
        # Static files get different cache control
        if path.startswith("/static/"):
            response.headers["Cache-Control"] = "public, max-age=31536000, immutable"
            # Remove Pragma and Expires headers if they exist
            if "Pragma" in response.headers:
                del response.headers["Pragma"]
            if "Expires" in response.headers:
                del response.headers["Expires"]
        
        # Admin endpoints get stricter headers
        if "/admin" in path:
            response.headers["X-Frame-Options"] = "DENY"
            response.headers["X-Content-Type-Options"] = "nosniff"

# Global security headers instance
security_headers = SecurityHeadersMiddleware()

async def security_headers_middleware(request: Request, call_next):
    """Security headers middleware function"""
    response = await call_next(request)
    
    # Add security headers to response
    security_headers.add_security_headers(response, request)
    
    return response

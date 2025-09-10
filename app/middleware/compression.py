"""
Compression Middleware for GenAI Metrics Dashboard
Implements gzip compression for better performance
"""
import gzip
import json
from typing import Optional
from fastapi import Request
from fastapi.responses import Response
import logging

logger = logging.getLogger(__name__)

class CompressionMiddleware:
    """Gzip compression middleware"""
    
    def __init__(self):
        self.min_size = 1024  # Minimum size to compress (1KB)
        self.compression_level = 6  # Compression level (1-9)
        self.content_types = {
            "application/json",
            "application/javascript",
            "application/xml",
            "text/css",
            "text/html",
            "text/javascript",
            "text/plain",
            "text/xml",
            "text/csv",
            "application/xml",
            "application/rss+xml",
            "application/atom+xml",
            "image/svg+xml"
        }
    
    def should_compress(self, request: Request, response: Response) -> bool:
        """Determine if response should be compressed"""
        # Check if client accepts gzip
        accept_encoding = request.headers.get("accept-encoding", "")
        if "gzip" not in accept_encoding:
            return False
        
        # Check content type
        content_type = response.headers.get("content-type", "")
        if not any(ct in content_type for ct in self.content_types):
            return False
        
        # Check if already compressed
        if response.headers.get("content-encoding"):
            return False
        
        # Check content length
        content_length = response.headers.get("content-length")
        if content_length and int(content_length) < self.min_size:
            return False
        
        return True
    
    def compress_response(self, response: Response) -> Response:
        """Compress response content"""
        try:
            # Get response body
            body = response.body
            
            # Skip if body is too small
            if len(body) < self.min_size:
                return response
            
            # Compress the body
            compressed_body = gzip.compress(body, compresslevel=self.compression_level)
            
            # Only use compression if it actually reduces size
            if len(compressed_body) >= len(body):
                return response
            
            # Update response
            response.body = compressed_body
            response.headers["content-encoding"] = "gzip"
            response.headers["content-length"] = str(len(compressed_body))
            
            # Add Vary header to indicate compression varies
            vary = response.headers.get("vary", "")
            if "Accept-Encoding" not in vary:
                response.headers["vary"] = f"{vary}, Accept-Encoding".strip(", ")
            
            logger.debug(f"Compressed response: {len(body)} -> {len(compressed_body)} bytes")
            
        except Exception as e:
            logger.error(f"Error compressing response: {e}")
        
        return response

# Global compression middleware instance
compression_middleware = CompressionMiddleware()

async def compression_middleware_func(request: Request, call_next):
    """Compression middleware function"""
    response = await call_next(request)
    
    # Apply compression if appropriate
    if compression_middleware.should_compress(request, response):
        response = compression_middleware.compress_response(response)
    
    return response

"""
Enhanced Input Validation Middleware for GenAI Metrics Dashboard
Implements comprehensive input sanitization and validation
"""
import re
import html
import json
from typing import Any, Dict, List, Optional, Union
from fastapi import Request, HTTPException, status
from fastapi.responses import JSONResponse
import logging

logger = logging.getLogger(__name__)

class InputValidator:
    """Enhanced input validation and sanitization"""
    
    def __init__(self):
        # SQL injection patterns
        self.sql_patterns = [
            r"(\b(SELECT|INSERT|UPDATE|DELETE|DROP|CREATE|ALTER|EXEC|UNION|SCRIPT)\b)",
            r"(\b(OR|AND)\s+\d+\s*=\s*\d+)",
            r"(\b(OR|AND)\s+'.*'\s*=\s*'.*')",
            r"(--|\#|\/\*|\*\/)",
            r"(\b(WAITFOR|DELAY)\b)",
            r"(\b(CHAR|ASCII|SUBSTRING|LEN)\b)",
        ]
        
        # XSS patterns
        self.xss_patterns = [
            r"<script[^>]*>.*?</script>",
            r"javascript:",
            r"on\w+\s*=",
            r"<iframe[^>]*>",
            r"<object[^>]*>",
            r"<embed[^>]*>",
            r"<link[^>]*>",
            r"<meta[^>]*>",
            r"<style[^>]*>",
            r"expression\s*\(",
            r"url\s*\(",
            r"@import",
        ]
        
        # Path traversal patterns
        self.path_traversal_patterns = [
            r"\.\./",
            r"\.\.\\",
            r"\.\.%2f",
            r"\.\.%5c",
            r"%2e%2e%2f",
            r"%2e%2e%5c",
        ]
        
        # Command injection patterns
        self.command_patterns = [
            r"[;&|`$]",
            r"\b(cat|ls|pwd|whoami|id|uname|ps|netstat|ifconfig)\b",
            r"\b(wget|curl|nc|telnet|ssh|ftp)\b",
            r"\b(rm|mv|cp|chmod|chown)\b",
        ]
    
    def sanitize_string(self, value: str, max_length: int = 1000) -> str:
        """Sanitize string input"""
        if not isinstance(value, str):
            return str(value)
        
        # Limit length
        if len(value) > max_length:
            value = value[:max_length]
            logger.warning(f"String truncated to {max_length} characters")
        
        # HTML escape
        value = html.escape(value, quote=True)
        
        # Remove null bytes
        value = value.replace('\x00', '')
        
        # Normalize whitespace
        value = re.sub(r'\s+', ' ', value).strip()
        
        return value
    
    def validate_email(self, email: str) -> bool:
        """Validate email format"""
        if not email or not isinstance(email, str):
            return False
        
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(email_pattern, email))
    
    def validate_url(self, url: str) -> bool:
        """Validate URL format"""
        if not url or not isinstance(url, str):
            return False
        
        url_pattern = r'^https?://[^\s/$.?#].[^\s]*$'
        return bool(re.match(url_pattern, url))
    
    def validate_phone(self, phone: str) -> bool:
        """Validate phone number format"""
        if not phone or not isinstance(phone, str):
            return False
        
        # Remove all non-digit characters
        digits = re.sub(r'\D', '', phone)
        
        # Check if it's a valid length (7-15 digits)
        return 7 <= len(digits) <= 15
    
    def validate_date(self, date_str: str) -> bool:
        """Validate date format (YYYY-MM-DD)"""
        if not date_str or not isinstance(date_str, str):
            return False
        
        date_pattern = r'^\d{4}-\d{2}-\d{2}$'
        if not re.match(date_pattern, date_str):
            return False
        
        try:
            from datetime import datetime
            datetime.strptime(date_str, '%Y-%m-%d')
            return True
        except ValueError:
            return False
    
    def validate_integer(self, value: Any, min_val: int = None, max_val: int = None) -> bool:
        """Validate integer value"""
        try:
            int_val = int(value)
            if min_val is not None and int_val < min_val:
                return False
            if max_val is not None and int_val > max_val:
                return False
            return True
        except (ValueError, TypeError):
            return False
    
    def validate_float(self, value: Any, min_val: float = None, max_val: float = None) -> bool:
        """Validate float value"""
        try:
            float_val = float(value)
            if min_val is not None and float_val < min_val:
                return False
            if max_val is not None and float_val > max_val:
                return False
            return True
        except (ValueError, TypeError):
            return False
    
    def check_sql_injection(self, value: str) -> bool:
        """Check for SQL injection patterns"""
        if not isinstance(value, str):
            return False
        
        value_upper = value.upper()
        for pattern in self.sql_patterns:
            if re.search(pattern, value_upper, re.IGNORECASE):
                logger.warning(f"Potential SQL injection detected: {pattern}")
                return True
        
        return False
    
    def check_xss(self, value: str) -> bool:
        """Check for XSS patterns"""
        if not isinstance(value, str):
            return False
        
        for pattern in self.xss_patterns:
            if re.search(pattern, value, re.IGNORECASE):
                logger.warning(f"Potential XSS detected: {pattern}")
                return True
        
        return False
    
    def check_path_traversal(self, value: str) -> bool:
        """Check for path traversal patterns"""
        if not isinstance(value, str):
            return False
        
        for pattern in self.path_traversal_patterns:
            if re.search(pattern, value, re.IGNORECASE):
                logger.warning(f"Potential path traversal detected: {pattern}")
                return True
        
        return False
    
    def check_command_injection(self, value: str) -> bool:
        """Check for command injection patterns"""
        if not isinstance(value, str):
            return False
        
        for pattern in self.command_patterns:
            if re.search(pattern, value, re.IGNORECASE):
                logger.warning(f"Potential command injection detected: {pattern}")
                return True
        
        return False
    
    def validate_and_sanitize_input(self, data: Any, field_name: str = None) -> Any:
        """Validate and sanitize input data recursively"""
        if isinstance(data, str):
            # Check for malicious patterns
            if self.check_sql_injection(data):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Invalid input detected in field: {field_name or 'unknown'}"
                )
            
            if self.check_xss(data):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Invalid input detected in field: {field_name or 'unknown'}"
                )
            
            if self.check_path_traversal(data):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Invalid input detected in field: {field_name or 'unknown'}"
                )
            
            if self.check_command_injection(data):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Invalid input detected in field: {field_name or 'unknown'}"
                )
            
            # Sanitize the string
            return self.sanitize_string(data)
        
        elif isinstance(data, dict):
            # Recursively validate dictionary
            sanitized_dict = {}
            for key, value in data.items():
                sanitized_key = self.sanitize_string(str(key), max_length=100)
                sanitized_value = self.validate_and_sanitize_input(value, f"{field_name}.{key}" if field_name else key)
                sanitized_dict[sanitized_key] = sanitized_value
            return sanitized_dict
        
        elif isinstance(data, list):
            # Recursively validate list
            sanitized_list = []
            for i, item in enumerate(data):
                sanitized_item = self.validate_and_sanitize_input(item, f"{field_name}[{i}]" if field_name else f"item_{i}")
                sanitized_list.append(sanitized_item)
            return sanitized_list
        
        elif isinstance(data, (int, float, bool)):
            # These types are generally safe
            return data
        
        else:
            # Convert to string and sanitize
            return self.sanitize_string(str(data))
    
    def validate_file_upload(self, filename: str, content_type: str, file_size: int) -> bool:
        """Validate file upload parameters"""
        # Check filename
        if not filename or len(filename) > 255:
            return False
        
        # Check for path traversal in filename
        if self.check_path_traversal(filename):
            return False
        
        # Check file extension
        allowed_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.pdf', '.doc', '.docx', '.txt', '.csv', '.xlsx'}
        file_ext = '.' + filename.split('.')[-1].lower() if '.' in filename else ''
        if file_ext not in allowed_extensions:
            logger.warning(f"Disallowed file extension: {file_ext}")
            return False
        
        # Check content type
        allowed_types = {
            'image/jpeg', 'image/png', 'image/gif',
            'application/pdf', 'application/msword',
            'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            'text/plain', 'text/csv',
            'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        }
        if content_type not in allowed_types:
            logger.warning(f"Disallowed content type: {content_type}")
            return False
        
        # Check file size (10MB limit)
        max_size = 10 * 1024 * 1024  # 10MB
        if file_size > max_size:
            logger.warning(f"File too large: {file_size} bytes")
            return False
        
        return True

# Global input validator instance
input_validator = InputValidator()

async def input_validation_middleware(request: Request, call_next):
    """Input validation middleware function"""
    try:
        # Skip validation for certain endpoints
        if request.url.path in ["/health", "/status", "/docs", "/redoc", "/openapi.json"]:
            response = await call_next(request)
            return response
        
        # Validate query parameters
        if request.query_params:
            for key, value in request.query_params.items():
                try:
                    input_validator.validate_and_sanitize_input(value, f"query.{key}")
                except HTTPException as e:
                    logger.warning(f"Query parameter validation failed: {key}={value}")
                    return JSONResponse(
                        status_code=e.status_code,
                        content={"error": "Invalid query parameter", "detail": e.detail}
                    )
        
        # Validate form data
        if request.method in ["POST", "PUT", "PATCH"]:
            content_type = request.headers.get("content-type", "")
            
            if "application/json" in content_type:
                # Validate JSON body
                try:
                    body = await request.json()
                    validated_body = input_validator.validate_and_sanitize_input(body, "request_body")
                    
                    # Replace request body with validated data
                    request._json = validated_body
                except json.JSONDecodeError:
                    logger.warning("Invalid JSON in request body")
                    return JSONResponse(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        content={"error": "Invalid JSON format"}
                    )
                except HTTPException as e:
                    logger.warning(f"Request body validation failed: {e.detail}")
                    return JSONResponse(
                        status_code=e.status_code,
                        content={"error": "Invalid request data", "detail": e.detail}
                    )
            
            elif "multipart/form-data" in content_type:
                # Validate form data
                try:
                    form_data = await request.form()
                    for key, value in form_data.items():
                        input_validator.validate_and_sanitize_input(value, f"form.{key}")
                except HTTPException as e:
                    logger.warning(f"Form data validation failed: {e.detail}")
                    return JSONResponse(
                        status_code=e.status_code,
                        content={"error": "Invalid form data", "detail": e.detail}
                    )
        
        # Process request
        response = await call_next(request)
        return response
        
    except Exception as e:
        logger.error(f"Input validation middleware error: {e}")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"error": "Internal server error"}
        )

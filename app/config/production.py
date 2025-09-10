"""
Production Configuration for GenAI Metrics Dashboard
Contains production-specific settings and security configurations
"""
import os
from typing import List

class ProductionSettings:
    """Production-specific settings"""
    
    # Security Settings
    SECRET_KEY: str = os.getenv("SECRET_KEY", "CHANGE_THIS_IN_PRODUCTION")
    DEBUG: bool = False
    
    # Database Settings
    DATABASE_URL: str = os.getenv("DATABASE_URL", "postgresql://user:password@localhost:5432/genai_metrics_db")
    DB_POOL_SIZE: int = int(os.getenv("DB_POOL_SIZE", "20"))
    DB_MAX_OVERFLOW: int = int(os.getenv("DB_MAX_OVERFLOW", "30"))
    DB_POOL_TIMEOUT: int = int(os.getenv("DB_POOL_TIMEOUT", "30"))
    DB_POOL_RECYCLE: int = int(os.getenv("DB_POOL_RECYCLE", "3600"))
    
    # Redis Settings
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379")
    
    # CORS Settings - Restrict in production
    BACKEND_CORS_ORIGINS: List[str] = [
        origin.strip() for origin in os.getenv("BACKEND_CORS_ORIGINS", "").split(",")
        if origin.strip()
    ]
    
    # Rate Limiting Settings
    RATE_LIMIT_ENABLED: bool = True
    RATE_LIMIT_REDIS_URL: str = os.getenv("RATE_LIMIT_REDIS_URL", REDIS_URL)
    
    # Security Headers
    SECURITY_HEADERS_ENABLED: bool = True
    CSP_ENABLED: bool = True
    HSTS_MAX_AGE: int = int(os.getenv("HSTS_MAX_AGE", "31536000"))  # 1 year
    
    # CSRF Protection
    CSRF_ENABLED: bool = True
    CSRF_TOKEN_EXPIRY: int = int(os.getenv("CSRF_TOKEN_EXPIRY", "3600"))  # 1 hour
    
    # Input Validation
    INPUT_VALIDATION_ENABLED: bool = True
    MAX_REQUEST_SIZE: int = int(os.getenv("MAX_REQUEST_SIZE", "10485760"))  # 10MB
    
    # Compression
    COMPRESSION_ENABLED: bool = True
    COMPRESSION_MIN_SIZE: int = int(os.getenv("COMPRESSION_MIN_SIZE", "1024"))  # 1KB
    
    # Logging
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    LOG_FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    # Monitoring
    MONITORING_ENABLED: bool = True
    ERROR_TRACKING_ENABLED: bool = True
    PERFORMANCE_MONITORING_ENABLED: bool = True
    
    # File Upload Settings
    MAX_FILE_SIZE: int = int(os.getenv("MAX_FILE_SIZE", "10485760"))  # 10MB
    ALLOWED_FILE_TYPES: List[str] = [
        "image/jpeg", "image/png", "image/gif",
        "application/pdf", "text/plain", "text/csv",
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    ]
    
    # Session Settings
    SESSION_COOKIE_SECURE: bool = True
    SESSION_COOKIE_HTTPONLY: bool = True
    SESSION_COOKIE_SAMESITE: str = "strict"
    
    # API Settings
    API_RATE_LIMIT_PER_MINUTE: int = int(os.getenv("API_RATE_LIMIT_PER_MINUTE", "200"))
    API_RATE_LIMIT_BURST: int = int(os.getenv("API_RATE_LIMIT_BURST", "50"))
    
    # External Services
    OLLAMA_BASE_URL: str = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    CHROMA_PERSIST_DIRECTORY: str = os.getenv("CHROMA_PERSIST_DIRECTORY", "./chroma_db")
    
    # Performance Settings
    CACHE_TTL: int = int(os.getenv("CACHE_TTL", "300"))  # 5 minutes
    MAX_CONCURRENT_REQUESTS: int = int(os.getenv("MAX_CONCURRENT_REQUESTS", "100"))
    
    # Backup Settings
    BACKUP_ENABLED: bool = os.getenv("BACKUP_ENABLED", "false").lower() == "true"
    BACKUP_SCHEDULE: str = os.getenv("BACKUP_SCHEDULE", "0 2 * * *")  # Daily at 2 AM
    BACKUP_RETENTION_DAYS: int = int(os.getenv("BACKUP_RETENTION_DAYS", "30"))
    
    @classmethod
    def validate_config(cls):
        """Validate production configuration"""
        errors = []
        
        if cls.SECRET_KEY == "CHANGE_THIS_IN_PRODUCTION":
            errors.append("SECRET_KEY must be changed from default value")
        
        if not cls.BACKEND_CORS_ORIGINS:
            errors.append("BACKEND_CORS_ORIGINS must be configured for production")
        
        if cls.DEBUG:
            errors.append("DEBUG should be False in production")
        
        if errors:
            raise ValueError(f"Production configuration errors: {', '.join(errors)}")
        
        return True

# Environment-specific configuration
def get_settings():
    """Get settings based on environment"""
    env = os.getenv("ENVIRONMENT", "development")
    
    if env == "production":
        return ProductionSettings()
    else:
        # Import development settings
        from app.config import Settings
        return Settings()

# Validate production settings on import
if os.getenv("ENVIRONMENT") == "production":
    try:
        ProductionSettings.validate_config()
    except ValueError as e:
        print(f"Configuration Error: {e}")
        raise

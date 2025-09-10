"""
Database configuration and connection management for GenAI Metrics Dashboard
Optimized for performance with connection pooling and monitoring
"""
from sqlalchemy import create_engine, event
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import QueuePool
import os
import logging
from contextlib import asynccontextmanager
from typing import Generator

logger = logging.getLogger(__name__)

# Database URL - can be overridden with environment variable
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:password@localhost:5432/genai_metrics_db")

# Optimized database configuration
DATABASE_CONFIG = {
    "pool_size": int(os.getenv("DB_POOL_SIZE", "20")),
    "max_overflow": int(os.getenv("DB_MAX_OVERFLOW", "30")),
    "pool_timeout": int(os.getenv("DB_POOL_TIMEOUT", "30")),
    "pool_recycle": int(os.getenv("DB_POOL_RECYCLE", "3600")),
    "pool_pre_ping": os.getenv("DB_POOL_PRE_PING", "true").lower() == "true",
    "echo": os.getenv("DB_ECHO", "false").lower() == "true",
    "echo_pool": os.getenv("DB_ECHO_POOL", "false").lower() == "true"
}

# Create SQLAlchemy engine with optimized settings
engine = create_engine(
    DATABASE_URL,
    poolclass=QueuePool,
    pool_size=DATABASE_CONFIG["pool_size"],
    max_overflow=DATABASE_CONFIG["max_overflow"],
    pool_timeout=DATABASE_CONFIG["pool_timeout"],
    pool_recycle=DATABASE_CONFIG["pool_recycle"],
    pool_pre_ping=DATABASE_CONFIG["pool_pre_ping"],
    echo=DATABASE_CONFIG["echo"],
    echo_pool=DATABASE_CONFIG["echo_pool"]
)

# Create SessionLocal class with optimized settings
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
    expire_on_commit=False  # Prevent lazy loading issues
)

# Create Base class for models
Base = declarative_base()

# Database connection monitoring
@event.listens_for(engine, "connect")
def receive_connect(dbapi_connection, connection_record):
    """Monitor database connections"""
    logger.debug("🔌 New database connection established")

@event.listens_for(engine, "checkout")
def receive_checkout(dbapi_connection, connection_record, connection_proxy):
    """Monitor connection checkout"""
    logger.debug("📤 Database connection checked out")

@event.listens_for(engine, "checkin")
def receive_checkin(dbapi_connection, connection_record):
    """Monitor connection checkin"""
    logger.debug("📥 Database connection checked in")

@event.listens_for(engine, "invalidate")
def receive_invalidate(dbapi_connection, connection_record, exception):
    """Monitor connection invalidation"""
    logger.warning(f"⚠️ Database connection invalidated: {exception}")

# Dependency to get database session
def get_db() -> Generator:
    """Get database session with proper error handling"""
    db = SessionLocal()
    try:
        yield db
    except Exception as e:
        logger.error(f"Database session error: {e}")
        db.rollback()
        raise
    finally:
        db.close()

# Async context manager for database sessions
@asynccontextmanager
async def get_db_session():
    """Async context manager for database sessions"""
    db = SessionLocal()
    try:
        yield db
        await db.commit()
    except Exception as e:
        logger.error(f"Database session error: {e}")
        await db.rollback()
        raise
    finally:
        await db.close()

# Database health check
def check_database_health() -> dict:
    """Check database connection health"""
    try:
        # Test connection
        with engine.connect() as connection:
            result = connection.execute("SELECT 1").fetchone()
            
        # Get pool status
        pool = engine.pool
        pool_status = {
            "size": pool.size(),
            "checked_in": pool.checkedin(),
            "checked_out": pool.checkedout(),
            "overflow": pool.overflow(),
            "invalid": pool.invalid()
        }
        
        return {
            "status": "healthy",
            "connection_test": "passed",
            "pool_status": pool_status,
            "config": DATABASE_CONFIG
        }
        
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        return {
            "status": "unhealthy",
            "error": str(e),
            "config": DATABASE_CONFIG
        }

# Database performance monitoring
class DatabasePerformanceMonitor:
    """Monitor database performance metrics"""
    
    def __init__(self):
        self.query_count = 0
        self.slow_queries = 0
        self.connection_count = 0
        self.error_count = 0
    
    def log_query(self, execution_time: float, query_type: str = "unknown"):
        """Log database query performance"""
        self.query_count += 1
        
        if execution_time > 1.0:  # Slow query threshold
            self.slow_queries += 1
            logger.warning(f"🐌 Slow query detected: {execution_time:.3f}s ({query_type})")
    
    def log_connection(self):
        """Log database connection"""
        self.connection_count += 1
    
    def log_error(self, error: str):
        """Log database error"""
        self.error_count += 1
        logger.error(f"Database error: {error}")
    
    def get_stats(self) -> dict:
        """Get database performance statistics"""
        return {
            "query_count": self.query_count,
            "slow_queries": self.slow_queries,
            "connection_count": self.connection_count,
            "error_count": self.error_count,
            "slow_query_rate": (self.slow_queries / self.query_count * 100) if self.query_count > 0 else 0
        }

# Global database performance monitor
db_performance_monitor = DatabasePerformanceMonitor()

# Database initialization
def initialize_database():
    """Initialize database with performance optimizations"""
    logger.info("🚀 Initializing database with performance optimizations")
    
    # Test connection
    health = check_database_health()
    if health["status"] == "healthy":
        logger.info("✅ Database connection established successfully")
        logger.info(f"📊 Pool configuration: {DATABASE_CONFIG}")
    else:
        logger.error(f"❌ Database initialization failed: {health.get('error', 'Unknown error')}")
        raise Exception("Database initialization failed")

# Database cleanup
def cleanup_database():
    """Clean up database connections"""
    logger.info("🧹 Cleaning up database connections")
    
    # Dispose of engine
    engine.dispose()
    
    logger.info("✅ Database cleanup completed")

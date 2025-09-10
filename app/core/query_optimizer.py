"""
Database Query Optimization
Provides optimized query methods and N+1 query prevention
"""

from sqlalchemy.orm import joinedload, selectinload, subqueryload
from sqlalchemy import func, and_, or_
from typing import List, Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)


class QueryOptimizer:
    """Database query optimization utilities"""
    
    @staticmethod
    def optimize_project_queries(session):
        """Optimize project-related queries with eager loading"""
        
        # Optimized query for projects with all related data
        def get_projects_with_relations():
            return session.query(Project).options(
                joinedload(Project.status),
                joinedload(Project.priority),
                joinedload(Project.criticality),
                joinedload(Project.features).joinedload(Feature.status),
                joinedload(Project.features).joinedload(Feature.priority),
                joinedload(Project.features).joinedload(Feature.backlogs).joinedload(Backlog.status),
                joinedload(Project.resources),
                joinedload(Project.functions)
            ).filter(Project.is_active == True)
        
        return get_projects_with_relations
    
    @staticmethod
    def optimize_dashboard_queries(session):
        """Optimize dashboard queries with efficient data loading"""
        
        def get_dashboard_data():
            # Single query to get all dashboard data
            return session.query(
                Project.id,
                Project.name,
                Project.status_id,
                Project.priority_id,
                Project.percent_complete,
                Project.due_date,
                func.count(Feature.id).label('feature_count'),
                func.count(Backlog.id).label('backlog_count'),
                func.count(Resource.id).label('resource_count')
            ).outerjoin(Feature, Project.id == Feature.project_id)\
             .outerjoin(Backlog, Feature.id == Backlog.feature_id)\
             .outerjoin(Resource, Project.id == Resource.project_id)\
             .filter(Project.is_active == True)\
             .group_by(Project.id, Project.name, Project.status_id, 
                      Project.priority_id, Project.percent_complete, Project.due_date)\
             .all()
        
        return get_dashboard_data
    
    @staticmethod
    def optimize_feature_queries(session):
        """Optimize feature queries with proper joins"""
        
        def get_features_with_project_data(project_id: int):
            return session.query(Feature).options(
                joinedload(Feature.project),
                joinedload(Feature.status),
                joinedload(Feature.priority),
                selectinload(Feature.backlogs).joinedload(Backlog.status)
            ).filter(Feature.project_id == project_id)
        
        return get_features_with_project_data
    
    @staticmethod
    def optimize_resource_queries(session):
        """Optimize resource queries with efficient filtering"""
        
        def get_resources_with_skills(skills_filter: List[str] = None):
            query = session.query(Resource).options(
                joinedload(Resource.skills)
            ).filter(Resource.is_active == True)
            
            if skills_filter:
                # Use PostgreSQL array operations for skills filtering
                query = query.filter(
                    Resource.skills.op('&&')(skills_filter)  # Overlap operator
                )
            
            return query
        
        return get_resources_with_skills


class PaginatedQuery:
    """Paginated query implementation"""
    
    def __init__(self, query, page: int = 1, per_page: int = 20, max_per_page: int = 100):
        self.query = query
        self.page = max(1, page)
        self.per_page = min(per_page, max_per_page)
        self.max_per_page = max_per_page
    
    def paginate(self):
        """Apply pagination to query"""
        offset = (self.page - 1) * self.per_page
        return self.query.offset(offset).limit(self.per_page)
    
    async def get_paginated_result(self, session):
        """Get paginated result with metadata"""
        # Get total count
        total_count = session.query(self.query.subquery()).count()
        
        # Get paginated data
        paginated_query = self.paginate()
        data = paginated_query.all()
        
        # Calculate pagination metadata
        total_pages = (total_count + self.per_page - 1) // self.per_page
        
        return {
            "data": data,
            "pagination": {
                "page": self.page,
                "per_page": self.per_page,
                "total": total_count,
                "pages": total_pages,
                "has_next": self.page < total_pages,
                "has_prev": self.page > 1,
                "next_page": self.page + 1 if self.page < total_pages else None,
                "prev_page": self.page - 1 if self.page > 1 else None
            }
        }


class QueryPerformanceMonitor:
    """Monitor and log query performance"""
    
    def __init__(self):
        self.slow_query_threshold = 1.0  # seconds
        self.query_stats = {}
    
    def log_query_performance(self, query_name: str, execution_time: float, 
                             row_count: int = None, query_sql: str = None):
        """Log query performance metrics"""
        
        # Update statistics
        if query_name not in self.query_stats:
            self.query_stats[query_name] = {
                "count": 0,
                "total_time": 0,
                "avg_time": 0,
                "max_time": 0,
                "min_time": float('inf'),
                "slow_queries": 0
            }
        
        stats = self.query_stats[query_name]
        stats["count"] += 1
        stats["total_time"] += execution_time
        stats["avg_time"] = stats["total_time"] / stats["count"]
        stats["max_time"] = max(stats["max_time"], execution_time)
        stats["min_time"] = min(stats["min_time"], execution_time)
        
        if execution_time > self.slow_query_threshold:
            stats["slow_queries"] += 1
            logger.warning(f"🐌 Slow query detected: {query_name} took {execution_time:.3f}s")
            
            if query_sql:
                logger.warning(f"SQL: {query_sql}")
        
        # Log performance
        if execution_time > 0.5:  # Log queries taking more than 500ms
            logger.info(f"📊 Query: {query_name} | Time: {execution_time:.3f}s | Rows: {row_count or 'N/A'}")
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """Get query performance summary"""
        summary = {
            "total_queries": sum(stats["count"] for stats in self.query_stats.values()),
            "slow_queries": sum(stats["slow_queries"] for stats in self.query_stats.values()),
            "avg_execution_time": 0,
            "queries": {}
        }
        
        total_time = sum(stats["total_time"] for stats in self.query_stats.values())
        if summary["total_queries"] > 0:
            summary["avg_execution_time"] = total_time / summary["total_queries"]
        
        for query_name, stats in self.query_stats.items():
            summary["queries"][query_name] = {
                "count": stats["count"],
                "avg_time": stats["avg_time"],
                "max_time": stats["max_time"],
                "min_time": stats["min_time"],
                "slow_queries": stats["slow_queries"]
            }
        
        return summary


# Global query performance monitor
query_monitor = QueryPerformanceMonitor()


def monitor_query_performance(query_name: str):
    """Decorator to monitor query performance"""
    def decorator(func):
        async def wrapper(*args, **kwargs):
            import time
            start_time = time.time()
            
            try:
                result = await func(*args, **kwargs)
                execution_time = time.time() - start_time
                
                # Log performance
                row_count = len(result) if isinstance(result, (list, tuple)) else None
                query_monitor.log_query_performance(
                    query_name, execution_time, row_count
                )
                
                return result
                
            except Exception as e:
                execution_time = time.time() - start_time
                query_monitor.log_query_performance(
                    query_name, execution_time, 0, str(e)
                )
                raise
        
        return wrapper
    return decorator


class DatabaseConnectionPool:
    """Database connection pool management"""
    
    def __init__(self, engine):
        self.engine = engine
        self.pool_stats = {
            "size": 0,
            "checked_in": 0,
            "checked_out": 0,
            "overflow": 0,
            "invalid": 0
        }
    
    def get_pool_status(self) -> Dict[str, Any]:
        """Get connection pool status"""
        pool = self.engine.pool
        
        return {
            "pool_size": pool.size(),
            "checked_in": pool.checkedin(),
            "checked_out": pool.checkedout(),
            "overflow": pool.overflow(),
            "invalid": pool.invalid(),
            "total_connections": pool.size() + pool.overflow()
        }
    
    def optimize_pool_settings(self):
        """Optimize connection pool settings"""
        # These settings should be configured in database configuration
        optimal_settings = {
            "pool_size": 20,        # Base pool size
            "max_overflow": 30,      # Additional connections
            "pool_timeout": 30,      # Timeout for getting connection
            "pool_recycle": 3600,    # Recycle connections after 1 hour
            "pool_pre_ping": True    # Test connections before use
        }
        
        logger.info(f"🔧 Recommended pool settings: {optimal_settings}")
        return optimal_settings


# Query optimization utilities
def prevent_n_plus_one(query, relations: List[str]):
    """Prevent N+1 queries by eager loading relations"""
    options = []
    
    for relation in relations:
        if '.' in relation:
            # Handle nested relations (e.g., 'features.backlogs')
            parts = relation.split('.')
            current_option = joinedload(getattr(query.column_descriptions[0]['entity'], parts[0]))
            for part in parts[1:]:
                current_option = current_option.joinedload(part)
            options.append(current_option)
        else:
            # Handle direct relations
            options.append(joinedload(getattr(query.column_descriptions[0]['entity'], relation)))
    
    return query.options(*options)


def optimize_bulk_operations(session, model_class, operations: List[Dict]):
    """Optimize bulk database operations"""
    
    # Group operations by type
    inserts = [op for op in operations if op['type'] == 'insert']
    updates = [op for op in operations if op['type'] == 'update']
    deletes = [op for op in operations if op['type'] == 'delete']
    
    # Perform bulk operations
    if inserts:
        session.bulk_insert_mappings(model_class, inserts)
        logger.info(f"📥 Bulk inserted {len(inserts)} records")
    
    if updates:
        session.bulk_update_mappings(model_class, updates)
        logger.info(f"📝 Bulk updated {len(updates)} records")
    
    if deletes:
        # For deletes, we need to use bulk_delete_mappings or individual deletes
        for delete_op in deletes:
            session.query(model_class).filter_by(**delete_op['filters']).delete()
        logger.info(f"🗑️ Bulk deleted {len(deletes)} records")
    
    return len(operations)


# Import models (these would be imported from your models module)
# from app.models import Project, Feature, Backlog, Resource, Function

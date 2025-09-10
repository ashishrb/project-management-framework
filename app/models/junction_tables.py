"""
Junction Tables for Many-to-Many Relationships
Supporting cross-referencing between projects, tasks, features, and resources
"""
from sqlalchemy import Column, Integer, ForeignKey, DateTime, String
from sqlalchemy.orm import relationship
from app.database import Base

class ProjectFunction(Base):
    """Junction table for Project-Function many-to-many relationship"""
    __tablename__ = "project_functions"
    
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    function_id = Column(Integer, ForeignKey("functions.id"), nullable=False)
    
    # Additional metadata
    created_at = Column(DateTime)
    created_by = Column(String(100))
    
    # Relationships
    project = relationship("Project")
    function = relationship("Function")

class ProjectPlatform(Base):
    """Junction table for Project-Platform many-to-many relationship"""
    __tablename__ = "project_platforms"
    
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    platform_id = Column(Integer, ForeignKey("platforms.id"), nullable=False)
    
    # Additional metadata
    created_at = Column(DateTime)
    created_by = Column(String(100))
    
    # Relationships
    project = relationship("Project")
    platform = relationship("Platform")

class TaskFunction(Base):
    """Junction table for Task-Function many-to-many relationship"""
    __tablename__ = "task_functions"
    
    id = Column(Integer, primary_key=True, index=True)
    task_id = Column(Integer, ForeignKey("tasks.id"), nullable=False)
    function_id = Column(Integer, ForeignKey("functions.id"), nullable=False)
    
    # Additional metadata
    created_at = Column(DateTime)
    created_by = Column(String(100))
    
    # Relationships
    task = relationship("Task")
    function = relationship("Function")

class TaskPlatform(Base):
    """Junction table for Task-Platform many-to-many relationship"""
    __tablename__ = "task_platforms"
    
    id = Column(Integer, primary_key=True, index=True)
    task_id = Column(Integer, ForeignKey("tasks.id"), nullable=False)
    platform_id = Column(Integer, ForeignKey("platforms.id"), nullable=False)
    
    # Additional metadata
    created_at = Column(DateTime)
    created_by = Column(String(100))
    
    # Relationships
    task = relationship("Task")
    platform = relationship("Platform")

class FeatureFunction(Base):
    """Junction table for Feature-Function many-to-many relationship"""
    __tablename__ = "feature_functions"
    
    id = Column(Integer, primary_key=True, index=True)
    feature_id = Column(Integer, ForeignKey("features.id"), nullable=False)
    function_id = Column(Integer, ForeignKey("functions.id"), nullable=False)
    
    # Additional metadata
    created_at = Column(DateTime)
    created_by = Column(String(100))
    
    # Relationships
    feature = relationship("Feature")
    function = relationship("Function")

class FeaturePlatform(Base):
    """Junction table for Feature-Platform many-to-many relationship"""
    __tablename__ = "feature_platforms"
    
    id = Column(Integer, primary_key=True, index=True)
    feature_id = Column(Integer, ForeignKey("features.id"), nullable=False)
    platform_id = Column(Integer, ForeignKey("platforms.id"), nullable=False)
    
    # Additional metadata
    created_at = Column(DateTime)
    created_by = Column(String(100))
    
    # Relationships
    feature = relationship("Feature")
    platform = relationship("Platform")

class ResourceFunction(Base):
    """Junction table for Resource-Function many-to-many relationship"""
    __tablename__ = "resource_functions"
    
    id = Column(Integer, primary_key=True, index=True)
    resource_id = Column(Integer, ForeignKey("resources.id"), nullable=False)
    function_id = Column(Integer, ForeignKey("functions.id"), nullable=False)
    
    # Additional metadata
    created_at = Column(DateTime)
    created_by = Column(String(100))
    
    # Relationships
    resource = relationship("Resource")
    function = relationship("Function")

class ResourcePlatform(Base):
    """Junction table for Resource-Platform many-to-many relationship"""
    __tablename__ = "resource_platforms"
    
    id = Column(Integer, primary_key=True, index=True)
    resource_id = Column(Integer, ForeignKey("resources.id"), nullable=False)
    platform_id = Column(Integer, ForeignKey("platforms.id"), nullable=False)
    
    # Additional metadata
    created_at = Column(DateTime)
    created_by = Column(String(100))
    
    # Relationships
    resource = relationship("Resource")
    platform = relationship("Platform")

class ProjectResource(Base):
    """Junction table for Project-Resource many-to-many relationship"""
    __tablename__ = "project_resources"
    
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    resource_id = Column(Integer, ForeignKey("resources.id"), nullable=False)
    
    # Resource allocation details
    allocation_percentage = Column(Integer, default=100)  # 0-100%
    role_in_project = Column(String(100))  # Project Manager, Developer, etc.
    start_date = Column(DateTime)
    end_date = Column(DateTime)
    
    # Additional metadata
    created_at = Column(DateTime)
    created_by = Column(String(100))
    
    # Relationships
    project = relationship("Project")
    resource = relationship("Resource")

class TaskResource(Base):
    """Junction table for Task-Resource many-to-many relationship"""
    __tablename__ = "task_resources"
    
    id = Column(Integer, primary_key=True, index=True)
    task_id = Column(Integer, ForeignKey("tasks.id"), nullable=False)
    resource_id = Column(Integer, ForeignKey("resources.id"), nullable=False)
    
    # Resource allocation details
    allocation_percentage = Column(Integer, default=100)  # 0-100%
    estimated_hours = Column(Integer)
    actual_hours = Column(Integer)
    
    # Additional metadata
    created_at = Column(DateTime)
    created_by = Column(String(100))
    
    # Relationships
    task = relationship("Task")
    resource = relationship("Resource")

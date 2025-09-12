"""
Core Lookup Tables for GenAI Metrics Dashboard
Based on PROJECT_FLOW_DIAGRAM.md specifications
"""
from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base

class Function(Base):
    """Functions lookup table - 17 items (HR, Finance, Technology, etc.)"""
    __tablename__ = "functions"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False, index=True)
    description = Column(Text)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime)
    updated_at = Column(DateTime)

class Platform(Base):
    """Platforms lookup table - 9 items (LC Platform, Commercial, Custom, etc.)"""
    __tablename__ = "platforms"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False, index=True)
    description = Column(Text)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime)
    updated_at = Column(DateTime)

class Priority(Base):
    """Priorities lookup table - 6 levels (Critical, High, Medium, Low, etc.)"""
    __tablename__ = "priorities"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), unique=True, nullable=False, index=True)
    level = Column(Integer, unique=True, nullable=False)  # 0=Critical, 1=High, etc.
    description = Column(Text)
    color_code = Column(String(7))  # Hex color for UI
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime)
    updated_at = Column(DateTime)

class Status(Base):
    """Statuses lookup table - 4 types (Active, Completed, At Risk, Off Track)"""
    __tablename__ = "statuses"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), unique=True, nullable=False, index=True)
    description = Column(Text)
    color_code = Column(String(7))  # Hex color for UI
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime)
    updated_at = Column(DateTime)

class Portfolio(Base):
    """Portfolios lookup table - L1/L2 hierarchy"""
    __tablename__ = "portfolios"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False, index=True)
    level = Column(Integer, nullable=False)  # 1=L1, 2=L2
    parent_id = Column(Integer, ForeignKey("portfolios.id"), nullable=True)
    description = Column(Text)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime)
    updated_at = Column(DateTime)
    
    # Self-referential relationship
    parent = relationship("Portfolio", remote_side=[id])

class Application(Base):
    """Applications lookup table - SOX/Non-SOX classification"""
    __tablename__ = "applications"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False, index=True)
    sox_classification = Column(String(20), nullable=False)  # SOX/Non-SOX
    description = Column(Text)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime)
    updated_at = Column(DateTime)

class InvestmentType(Base):
    """Investment Types lookup table - Transform, Enhance, etc."""
    __tablename__ = "investment_types"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), unique=True, nullable=False, index=True)
    description = Column(Text)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime)
    updated_at = Column(DateTime)

class JourneyMap(Base):
    """Journey Maps lookup table"""
    __tablename__ = "journey_maps"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False, index=True)
    description = Column(Text)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime)
    updated_at = Column(DateTime)

class ProjectType(Base):
    """Project Types lookup table - 4 types"""
    __tablename__ = "project_types"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), unique=True, nullable=False, index=True)
    description = Column(Text)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime)
    updated_at = Column(DateTime)

class ProjectStatusClassification(Base):
    """Project Status Classifications lookup table"""
    __tablename__ = "project_status_classifications"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), unique=True, nullable=False, index=True)
    description = Column(Text)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime)
    updated_at = Column(DateTime)

class ProjectPriorityClassification(Base):
    """Project Priority Classifications lookup table"""
    __tablename__ = "project_priority_classifications"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), unique=True, nullable=False, index=True)
    description = Column(Text)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime)
    updated_at = Column(DateTime)

class ProjectCriticalityLevel(Base):
    """Project Criticality Levels lookup table"""
    __tablename__ = "project_criticality_levels"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), unique=True, nullable=False, index=True)
    level = Column(Integer, unique=True, nullable=False)  # 0=Critical, 1=High, etc.
    description = Column(Text)
    color_code = Column(String(7))  # Hex color for UI
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime)
    updated_at = Column(DateTime)

class BusinessUnit(Base):
    """Business Units lookup table - IT, Legal, Finance, HR, etc."""
    __tablename__ = "business_units"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False, index=True)
    description = Column(Text)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime)
    updated_at = Column(DateTime)

class InvestmentClass(Base):
    """Investment Classes lookup table - Change, etc."""
    __tablename__ = "investment_classes"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), unique=True, nullable=False, index=True)
    description = Column(Text)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime)
    updated_at = Column(DateTime)

class BenefitCategory(Base):
    """Benefit Categories lookup table - Cost savings, Revenue, Process Improvement, etc."""
    __tablename__ = "benefit_categories"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False, index=True)
    description = Column(Text)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime)
    updated_at = Column(DateTime)

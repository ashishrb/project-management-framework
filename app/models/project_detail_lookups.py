"""
Additional Lookup Tables for Project Detail Management
Based on the project detail screenshots requirements
"""
from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime
from app.database import Base

class DemandCategory(Base):
    """Demand Categories lookup table - Transform, Enhance, etc."""
    __tablename__ = "demand_categories"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), unique=True, nullable=False, index=True)
    description = Column(Text)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime)
    updated_at = Column(DateTime)

class ModernizationDomain(Base):
    """Modernization Domains lookup table"""
    __tablename__ = "modernization_domains"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False, index=True)
    description = Column(Text)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime)
    updated_at = Column(DateTime)

class DigitizationCategory(Base):
    """Digitization Categories lookup table"""
    __tablename__ = "digitization_categories"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False, index=True)
    description = Column(Text)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime)
    updated_at = Column(DateTime)

class DeliveryOrganization(Base):
    """Delivery Organizations lookup table - L1/L2 hierarchy"""
    __tablename__ = "delivery_organizations"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False, index=True)
    level = Column(Integer, nullable=False)  # 1=L1, 2=L2
    parent_id = Column(Integer, nullable=True)
    description = Column(Text)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime)
    updated_at = Column(DateTime)

class ExpenseType(Base):
    """Expense Types lookup table - WI (Work Item) types"""
    __tablename__ = "expense_types"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), unique=True, nullable=False, index=True)
    code = Column(String(20), unique=True, nullable=False)  # WI code
    description = Column(Text)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime)
    updated_at = Column(DateTime)

class BusinessProcess(Base):
    """Business Processes lookup table"""
    __tablename__ = "business_processes"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), unique=True, nullable=False, index=True)
    description = Column(Text)
    category = Column(String(100))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime)
    updated_at = Column(DateTime)

class GenerativeAIImpact(Base):
    """Generative AI Impact levels lookup table"""
    __tablename__ = "generative_ai_impacts"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), unique=True, nullable=False, index=True)
    description = Column(Text)
    impact_level = Column(Integer)  # 1=Low, 2=Medium, 3=High, 4=Critical
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime)
    updated_at = Column(DateTime)

class ProjectPhase(Base):
    """Project Phases lookup table - Initiation, Planning, Execution, Closure"""
    __tablename__ = "project_phases"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), unique=True, nullable=False, index=True)
    description = Column(Text)
    phase_order = Column(Integer, nullable=False)  # 1=Initiation, 2=Planning, etc.
    color_code = Column(String(7))  # Hex color for UI
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime)
    updated_at = Column(DateTime)

class ProjectState(Base):
    """Project States lookup table - Active, Inactive, Suspended, Cancelled"""
    __tablename__ = "project_states"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), unique=True, nullable=False, index=True)
    description = Column(Text)
    color_code = Column(String(7))  # Hex color for UI
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime)
    updated_at = Column(DateTime)

class NISTDomain(Base):
    """NIST CSF Domains lookup table"""
    __tablename__ = "nist_domains"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False, index=True)
    description = Column(Text)
    domain_code = Column(String(20), unique=True, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime)
    updated_at = Column(DateTime)

class NISTMapping(Base):
    """NIST CSF Mappings lookup table"""
    __tablename__ = "nist_mappings"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False, index=True)
    description = Column(Text)
    mapping_code = Column(String(20), unique=True, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime)
    updated_at = Column(DateTime)

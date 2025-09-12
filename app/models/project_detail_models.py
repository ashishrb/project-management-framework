"""
Additional Models for Comprehensive Project Detail Management
Based on the project detail screenshots requirements
"""
from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey, Date, JSON, Numeric
from sqlalchemy.orm import relationship
from app.database import Base

class ProjectStakeholder(Base):
    """Project Stakeholders table - Business Owner, Sponsor, Technology Leader, etc."""
    __tablename__ = "project_stakeholders"
    
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    
    # Stakeholder information
    stakeholder_type = Column(String(50), nullable=False)  # Business Owner, Business Sponsor, Technology Portfolio Leader
    name = Column(String(100), nullable=False)
    email = Column(String(100))
    role = Column(String(100))
    department = Column(String(100))
    
    # Additional metadata
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime)
    updated_at = Column(DateTime)
    created_by = Column(String(100))
    updated_by = Column(String(100))
    
    # Relationships
    project = relationship("Project")

class ProjectCharter(Base):
    """Enhanced Project Charter table with approval workflow"""
    __tablename__ = "project_charters"
    
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    
    # Charter content
    additional_observations = Column(Text)
    sustainability_operationalization = Column(Text)
    assumptions = Column(Text)
    out_of_scope = Column(Text)
    charter_status = Column(String(50))  # Draft, Under Review, Approved, Rejected
    
    # Approval workflow
    risk_management_approval = Column(String(50))  # Pending, Approved, Rejected
    risk_approver = Column(String(100))
    risk_approval_date = Column(DateTime)
    charter_approved = Column(String(50))  # Pending, Approved, Rejected
    charter_approver = Column(String(100))
    charter_approval_date = Column(DateTime)
    
    # Additional metadata
    created_at = Column(DateTime)
    updated_at = Column(DateTime)
    created_by = Column(String(100))
    updated_by = Column(String(100))
    
    # Relationships
    project = relationship("Project")

class ProjectNIST(Base):
    """NIST CSF Alignment table for IT & Security projects"""
    __tablename__ = "project_nist"
    
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    
    # NIST CSF information
    nist_finding_high_priority_improvements = Column(Text)
    nist_mapping = Column(String(100))
    nist_domain = Column(String(100))
    nist_ofi_number = Column(String(50))  # NIST OFI#
    nist_self_assessment_score = Column(Numeric(3, 2))  # 0-5 scale
    
    # Additional metadata
    created_at = Column(DateTime)
    updated_at = Column(DateTime)
    created_by = Column(String(100))
    updated_by = Column(String(100))
    
    # Relationships
    project = relationship("Project")

class ProjectLifecycle(Base):
    """Project Lifecycle tracking table"""
    __tablename__ = "project_lifecycle"
    
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    
    # Lifecycle stages
    current_phase = Column(String(50), nullable=False)  # Initiation, Planning, Execution, Closure
    phase_start_date = Column(DateTime)
    phase_end_date = Column(DateTime)
    phase_duration_days = Column(Integer)
    
    # Phase transitions
    previous_phase = Column(String(50))
    next_phase = Column(String(50))
    phase_transition_date = Column(DateTime)
    
    # Additional metadata
    created_at = Column(DateTime)
    updated_at = Column(DateTime)
    created_by = Column(String(100))
    updated_by = Column(String(100))
    
    # Relationships
    project = relationship("Project")

class ProjectDependency(Base):
    """Project Dependencies table - System, Process, Resource dependencies"""
    __tablename__ = "project_dependencies"
    
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    
    # Dependency information
    dependency_type = Column(String(50), nullable=False)  # System, Process, Resource
    dependency_name = Column(String(200), nullable=False)
    dependency_description = Column(Text)
    dependency_status = Column(String(50))  # Open, In Progress, Resolved, Blocked
    
    # Dependency details
    criticality = Column(String(20))  # Low, Medium, High, Critical
    impact_if_unresolved = Column(Text)
    resolution_owner = Column(String(100))
    resolution_due_date = Column(Date)
    
    # Additional metadata
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime)
    updated_at = Column(DateTime)
    created_by = Column(String(100))
    updated_by = Column(String(100))
    
    # Relationships
    project = relationship("Project")

class ProjectApplication(Base):
    """Project Applications Impact table - SOX/Non-SOX applications"""
    __tablename__ = "project_applications"
    
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    application_id = Column(Integer, ForeignKey("applications.id"), nullable=False)
    
    # Impact information
    impact_type = Column(String(50))  # Direct, Indirect, Integration
    impact_description = Column(Text)
    sox_impact = Column(Boolean, default=False)
    
    # Additional metadata
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime)
    updated_at = Column(DateTime)
    created_by = Column(String(100))
    updated_by = Column(String(100))
    
    # Relationships
    project = relationship("Project")
    application = relationship("Application")

class ProjectBaseline(Base):
    """Project Baseline tracking table"""
    __tablename__ = "project_baselines"
    
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    
    # Baseline information
    baseline_start_date = Column(Date)
    baseline_due_date = Column(Date)
    baseline_budget = Column(Numeric(15, 2))
    baseline_scope = Column(Text)
    
    # Variance tracking
    start_date_variance = Column(Integer)  # Days variance
    due_date_variance = Column(Integer)    # Days variance
    budget_variance = Column(Numeric(15, 2))
    scope_variance = Column(Text)
    
    # Baseline approval
    baseline_approved = Column(Boolean, default=False)
    baseline_approver = Column(String(100))
    baseline_approval_date = Column(DateTime)
    
    # Additional metadata
    created_at = Column(DateTime)
    updated_at = Column(DateTime)
    created_by = Column(String(100))
    updated_by = Column(String(100))
    
    # Relationships
    project = relationship("Project")

class ProjectStatusDetail(Base):
    """Enhanced Project Status Details table"""
    __tablename__ = "project_status_details"
    
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    
    # Status information
    state = Column(String(50))  # Active, Inactive, Suspended, Cancelled
    phase = Column(String(50))  # Initiation, Planning, Execution, Closure
    project_type = Column(String(50))  # Approved, Proposed, Pilot
    status = Column(String(50))  # On Track, At Risk, Off Track, Completed
    status_headline = Column(Text)
    
    # Timeline information
    start_date = Column(Date)
    due_date = Column(Date)
    actual_start_date = Column(Date)
    actual_end_date = Column(Date)
    
    # Additional metadata
    created_at = Column(DateTime)
    updated_at = Column(DateTime)
    created_by = Column(String(100))
    updated_by = Column(String(100))
    
    # Relationships
    project = relationship("Project")

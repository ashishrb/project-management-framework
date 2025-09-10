"""
Main Data Tables for GenAI Metrics Dashboard
Enhanced schema supporting 270+ features, 216+ backlogs, and comprehensive project management
"""
from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey, Numeric, Date, JSON
from sqlalchemy.orm import relationship
from app.database import Base

class Project(Base):
    """Enhanced Projects table with 20+ columns supporting enterprise requirements"""
    __tablename__ = "projects"
    
    # Primary identification
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(String(20), unique=True, nullable=False, index=True)  # P-47505, P-80008, etc.
    esa_id = Column(String(20), nullable=True, index=True)  # 1000386270, etc.
    
    # Basic project information
    name = Column(String(200), nullable=False, index=True)
    description = Column(Text)
    project_type_id = Column(Integer, ForeignKey("project_types.id"))
    status_id = Column(Integer, ForeignKey("statuses.id"))
    priority_id = Column(Integer, ForeignKey("priorities.id"))
    criticality_id = Column(Integer, ForeignKey("project_criticality_levels.id"))
    
    # Portfolio and classification
    portfolio_id = Column(Integer, ForeignKey("portfolios.id"))
    sub_portfolio = Column(String(100))
    top_level_portfolio = Column(String(100))
    investment_type_id = Column(Integer, ForeignKey("investment_types.id"))
    
    # Modernization and digitization
    modernization_domain = Column(String(100))
    digitization_category = Column(String(100))
    
    # Financial information
    budget_amount = Column(Numeric(15, 2))
    funding_status = Column(String(50))
    budget_status = Column(String(50))
    
    # Timeline information
    start_date = Column(Date)
    due_date = Column(Date)
    actual_start_date = Column(Date)
    actual_end_date = Column(Date)
    
    # Progress tracking
    percent_complete = Column(Numeric(5, 2), default=0.0)
    
    # Stakeholder information
    project_manager = Column(String(100))
    technology_portfolio_leader = Column(String(100))
    business_owner = Column(String(100))
    owner = Column(String(100))
    
    # Additional metadata
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime)
    updated_at = Column(DateTime)
    created_by = Column(String(100))
    updated_by = Column(String(100))
    
    # Relationships
    project_type = relationship("app.models.lookup_tables.ProjectType")
    status = relationship("app.models.lookup_tables.Status")
    priority = relationship("app.models.lookup_tables.Priority")
    criticality = relationship("app.models.lookup_tables.ProjectCriticalityLevel")
    portfolio = relationship("app.models.lookup_tables.Portfolio")
    investment_type = relationship("app.models.lookup_tables.InvestmentType")

class Task(Base):
    """Enhanced Tasks table with Gantt chart support"""
    __tablename__ = "tasks"
    
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    task_name = Column(String(200), nullable=False)
    description = Column(Text)
    
    # Task classification
    status_id = Column(Integer, ForeignKey("statuses.id"))
    priority_id = Column(Integer, ForeignKey("priorities.id"))
    
    # Timeline information
    start_date = Column(Date)
    due_date = Column(Date)
    actual_start_date = Column(Date)
    actual_end_date = Column(Date)
    estimated_hours = Column(Numeric(8, 2))
    actual_hours = Column(Numeric(8, 2))
    
    # Progress tracking
    percent_complete = Column(Numeric(5, 2), default=0.0)
    
    # Dependencies
    predecessor_tasks = Column(JSON)  # Array of task IDs
    successor_tasks = Column(JSON)    # Array of task IDs
    
    # Additional metadata
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime)
    updated_at = Column(DateTime)
    created_by = Column(String(100))
    updated_by = Column(String(100))
    
    # Relationships
    project = relationship("Project")
    status = relationship("app.models.lookup_tables.Status")
    priority = relationship("app.models.lookup_tables.Priority")

class Feature(Base):
    """Features table - 270+ items supporting GenAI analytics"""
    __tablename__ = "features"
    
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    feature_name = Column(String(200), nullable=False, index=True)
    description = Column(Text)
    
    # Feature classification
    status_id = Column(Integer, ForeignKey("statuses.id"))
    priority_id = Column(Integer, ForeignKey("priorities.id"))
    
    # Business context
    business_value = Column(Text)
    acceptance_criteria = Column(Text)
    
    # Technical information
    complexity = Column(String(20))  # Low, Medium, High
    effort_estimate = Column(Numeric(8, 2))  # Story points or hours
    
    # Timeline information
    planned_start_date = Column(Date)
    planned_end_date = Column(Date)
    actual_start_date = Column(Date)
    actual_end_date = Column(Date)
    
    # Progress tracking
    percent_complete = Column(Numeric(5, 2), default=0.0)
    
    # Additional metadata
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime)
    updated_at = Column(DateTime)
    created_by = Column(String(100))
    updated_by = Column(String(100))
    
    # Relationships
    project = relationship("Project")
    status = relationship("app.models.lookup_tables.Status")
    priority = relationship("app.models.lookup_tables.Priority")

class Backlog(Base):
    """Backlogs table - 216+ items with priority management"""
    __tablename__ = "backlogs"
    
    id = Column(Integer, primary_key=True, index=True)
    backlog_id = Column(String(20), unique=True, nullable=False, index=True)  # BL-001, BL-002, etc.
    name = Column(String(200), nullable=False, index=True)
    description = Column(Text)
    
    # Backlog classification
    priority_id = Column(Integer, ForeignKey("priorities.id"))
    status_id = Column(Integer, ForeignKey("statuses.id"))
    
    # Business context
    business_value = Column(Text)
    user_story = Column(Text)
    acceptance_criteria = Column(Text)
    
    # Technical information
    complexity = Column(String(20))  # Low, Medium, High
    effort_estimate = Column(Numeric(8, 2))  # Story points or hours
    
    # Timeline information
    target_quarter = Column(String(10))  # Q1 2025, Q2 2025, etc.
    planned_start_date = Column(Date)
    planned_end_date = Column(Date)
    
    # Additional metadata
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime)
    updated_at = Column(DateTime)
    created_by = Column(String(100))
    updated_by = Column(String(100))
    
    # Relationships
    priority = relationship("app.models.lookup_tables.Priority")
    status = relationship("app.models.lookup_tables.Status")

class Resource(Base):
    """Resources table - 10+ resources with skills and allocation"""
    __tablename__ = "resources"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, index=True)
    email = Column(String(100), unique=True, nullable=False, index=True)
    
    # Role and skills
    role = Column(String(50))  # Developer, Manager, Analyst, etc.
    skills = Column(JSON)  # Array of skill strings
    experience_level = Column(String(20))  # Junior, Mid, Senior, Lead
    
    # Availability
    is_active = Column(Boolean, default=True)
    availability_percentage = Column(Numeric(5, 2), default=100.0)
    
    # Additional metadata
    created_at = Column(DateTime)
    updated_at = Column(DateTime)
    created_by = Column(String(100))
    updated_by = Column(String(100))

class Risk(Base):
    """Risks table - 2 active risks with mitigation plans"""
    __tablename__ = "risks"
    
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    risk_name = Column(String(200), nullable=False)
    description = Column(Text)
    
    # Risk classification
    risk_level = Column(String(20))  # Low, Medium, High, Critical
    probability = Column(Numeric(5, 2))  # 0.0 to 1.0
    impact = Column(Numeric(5, 2))  # 0.0 to 1.0
    risk_score = Column(Numeric(5, 2))  # probability * impact
    
    # Mitigation information
    mitigation_plan = Column(Text)
    mitigation_owner = Column(String(100))
    mitigation_due_date = Column(Date)
    
    # Status tracking
    status = Column(String(50))  # Open, In Progress, Mitigated, Closed
    is_active = Column(Boolean, default=True)
    
    # Additional metadata
    created_at = Column(DateTime)
    updated_at = Column(DateTime)
    created_by = Column(String(100))
    updated_by = Column(String(100))
    
    # Relationships
    project = relationship("Project")

class Approval(Base):
    """Approvals table - 3 types (Risk, EA, Security)"""
    __tablename__ = "approvals"
    
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    approval_type = Column(String(50), nullable=False)  # Risk, EA, Security
    approval_status = Column(String(50), nullable=False)  # Pending, Approved, Rejected
    
    # Approval details
    approver = Column(String(100))
    approval_date = Column(DateTime)
    comments = Column(Text)
    
    # Additional metadata
    created_at = Column(DateTime)
    updated_at = Column(DateTime)
    created_by = Column(String(100))
    updated_by = Column(String(100))
    
    # Relationships
    project = relationship("Project")

class Charter(Base):
    """Charters table - Complete project charter information"""
    __tablename__ = "charters"
    
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    
    # Charter content
    scope = Column(Text)
    assumptions = Column(Text)
    out_of_scope = Column(Text)
    success_criteria = Column(Text)
    constraints = Column(Text)
    
    # Additional metadata
    created_at = Column(DateTime)
    updated_at = Column(DateTime)
    created_by = Column(String(100))
    updated_by = Column(String(100))
    
    # Relationships
    project = relationship("Project")

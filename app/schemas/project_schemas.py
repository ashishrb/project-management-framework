"""
Pydantic schemas for project management
"""
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime, date
from decimal import Decimal

# ==================== PROJECT SCHEMAS ====================

class ProjectBase(BaseModel):
    project_id: str
    esa_id: Optional[str] = None
    name: str
    description: Optional[str] = None
    project_type_id: Optional[int] = None
    status_id: Optional[int] = None
    priority_id: Optional[int] = None
    criticality_id: Optional[int] = None
    portfolio_id: Optional[int] = None
    sub_portfolio: Optional[str] = None
    top_level_portfolio: Optional[str] = None
    investment_type_id: Optional[int] = None
    modernization_domain: Optional[str] = None
    digitization_category: Optional[str] = None
    budget_amount: Optional[Decimal] = None
    funding_status: Optional[str] = None
    budget_status: Optional[str] = None
    start_date: Optional[date] = None
    due_date: Optional[date] = None
    actual_start_date: Optional[date] = None
    actual_end_date: Optional[date] = None
    percent_complete: Optional[Decimal] = None
    project_manager: Optional[str] = None
    technology_portfolio_leader: Optional[str] = None
    business_owner: Optional[str] = None
    owner: Optional[str] = None

class ProjectCreate(ProjectBase):
    pass

class ProjectUpdate(BaseModel):
    project_id: Optional[str] = None
    esa_id: Optional[str] = None
    name: Optional[str] = None
    description: Optional[str] = None
    project_type_id: Optional[int] = None
    status_id: Optional[int] = None
    priority_id: Optional[int] = None
    criticality_id: Optional[int] = None
    portfolio_id: Optional[int] = None
    sub_portfolio: Optional[str] = None
    top_level_portfolio: Optional[str] = None
    investment_type_id: Optional[int] = None
    modernization_domain: Optional[str] = None
    digitization_category: Optional[str] = None
    budget_amount: Optional[Decimal] = None
    funding_status: Optional[str] = None
    budget_status: Optional[str] = None
    start_date: Optional[date] = None
    due_date: Optional[date] = None
    actual_start_date: Optional[date] = None
    actual_end_date: Optional[date] = None
    percent_complete: Optional[Decimal] = None
    project_manager: Optional[str] = None
    technology_portfolio_leader: Optional[str] = None
    business_owner: Optional[str] = None
    owner: Optional[str] = None

class ProjectResponse(ProjectBase):
    id: int
    is_active: bool = True
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    created_by: Optional[str] = None
    updated_by: Optional[str] = None

    class Config:
        from_attributes = True

# ==================== TASK SCHEMAS ====================

class TaskBase(BaseModel):
    task_name: str
    description: Optional[str] = None
    status_id: Optional[int] = None
    priority_id: Optional[int] = None
    start_date: Optional[date] = None
    due_date: Optional[date] = None
    actual_start_date: Optional[date] = None
    actual_end_date: Optional[date] = None
    estimated_hours: Optional[Decimal] = None
    actual_hours: Optional[Decimal] = None
    percent_complete: Optional[Decimal] = None
    predecessor_tasks: Optional[List[int]] = None
    successor_tasks: Optional[List[int]] = None

class TaskCreate(TaskBase):
    pass

class TaskUpdate(BaseModel):
    task_name: Optional[str] = None
    description: Optional[str] = None
    status_id: Optional[int] = None
    priority_id: Optional[int] = None
    start_date: Optional[date] = None
    due_date: Optional[date] = None
    actual_start_date: Optional[date] = None
    actual_end_date: Optional[date] = None
    estimated_hours: Optional[Decimal] = None
    actual_hours: Optional[Decimal] = None
    percent_complete: Optional[Decimal] = None
    predecessor_tasks: Optional[List[int]] = None
    successor_tasks: Optional[List[int]] = None

class TaskResponse(TaskBase):
    id: int
    project_id: int
    is_active: bool = True
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    created_by: Optional[str] = None
    updated_by: Optional[str] = None

    class Config:
        from_attributes = True

# ==================== FEATURE SCHEMAS ====================

class FeatureBase(BaseModel):
    feature_name: str
    description: Optional[str] = None
    status_id: Optional[int] = None
    priority_id: Optional[int] = None
    business_value: Optional[str] = None
    acceptance_criteria: Optional[str] = None
    complexity: Optional[str] = None
    effort_estimate: Optional[Decimal] = None
    planned_start_date: Optional[date] = None
    planned_end_date: Optional[date] = None
    actual_start_date: Optional[date] = None
    actual_end_date: Optional[date] = None
    percent_complete: Optional[Decimal] = None

class FeatureCreate(FeatureBase):
    pass

class FeatureUpdate(BaseModel):
    feature_name: Optional[str] = None
    description: Optional[str] = None
    status_id: Optional[int] = None
    priority_id: Optional[int] = None
    business_value: Optional[str] = None
    acceptance_criteria: Optional[str] = None
    complexity: Optional[str] = None
    effort_estimate: Optional[Decimal] = None
    planned_start_date: Optional[date] = None
    planned_end_date: Optional[date] = None
    actual_start_date: Optional[date] = None
    actual_end_date: Optional[date] = None
    percent_complete: Optional[Decimal] = None

class FeatureResponse(FeatureBase):
    id: int
    project_id: int
    is_active: bool = True
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    created_by: Optional[str] = None
    updated_by: Optional[str] = None

    class Config:
        from_attributes = True

# ==================== BACKLOG SCHEMAS ====================

class BacklogBase(BaseModel):
    backlog_id: str
    name: str
    description: Optional[str] = None
    priority_id: Optional[int] = None
    status_id: Optional[int] = None
    business_value: Optional[str] = None
    user_story: Optional[str] = None
    acceptance_criteria: Optional[str] = None
    complexity: Optional[str] = None
    effort_estimate: Optional[Decimal] = None
    target_quarter: Optional[str] = None
    planned_start_date: Optional[date] = None
    planned_end_date: Optional[date] = None

class BacklogCreate(BacklogBase):
    pass

class BacklogUpdate(BaseModel):
    backlog_id: Optional[str] = None
    name: Optional[str] = None
    description: Optional[str] = None
    priority_id: Optional[int] = None
    status_id: Optional[int] = None
    business_value: Optional[str] = None
    user_story: Optional[str] = None
    acceptance_criteria: Optional[str] = None
    complexity: Optional[str] = None
    effort_estimate: Optional[Decimal] = None
    target_quarter: Optional[str] = None
    planned_start_date: Optional[date] = None
    planned_end_date: Optional[date] = None

class BacklogResponse(BacklogBase):
    id: int
    is_active: bool = True
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    created_by: Optional[str] = None
    updated_by: Optional[str] = None

    class Config:
        from_attributes = True


# ==================== RISK SCHEMAS ====================

class RiskBase(BaseModel):
    project_id: int
    risk_name: str
    description: Optional[str] = None
    risk_level: Optional[str] = None
    probability: Optional[Decimal] = None
    impact: Optional[Decimal] = None
    risk_score: Optional[Decimal] = None
    mitigation_plan: Optional[str] = None
    mitigation_owner: Optional[str] = None
    mitigation_due_date: Optional[date] = None
    status: Optional[str] = None

class RiskCreate(RiskBase):
    pass

class RiskUpdate(BaseModel):
    project_id: Optional[int] = None
    risk_name: Optional[str] = None
    description: Optional[str] = None
    risk_level: Optional[str] = None
    probability: Optional[Decimal] = None
    impact: Optional[Decimal] = None
    risk_score: Optional[Decimal] = None
    mitigation_plan: Optional[str] = None
    mitigation_owner: Optional[str] = None
    mitigation_due_date: Optional[date] = None
    status: Optional[str] = None

class RiskResponse(RiskBase):
    id: int
    is_active: bool = True
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    created_by: Optional[str] = None
    updated_by: Optional[str] = None

    class Config:
        from_attributes = True

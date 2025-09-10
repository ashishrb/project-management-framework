"""
Pydantic schemas for resource management
"""
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime

# ==================== RESOURCE SCHEMAS ====================

class ResourceBase(BaseModel):
    name: str
    email: str
    role: Optional[str] = None
    skills: Optional[List[str]] = None
    experience_level: Optional[str] = None
    availability_percentage: Optional[float] = 100.0

class ResourceCreate(ResourceBase):
    pass

class ResourceUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    role: Optional[str] = None
    skills: Optional[List[str]] = None
    experience_level: Optional[str] = None
    availability_percentage: Optional[float] = None

class ResourceResponse(ResourceBase):
    id: int
    is_active: bool = True
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    created_by: Optional[str] = None
    updated_by: Optional[str] = None

    class Config:
        from_attributes = True

# ==================== ALLOCATION SCHEMAS ====================

class ResourceAllocation(BaseModel):
    """Resource allocation information"""
    id: int
    type: str  # "project" or "task"
    entity_id: int
    entity_name: str
    allocation_percentage: int
    role: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    estimated_hours: Optional[int] = None
    actual_hours: Optional[int] = None

class ProjectAllocation(BaseModel):
    """Project allocation details"""
    project_id: int
    project_name: str
    allocation_percentage: int
    role_in_project: str
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None

class TaskAllocation(BaseModel):
    """Task allocation details"""
    task_id: int
    task_name: str
    allocation_percentage: int
    estimated_hours: Optional[int] = None
    actual_hours: Optional[int] = None

# ==================== ANALYTICS SCHEMAS ====================

class ResourceAvailability(BaseModel):
    """Resource availability analytics"""
    resource_id: int
    resource_name: str
    role: str
    total_allocation: int
    available_percentage: float
    is_available: bool

class ResourceWorkload(BaseModel):
    """Resource workload analytics"""
    resource_id: int
    resource_name: str
    role: str
    project_count: int
    task_count: int
    total_estimated_hours: int
    total_actual_hours: int
    utilization_rate: float

class ResourceSkills(BaseModel):
    """Resource skills information"""
    resource_id: int
    resource_name: str
    skills: List[str]
    experience_level: str
    skill_categories: Dict[str, List[str]]

# ==================== CAPACITY PLANNING ====================

class CapacityPlan(BaseModel):
    """Resource capacity planning"""
    resource_id: int
    resource_name: str
    current_capacity: int
    planned_capacity: int
    available_capacity: int
    utilization_rate: float
    recommendations: List[str]

class ResourceDemand(BaseModel):
    """Resource demand analysis"""
    skill: str
    required_count: int
    available_count: int
    shortage: int
    surplus: int
    priority: str

class ResourceForecast(BaseModel):
    """Resource forecasting"""
    period: str
    total_demand: int
    total_supply: int
    gap: int
    recommendations: List[str]

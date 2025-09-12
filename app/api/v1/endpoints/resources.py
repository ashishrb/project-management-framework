"""
Resources API endpoints for GenAI Metrics Dashboard
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import and_
import asyncio

from app.database import get_db
from app.api.deps import get_current_user
from app.models.main_tables import Resource, Project, Task
from app.models.junction_tables import ProjectResource, TaskResource
from app.schemas.resource_schemas import (
    ResourceResponse, ResourceCreate, ResourceUpdate,
    ResourceAllocation, ProjectAllocation, TaskAllocation
)
from app.websocket.connection_manager import connection_manager

router = APIRouter()

# ==================== RESOURCES ====================

@router.get("", response_model=List[ResourceResponse])
@router.get("/", response_model=List[ResourceResponse])
def get_resources(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    role: Optional[str] = None,
    is_active: bool = True,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get all resources with filtering"""
    query = db.query(Resource)
    
    if role:
        query = query.filter(Resource.role == role)
    if is_active is not None:
        query = query.filter(Resource.is_active == is_active)
    
    resources = query.offset(skip).limit(limit).all()
    return resources

@router.get("/{resource_id}", response_model=ResourceResponse)
def get_resource(
    resource_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get a specific resource by ID"""
    resource = db.query(Resource).filter(Resource.id == resource_id).first()
    if not resource:
        raise HTTPException(status_code=404, detail="Resource not found")
    return resource

@router.post("/", response_model=ResourceResponse)
def create_resource(
    resource: ResourceCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Create a new resource"""
    db_resource = Resource(**resource.model_dump())
    db.add(db_resource)
    db.commit()
    db.refresh(db_resource)
    # WebSocket notify
    try:
        message = {"type": "resource_created", "resource_id": db_resource.id, "name": db_resource.name}
        connection_manager.queue_message(message, room="resources")
        asyncio.get_event_loop().create_task(connection_manager.broadcast_to_room(message, room="resources"))
    except Exception:
        pass
    return db_resource

@router.put("/{resource_id}", response_model=ResourceResponse)
def update_resource(
    resource_id: int,
    resource: ResourceUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Update a resource"""
    db_resource = db.query(Resource).filter(Resource.id == resource_id).first()
    if not db_resource:
        raise HTTPException(status_code=404, detail="Resource not found")
    
    for field, value in resource.model_dump(exclude_unset=True).items():
        setattr(db_resource, field, value)
    
    db.commit()
    db.refresh(db_resource)
    # WebSocket notify
    try:
        message = {"type": "resource_updated", "resource_id": db_resource.id, "name": db_resource.name}
        connection_manager.queue_message(message, room="resources")
        asyncio.get_event_loop().create_task(connection_manager.broadcast_to_room(message, room="resources"))
    except Exception:
        pass
    return db_resource

@router.delete("/{resource_id}")
def delete_resource(
    resource_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Delete a resource (soft delete)"""
    db_resource = db.query(Resource).filter(Resource.id == resource_id).first()
    if not db_resource:
        raise HTTPException(status_code=404, detail="Resource not found")
    
    db_resource.is_active = False
    db.commit()
    # WebSocket notify
    try:
        message = {"type": "resource_deleted", "resource_id": db_resource.id}
        connection_manager.queue_message(message, room="resources")
        asyncio.get_event_loop().create_task(connection_manager.broadcast_to_room(message, room="resources"))
    except Exception:
        pass
    return {"message": "Resource deleted successfully"}

# ==================== RESOURCE ALLOCATIONS ====================

@router.get("/{resource_id}/allocations", response_model=List[ResourceAllocation])
def get_resource_allocations(
    resource_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get all allocations for a resource"""
    # Get project allocations
    project_allocations = db.query(ProjectResource).filter(
        ProjectResource.resource_id == resource_id
    ).all()
    
    # Get task allocations
    task_allocations = db.query(TaskResource).filter(
        TaskResource.resource_id == resource_id
    ).all()
    
    allocations = []
    
    # Add project allocations
    for allocation in project_allocations:
        project = db.query(Project).filter(Project.id == allocation.project_id).first()
        if project:
            allocations.append(ResourceAllocation(
                id=allocation.id,
                type="project",
                entity_id=allocation.project_id,
                entity_name=project.name,
                allocation_percentage=allocation.allocation_percentage,
                role=allocation.role_in_project,
                start_date=allocation.start_date,
                end_date=allocation.end_date
            ))
    
    # Add task allocations
    for allocation in task_allocations:
        task = db.query(Task).filter(Task.id == allocation.task_id).first()
        if task:
            allocations.append(ResourceAllocation(
                id=allocation.id,
                type="task",
                entity_id=allocation.task_id,
                entity_name=task.task_name,
                allocation_percentage=allocation.allocation_percentage,
                estimated_hours=allocation.estimated_hours,
                actual_hours=allocation.actual_hours
            ))
    
    return allocations

@router.post("/{resource_id}/projects/{project_id}/allocate")
def allocate_resource_to_project(
    resource_id: int,
    project_id: int,
    allocation_percentage: int = Query(..., ge=1, le=100),
    role_in_project: str = "Team Member",
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Allocate a resource to a project"""
    # Verify resource exists
    resource = db.query(Resource).filter(Resource.id == resource_id).first()
    if not resource:
        raise HTTPException(status_code=404, detail="Resource not found")
    
    # Verify project exists
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # Check if allocation already exists
    existing_allocation = db.query(ProjectResource).filter(
        and_(
            ProjectResource.resource_id == resource_id,
            ProjectResource.project_id == project_id
        )
    ).first()
    
    if existing_allocation:
        raise HTTPException(status_code=400, detail="Resource already allocated to this project")
    
    # Create new allocation
    allocation = ProjectResource(
        resource_id=resource_id,
        project_id=project_id,
        allocation_percentage=allocation_percentage,
        role_in_project=role_in_project
    )
    
    db.add(allocation)
    db.commit()
    
    return {"message": "Resource allocated to project successfully"}

@router.post("/{resource_id}/tasks/{task_id}/allocate")
def allocate_resource_to_task(
    resource_id: int,
    task_id: int,
    allocation_percentage: int = Query(..., ge=1, le=100),
    estimated_hours: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Allocate a resource to a task"""
    # Verify resource exists
    resource = db.query(Resource).filter(Resource.id == resource_id).first()
    if not resource:
        raise HTTPException(status_code=404, detail="Resource not found")
    
    # Verify task exists
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    # Check if allocation already exists
    existing_allocation = db.query(TaskResource).filter(
        and_(
            TaskResource.resource_id == resource_id,
            TaskResource.task_id == task_id
        )
    ).first()
    
    if existing_allocation:
        raise HTTPException(status_code=400, detail="Resource already allocated to this task")
    
    # Create new allocation
    allocation = TaskResource(
        resource_id=resource_id,
        task_id=task_id,
        allocation_percentage=allocation_percentage,
        estimated_hours=estimated_hours
    )
    
    db.add(allocation)
    db.commit()
    
    return {"message": "Resource allocated to task successfully"}

@router.delete("/{resource_id}/projects/{project_id}/deallocate")
def deallocate_resource_from_project(
    resource_id: int,
    project_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Deallocate a resource from a project"""
    allocation = db.query(ProjectResource).filter(
        and_(
            ProjectResource.resource_id == resource_id,
            ProjectResource.project_id == project_id
        )
    ).first()
    
    if not allocation:
        raise HTTPException(status_code=404, detail="Allocation not found")
    
    db.delete(allocation)
    db.commit()
    
    return {"message": "Resource deallocated from project successfully"}

@router.delete("/{resource_id}/tasks/{task_id}/deallocate")
def deallocate_resource_from_task(
    resource_id: int,
    task_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Deallocate a resource from a task"""
    allocation = db.query(TaskResource).filter(
        and_(
            TaskResource.resource_id == resource_id,
            TaskResource.task_id == task_id
        )
    ).first()
    
    if not allocation:
        raise HTTPException(status_code=404, detail="Allocation not found")
    
    db.delete(allocation)
    db.commit()
    
    return {"message": "Resource deallocated from task successfully"}

# ==================== RESOURCE ANALYTICS ====================

@router.get("/analytics/availability")
def get_resource_availability(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get resource availability analytics"""
    resources = db.query(Resource).filter(Resource.is_active == True).all()
    
    availability_data = []
    for resource in resources:
        # Calculate current allocation percentage
        project_allocations = db.query(ProjectResource).filter(
            ProjectResource.resource_id == resource.id
        ).all()
        
        total_allocation = sum(alloc.allocation_percentage for alloc in project_allocations)
        available_percentage = 100 - total_allocation
        
        availability_data.append({
            "resource_id": resource.id,
            "resource_name": resource.name,
            "role": resource.role,
            "total_allocation": total_allocation,
            "available_percentage": available_percentage,
            "is_available": available_percentage > 0
        })
    
    return availability_data

@router.get("/analytics/workload")
def get_resource_workload(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get resource workload analytics"""
    resources = db.query(Resource).filter(Resource.is_active == True).all()
    
    workload_data = []
    for resource in resources:
        # Get project workload
        project_allocations = db.query(ProjectResource).filter(
            ProjectResource.resource_id == resource.id
        ).all()
        
        # Get task workload
        task_allocations = db.query(TaskResource).filter(
            TaskResource.resource_id == resource.id
        ).all()
        
        total_estimated_hours = sum(
            alloc.estimated_hours or 0 for alloc in task_allocations
        )
        total_actual_hours = sum(
            alloc.actual_hours or 0 for alloc in task_allocations
        )
        
        workload_data.append({
            "resource_id": resource.id,
            "resource_name": resource.name,
            "role": resource.role,
            "project_count": len(project_allocations),
            "task_count": len(task_allocations),
            "total_estimated_hours": total_estimated_hours,
            "total_actual_hours": total_actual_hours,
            "utilization_rate": round((total_actual_hours / max(total_estimated_hours, 1)) * 100, 2)
        })
    
    return workload_data

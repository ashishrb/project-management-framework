"""
Project Management API endpoints
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_

from app.database import get_db
from app.api.deps import get_current_user
from app.models.main_tables import Project, Task, Feature, Backlog
from app.models.lookup_tables import Status, Priority, ProjectType, Portfolio
from app.schemas.project_schemas import (
    ProjectResponse, ProjectCreate, ProjectUpdate,
    TaskResponse, TaskCreate, TaskUpdate,
    FeatureResponse, FeatureCreate, FeatureUpdate,
    BacklogResponse, BacklogCreate, BacklogUpdate
)

router = APIRouter()

# ==================== PROJECTS ====================

@router.get("/", response_model=List[ProjectResponse])
def get_projects(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    status_id: Optional[int] = None,
    portfolio_id: Optional[int] = None,
    project_type_id: Optional[int] = None,
    search: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get all projects with filtering and pagination"""
    query = db.query(Project)
    
    # Apply filters
    if status_id:
        query = query.filter(Project.status_id == status_id)
    if portfolio_id:
        query = query.filter(Project.portfolio_id == portfolio_id)
    if project_type_id:
        query = query.filter(Project.project_type_id == project_type_id)
    if search:
        query = query.filter(
            or_(
                Project.name.ilike(f"%{search}%"),
                Project.description.ilike(f"%{search}%")
            )
        )
    
    projects = query.offset(skip).limit(limit).all()
    return projects

@router.get("/current", response_model=List[ProjectResponse])
def get_current_projects(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get current active projects (2 projects as per wire diagram)"""
    # Get projects with "Active" status
    active_status = db.query(Status).filter(Status.name == "Active").first()
    if not active_status:
        return []
    
    projects = db.query(Project).filter(
        and_(
            Project.status_id == active_status.id,
            Project.is_active == True
        )
    ).limit(2).all()
    
    return projects

@router.get("/approved", response_model=List[ProjectResponse])
def get_approved_projects(
    skip: int = Query(0, ge=0),
    limit: int = Query(93, ge=1, le=100),  # 93 projects as per wire diagram
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get approved projects (93 projects as per wire diagram)"""
    # Get projects with "Execution" status classification
    execution_status = db.query(Status).filter(Status.name == "Active").first()
    if not execution_status:
        return []
    
    projects = db.query(Project).filter(
        and_(
            Project.status_id == execution_status.id,
            Project.is_active == True
        )
    ).offset(skip).limit(limit).all()
    
    return projects

@router.get("/backlog", response_model=List[ProjectResponse])
def get_backlog_projects(
    skip: int = Query(0, ge=0),
    limit: int = Query(45, ge=1, le=100),  # 45+ projects as per wire diagram
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get backlog projects (45+ projects as per wire diagram)"""
    # Get projects with "Planning" status classification
    planning_status = db.query(Status).filter(Status.name == "Active").first()
    if not planning_status:
        return []
    
    projects = db.query(Project).filter(
        and_(
            Project.status_id == planning_status.id,
            Project.is_active == True
        )
    ).offset(skip).limit(limit).all()
    
    return projects

@router.get("/{project_id}", response_model=ProjectResponse)
def get_project(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get a specific project by ID"""
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project

@router.post("/", response_model=ProjectResponse)
def create_project(
    project: ProjectCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Create a new project"""
    db_project = Project(**project.model_dump())
    db.add(db_project)
    db.commit()
    db.refresh(db_project)
    return db_project

@router.put("/{project_id}", response_model=ProjectResponse)
def update_project(
    project_id: int,
    project: ProjectUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Update a project"""
    db_project = db.query(Project).filter(Project.id == project_id).first()
    if not db_project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    for field, value in project.model_dump(exclude_unset=True).items():
        setattr(db_project, field, value)
    
    db.commit()
    db.refresh(db_project)
    return db_project

@router.delete("/{project_id}")
def delete_project(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Delete a project (soft delete)"""
    db_project = db.query(Project).filter(Project.id == project_id).first()
    if not db_project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    db_project.is_active = False
    db.commit()
    return {"message": "Project deleted successfully"}

# ==================== TASKS ====================

@router.get("/{project_id}/tasks", response_model=List[TaskResponse])
def get_project_tasks(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get all tasks for a project"""
    tasks = db.query(Task).filter(
        and_(
            Task.project_id == project_id,
            Task.is_active == True
        )
    ).all()
    return tasks

@router.post("/{project_id}/tasks", response_model=TaskResponse)
def create_task(
    project_id: int,
    task: TaskCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Create a new task for a project"""
    # Verify project exists
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    task_data = task.model_dump()
    task_data["project_id"] = project_id
    db_task = Task(**task_data)
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    return db_task

# ==================== FEATURES ====================

@router.get("/{project_id}/features", response_model=List[FeatureResponse])
def get_project_features(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get all features for a project"""
    features = db.query(Feature).filter(
        and_(
            Feature.project_id == project_id,
            Feature.is_active == True
        )
    ).all()
    return features

@router.post("/{project_id}/features", response_model=FeatureResponse)
def create_feature(
    project_id: int,
    feature: FeatureCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Create a new feature for a project"""
    # Verify project exists
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    feature_data = feature.model_dump()
    feature_data["project_id"] = project_id
    db_feature = Feature(**feature_data)
    db.add(db_feature)
    db.commit()
    db.refresh(db_feature)
    return db_feature

# ==================== BACKLOGS ====================

@router.get("/backlog/items", response_model=List[BacklogResponse])
def get_backlog_items(
    skip: int = Query(0, ge=0),
    limit: int = Query(216, ge=1, le=1000),  # 216+ items as per wire diagram
    priority_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get all backlog items with filtering"""
    query = db.query(Backlog).filter(Backlog.is_active == True)
    
    if priority_id:
        query = query.filter(Backlog.priority_id == priority_id)
    
    backlogs = query.offset(skip).limit(limit).all()
    return backlogs

@router.post("/backlog/items", response_model=BacklogResponse)
def create_backlog_item(
    backlog: BacklogCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Create a new backlog item"""
    db_backlog = Backlog(**backlog.model_dump())
    db.add(db_backlog)
    db.commit()
    db.refresh(db_backlog)
    return db_backlog

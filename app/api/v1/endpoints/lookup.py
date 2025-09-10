"""
Lookup API endpoints for GenAI Metrics Dashboard
"""
from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.api.deps import get_current_user
from app.models.lookup_tables import (
    Function, Platform, Priority, Status, Portfolio, Application,
    InvestmentType, JourneyMap, ProjectType, ProjectStatusClassification,
    ProjectPriorityClassification, ProjectCriticalityLevel
)
from app.schemas.lookup_schemas import (
    Function as FunctionSchema, Platform as PlatformSchema,
    Priority as PrioritySchema, Status as StatusSchema
)

router = APIRouter()

# ==================== FUNCTIONS ====================

@router.get("/functions", response_model=List[FunctionSchema])
def get_functions(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get all functions (17 items)"""
    return db.query(Function).filter(Function.is_active == True).all()

# ==================== PLATFORMS ====================

@router.get("/platforms", response_model=List[PlatformSchema])
def get_platforms(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get all platforms (9 items)"""
    return db.query(Platform).filter(Platform.is_active == True).all()

# ==================== PRIORITIES ====================

@router.get("/priorities", response_model=List[PrioritySchema])
def get_priorities(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get all priorities (6 levels)"""
    return db.query(Priority).filter(Priority.is_active == True).order_by(Priority.level).all()

# ==================== STATUSES ====================

@router.get("/statuses", response_model=List[StatusSchema])
def get_statuses(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get all statuses (4 types)"""
    return db.query(Status).filter(Status.is_active == True).all()

# ==================== PORTFOLIOS ====================

@router.get("/portfolios")
def get_portfolios(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get all portfolios (L1/L2 hierarchy)"""
    portfolios = db.query(Portfolio).filter(Portfolio.is_active == True).all()
    
    # Format as hierarchical structure
    result = []
    for portfolio in portfolios:
        result.append({
            "id": portfolio.id,
            "name": portfolio.name,
            "level": portfolio.level,
            "parent_id": portfolio.parent_id,
            "description": portfolio.description
        })
    
    return result

# ==================== APPLICATIONS ====================

@router.get("/applications")
def get_applications(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get all applications (SOX/Non-SOX classification)"""
    applications = db.query(Application).filter(Application.is_active == True).all()
    
    result = []
    for app in applications:
        result.append({
            "id": app.id,
            "name": app.name,
            "sox_classification": app.sox_classification,
            "description": app.description
        })
    
    return result

# ==================== INVESTMENT TYPES ====================

@router.get("/investment-types")
def get_investment_types(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get all investment types"""
    investment_types = db.query(InvestmentType).filter(InvestmentType.is_active == True).all()
    
    result = []
    for inv_type in investment_types:
        result.append({
            "id": inv_type.id,
            "name": inv_type.name,
            "description": inv_type.description
        })
    
    return result

# ==================== JOURNEY MAPS ====================

@router.get("/journey-maps")
def get_journey_maps(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get all journey maps"""
    journey_maps = db.query(JourneyMap).filter(JourneyMap.is_active == True).all()
    
    result = []
    for journey in journey_maps:
        result.append({
            "id": journey.id,
            "name": journey.name,
            "description": journey.description
        })
    
    return result

# ==================== PROJECT TYPES ====================

@router.get("/project-types")
def get_project_types(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get all project types (4 types)"""
    project_types = db.query(ProjectType).filter(ProjectType.is_active == True).all()
    
    result = []
    for proj_type in project_types:
        result.append({
            "id": proj_type.id,
            "name": proj_type.name,
            "description": proj_type.description
        })
    
    return result

# ==================== PROJECT STATUS CLASSIFICATIONS ====================

@router.get("/project-status-classifications")
def get_project_status_classifications(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get all project status classifications"""
    classifications = db.query(ProjectStatusClassification).filter(
        ProjectStatusClassification.is_active == True
    ).all()
    
    result = []
    for classification in classifications:
        result.append({
            "id": classification.id,
            "name": classification.name,
            "description": classification.description
        })
    
    return result

# ==================== PROJECT PRIORITY CLASSIFICATIONS ====================

@router.get("/project-priority-classifications")
def get_project_priority_classifications(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get all project priority classifications"""
    classifications = db.query(ProjectPriorityClassification).filter(
        ProjectPriorityClassification.is_active == True
    ).all()
    
    result = []
    for classification in classifications:
        result.append({
            "id": classification.id,
            "name": classification.name,
            "description": classification.description
        })
    
    return result

# ==================== PROJECT CRITICALITY LEVELS ====================

@router.get("/project-criticality-levels")
def get_project_criticality_levels(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get all project criticality levels"""
    criticality_levels = db.query(ProjectCriticalityLevel).filter(
        ProjectCriticalityLevel.is_active == True
    ).order_by(ProjectCriticalityLevel.level).all()
    
    result = []
    for level in criticality_levels:
        result.append({
            "id": level.id,
            "name": level.name,
            "level": level.level,
            "description": level.description,
            "color_code": level.color_code
        })
    
    return result

# ==================== COMBINED LOOKUP ====================

@router.get("/all")
def get_all_lookup_data(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get all lookup data in a single response"""
    return {
        "functions": [{"id": f.id, "name": f.name} for f in db.query(Function).filter(Function.is_active == True).all()],
        "platforms": [{"id": p.id, "name": p.name} for p in db.query(Platform).filter(Platform.is_active == True).all()],
        "priorities": [{"id": p.id, "name": p.name, "level": p.level, "color_code": p.color_code} for p in db.query(Priority).filter(Priority.is_active == True).order_by(Priority.level).all()],
        "statuses": [{"id": s.id, "name": s.name, "color_code": s.color_code} for s in db.query(Status).filter(Status.is_active == True).all()],
        "portfolios": [{"id": p.id, "name": p.name, "level": p.level, "parent_id": p.parent_id} for p in db.query(Portfolio).filter(Portfolio.is_active == True).all()],
        "applications": [{"id": a.id, "name": a.name, "sox_classification": a.sox_classification} for a in db.query(Application).filter(Application.is_active == True).all()],
        "investment_types": [{"id": i.id, "name": i.name} for i in db.query(InvestmentType).filter(InvestmentType.is_active == True).all()],
        "project_types": [{"id": pt.id, "name": pt.name} for pt in db.query(ProjectType).filter(ProjectType.is_active == True).all()],
        "criticality_levels": [{"id": cl.id, "name": cl.name, "level": cl.level, "color_code": cl.color_code} for cl in db.query(ProjectCriticalityLevel).filter(ProjectCriticalityLevel.is_active == True).order_by(ProjectCriticalityLevel.level).all()]
    }

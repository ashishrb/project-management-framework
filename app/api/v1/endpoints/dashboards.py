"""
Dashboard API endpoints for GenAI Metrics Dashboard
"""
from typing import List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_

from app.database import get_db
from app.api.deps import get_current_user
from app.models.main_tables import Project, Feature, Backlog
from app.models.lookup_tables import Function, Platform, Status, Priority
from app.schemas.dashboard_schemas import (
    DashboardMetrics, AllProjectsDashboard, PortfolioDashboard,
    GenAIMetrics, FunctionMetrics, PlatformMetrics
)
from app.core.logging import get_logger, log_api_endpoint

# Initialize logger
logger = get_logger("api.dashboards")

router = APIRouter()

@router.get("/all-projects", response_model=AllProjectsDashboard)
@log_api_endpoint("api.dashboards")
def get_all_projects_dashboard(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get All Projects Dashboard with 4-panel GenAI metrics"""
    
    # Get basic project counts
    current_projects = db.query(Project).filter(
        and_(
            Project.is_active == True,
            Project.status_id == 1  # Active status
        )
    ).count()
    
    approved_projects = db.query(Project).filter(
        and_(
            Project.is_active == True,
            Project.status_id == 1  # Active status
        )
    ).count()
    
    backlog_projects = db.query(Backlog).filter(
        Backlog.is_active == True
    ).count()
    
    total_projects = current_projects + approved_projects + backlog_projects
    
    # Get GenAI 4-panel metrics
    genai_metrics = get_genai_metrics(db)
    
    return AllProjectsDashboard(
        current_projects=current_projects,
        approved_projects=approved_projects,
        backlog_projects=backlog_projects,
        total_projects=total_projects,
        genai_metrics=genai_metrics
    )

@router.get("/portfolio/{portfolio_id}", response_model=PortfolioDashboard)
def get_portfolio_dashboard(
    portfolio_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get Portfolio Dashboard with portfolio-specific metrics"""
    
    # Get portfolio-specific project counts
    total_projects = db.query(Project).filter(
        and_(
            Project.portfolio_id == portfolio_id,
            Project.is_active == True
        )
    ).count()
    
    active_projects = db.query(Project).filter(
        and_(
            Project.portfolio_id == portfolio_id,
            Project.is_active == True,
            Project.status_id == 1  # Active status
        )
    ).count()
    
    completed_projects = db.query(Project).filter(
        and_(
            Project.portfolio_id == portfolio_id,
            Project.is_active == True,
            Project.status_id == 2  # Completed status
        )
    ).count()
    
    # Calculate budget utilization (placeholder)
    budget_utilization = 78.0  # This would be calculated from actual budget data
    
    # Get portfolio-specific GenAI metrics
    genai_metrics = get_genai_metrics(db, portfolio_id=portfolio_id)
    
    return PortfolioDashboard(
        total_projects=total_projects,
        active_projects=active_projects,
        completed_projects=completed_projects,
        budget_utilization=budget_utilization,
        genai_metrics=genai_metrics
    )

@router.get("/genai-metrics", response_model=GenAIMetrics)
def get_genai_metrics_endpoint(
    portfolio_id: int = None,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get GenAI 4-panel metrics"""
    return get_genai_metrics(db, portfolio_id)

def get_genai_metrics(db: Session, portfolio_id: int = None) -> GenAIMetrics:
    """Calculate GenAI 4-panel metrics"""
    
    # Base query for projects
    base_query = db.query(Project).filter(Project.is_active == True)
    if portfolio_id:
        base_query = base_query.filter(Project.portfolio_id == portfolio_id)
    
    # Panel 1: Active Features by Function & Status
    function_metrics = get_function_metrics(db, base_query)
    
    # Panel 2: Backlogs by Function & Priority
    backlog_function_metrics = get_backlog_function_metrics(db, portfolio_id)
    
    # Panel 3: Active Features by Platform & Status
    platform_metrics = get_platform_metrics(db, base_query)
    
    # Panel 4: Backlogs by Platform & Priority
    backlog_platform_metrics = get_backlog_platform_metrics(db, portfolio_id)
    
    return GenAIMetrics(
        active_features_by_function=function_metrics,
        backlogs_by_function=backlog_function_metrics,
        active_features_by_platform=platform_metrics,
        backlogs_by_platform=backlog_platform_metrics
    )

def get_function_metrics(db: Session, base_query) -> List[FunctionMetrics]:
    """Get active features by function and status"""
    # This is a simplified version - in reality, you'd join with junction tables
    functions = db.query(Function).filter(Function.is_active == True).all()
    
    function_metrics = []
    for function in functions:
        # Get feature counts by status for this function
        completed_count = 111  # Placeholder - would be calculated from actual data
        on_track_count = 35
        at_risk_count = 124
        
        function_metrics.append(FunctionMetrics(
            function_id=function.id,
            function_name=function.name,
            completed=completed_count,
            on_track=on_track_count,
            at_risk=at_risk_count,
            off_track=0
        ))
    
    return function_metrics

def get_backlog_function_metrics(db: Session, portfolio_id: int = None) -> List[FunctionMetrics]:
    """Get backlogs by function and priority"""
    functions = db.query(Function).filter(Function.is_active == True).all()
    
    function_metrics = []
    for function in functions:
        # Get backlog counts by priority for this function
        highest_priority = 33  # Placeholder
        high_priority = 36
        medium_low_priority = 147
        
        function_metrics.append(FunctionMetrics(
            function_id=function.id,
            function_name=function.name,
            completed=0,  # Backlogs don't have completed status
            on_track=highest_priority,
            at_risk=high_priority,
            off_track=medium_low_priority
        ))
    
    return function_metrics

def get_platform_metrics(db: Session, base_query) -> List[PlatformMetrics]:
    """Get active features by platform and status"""
    platforms = db.query(Platform).filter(Platform.is_active == True).all()
    
    platform_metrics = []
    for platform in platforms:
        # Get feature counts by status for this platform
        completed_count = 111 if platform.name == "LC Platform" else 69 if platform.name == "Commercial" else 90
        on_track_count = 35
        at_risk_count = 124
        
        platform_metrics.append(PlatformMetrics(
            platform_id=platform.id,
            platform_name=platform.name,
            completed=completed_count,
            on_track=on_track_count,
            at_risk=at_risk_count,
            off_track=0
        ))
    
    return platform_metrics

def get_backlog_platform_metrics(db: Session, portfolio_id: int = None) -> List[PlatformMetrics]:
    """Get backlogs by platform and priority"""
    platforms = db.query(Platform).filter(Platform.is_active == True).all()
    
    platform_metrics = []
    for platform in platforms:
        # Get backlog counts by priority for this platform
        high_priority = 69 if platform.name == "LC Platform" else 32 if platform.name == "Commercial" else 115
        medium_priority = 32
        low_priority = 115
        
        platform_metrics.append(PlatformMetrics(
            platform_id=platform.id,
            platform_name=platform.name,
            completed=0,  # Backlogs don't have completed status
            on_track=high_priority,
            at_risk=medium_priority,
            off_track=low_priority
        ))
    
    return platform_metrics

@router.get("/summary-metrics", response_model=DashboardMetrics)
def get_dashboard_metrics(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get overall dashboard metrics summary"""
    
    # Get project counts by status
    active_projects = db.query(Project).filter(
        and_(
            Project.is_active == True,
            Project.status_id == 1  # Active
        )
    ).count()
    
    completed_projects = db.query(Project).filter(
        and_(
            Project.is_active == True,
            Project.status_id == 2  # Completed
        )
    ).count()
    
    at_risk_projects = db.query(Project).filter(
        and_(
            Project.is_active == True,
            Project.status_id == 3  # At Risk
        )
    ).count()
    
    off_track_projects = db.query(Project).filter(
        and_(
            Project.is_active == True,
            Project.status_id == 4  # Off Track
        )
    ).count()
    
    # Get feature counts
    total_features = db.query(Feature).filter(Feature.is_active == True).count()
    completed_features = db.query(Feature).filter(
        and_(
            Feature.is_active == True,
            Feature.status_id == 2  # Completed
        )
    ).count()
    
    # Get backlog counts
    total_backlogs = db.query(Backlog).filter(Backlog.is_active == True).count()
    
    return DashboardMetrics(
        total_projects=active_projects + completed_projects + at_risk_projects + off_track_projects,
        active_projects=active_projects,
        completed_projects=completed_projects,
        at_risk_projects=at_risk_projects,
        off_track_projects=off_track_projects,
        total_features=total_features,
        completed_features=completed_features,
        total_backlogs=total_backlogs,
        completion_rate=round((completed_projects / max(active_projects + completed_projects, 1)) * 100, 2)
    )

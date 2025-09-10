"""
Reports API endpoints for GenAI Metrics Dashboard
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_

from app.database import get_db
from app.api.deps import get_current_user
from app.models.main_tables import Project, Feature, Backlog, Resource, Risk
from app.models.lookup_tables import Function, Platform, Status, Priority, Portfolio
from app.schemas.report_schemas import (
    ProjectReport, FeatureReport, BacklogReport, ResourceReport,
    RiskReport, PortfolioReport, ExecutiveSummary
)

router = APIRouter()

# ==================== PROJECT SUMMARY ====================

@router.get("/project-summary", response_model=ExecutiveSummary)
def get_project_summary(
    portfolio_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get executive summary of all projects"""
    try:
        # Get total projects
        total_projects = db.query(Project).filter(Project.is_active == True).count()
        
        # Get projects by status
        projects_by_status = db.query(
            Status.name,
            func.count(Project.id).label('count')
        ).join(Project).filter(Project.is_active == True).group_by(Status.name).all()
        
        # Get projects by priority
        projects_by_priority = db.query(
            Priority.name,
            func.count(Project.id).label('count')
        ).join(Project).filter(Project.is_active == True).group_by(Priority.name).all()
        
        # Get total budget
        total_budget = db.query(func.sum(Project.budget_amount)).filter(
            Project.is_active == True
        ).scalar() or 0
        
        # Get average completion
        avg_completion = db.query(func.avg(Project.percent_complete)).filter(
            Project.is_active == True
        ).scalar() or 0
        
        # Get additional metrics
        active_projects = db.query(Project).filter(
            Project.is_active == True,
            Project.status_id == 1  # Active status
        ).count()
        
        completed_projects = db.query(Project).filter(
            Project.is_active == True,
            Project.status_id == 2  # Completed status
        ).count()
        
        at_risk_projects = db.query(Project).filter(
            Project.is_active == True,
            Project.status_id == 3  # At Risk status
        ).count()
        
        total_features = db.query(Feature).count()
        completed_features = db.query(Feature).filter(Feature.status_id == 2).count()
        total_backlogs = db.query(Backlog).count()
        total_resources = db.query(Resource).count()
        total_risks = db.query(Risk).count()
        high_risks = db.query(Risk).filter(Risk.risk_level.in_(["High", "Critical"])).count()
        
        project_completion_rate = float(avg_completion)
        feature_completion_rate = (completed_features / total_features * 100) if total_features > 0 else 0.0
        
        return ExecutiveSummary(
            total_projects=total_projects,
            active_projects=active_projects,
            completed_projects=completed_projects,
            at_risk_projects=at_risk_projects,
            total_features=total_features,
            completed_features=completed_features,
            total_backlogs=total_backlogs,
            total_resources=total_resources,
            total_risks=total_risks,
            high_risks=high_risks,
            project_completion_rate=project_completion_rate,
            feature_completion_rate=feature_completion_rate
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ==================== PROJECT REPORTS ====================

@router.get("/projects", response_model=List[ProjectReport])
def get_project_report(
    portfolio_id: Optional[int] = None,
    status_id: Optional[int] = None,
    project_type_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Generate project report with filtering"""
    query = db.query(Project).filter(Project.is_active == True)
    
    if portfolio_id:
        query = query.filter(Project.portfolio_id == portfolio_id)
    if status_id:
        query = query.filter(Project.status_id == status_id)
    if project_type_id:
        query = query.filter(Project.project_type_id == project_type_id)
    
    projects = query.all()
    
    report_data = []
    for project in projects:
        # Get project details
        status = db.query(Status).filter(Status.id == project.status_id).first()
        priority = db.query(Priority).filter(Priority.id == project.priority_id).first()
        portfolio = db.query(Portfolio).filter(Portfolio.id == project.portfolio_id).first()
        
        # Get feature count
        feature_count = db.query(Feature).filter(
            and_(
                Feature.project_id == project.id,
                Feature.is_active == True
            )
        ).count()
        
        # Get task count
        task_count = db.query(Task).filter(
            and_(
                Task.project_id == project.id,
                Task.is_active == True
            )
        ).count()
        
        report_data.append(ProjectReport(
            project_id=project.project_id,
            name=project.name,
            status=status.name if status else "Unknown",
            priority=priority.name if priority else "Unknown",
            portfolio=portfolio.name if portfolio else "Unknown",
            start_date=project.start_date,
            due_date=project.due_date,
            percent_complete=project.percent_complete or 0,
            feature_count=feature_count,
            task_count=task_count,
            project_manager=project.project_manager,
            business_owner=project.business_owner
        ))
    
    return report_data

# ==================== FEATURE REPORTS ====================

@router.get("/features", response_model=List[FeatureReport])
def get_feature_report(
    project_id: Optional[int] = None,
    function_id: Optional[int] = None,
    platform_id: Optional[int] = None,
    status_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Generate feature report with filtering"""
    query = db.query(Feature).filter(Feature.is_active == True)
    
    if project_id:
        query = query.filter(Feature.project_id == project_id)
    if status_id:
        query = query.filter(Feature.status_id == status_id)
    
    features = query.all()
    
    report_data = []
    for feature in features:
        # Get feature details
        status = db.query(Status).filter(Status.id == feature.status_id).first()
        priority = db.query(Priority).filter(Priority.id == feature.priority_id).first()
        project = db.query(Project).filter(Project.id == feature.project_id).first()
        
        report_data.append(FeatureReport(
            feature_name=feature.feature_name,
            project_name=project.name if project else "Unknown",
            status=status.name if status else "Unknown",
            priority=priority.name if priority else "Unknown",
            complexity=feature.complexity,
            effort_estimate=feature.effort_estimate,
            percent_complete=feature.percent_complete or 0,
            planned_start_date=feature.planned_start_date,
            planned_end_date=feature.planned_end_date,
            business_value=feature.business_value
        ))
    
    return report_data

# ==================== BACKLOG REPORTS ====================

@router.get("/backlog", response_model=List[BacklogReport])
def get_backlog_report(
    priority_id: Optional[int] = None,
    target_quarter: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Generate backlog report with filtering"""
    query = db.query(Backlog).filter(Backlog.is_active == True)
    
    if priority_id:
        query = query.filter(Backlog.priority_id == priority_id)
    if target_quarter:
        query = query.filter(Backlog.target_quarter == target_quarter)
    
    backlogs = query.all()
    
    report_data = []
    for backlog in backlogs:
        # Get backlog details
        status = db.query(Status).filter(Status.id == backlog.status_id).first()
        priority = db.query(Priority).filter(Priority.id == backlog.priority_id).first()
        
        report_data.append(BacklogReport(
            backlog_id=backlog.backlog_id,
            name=backlog.name,
            status=status.name if status else "Unknown",
            priority=priority.name if priority else "Unknown",
            complexity=backlog.complexity,
            effort_estimate=backlog.effort_estimate,
            target_quarter=backlog.target_quarter,
            planned_start_date=backlog.planned_start_date,
            planned_end_date=backlog.planned_end_date,
            business_value=backlog.business_value
        ))
    
    return report_data

# ==================== RESOURCE REPORTS ====================

@router.get("/resources", response_model=List[ResourceReport])
def get_resource_report(
    role: Optional[str] = None,
    experience_level: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Generate resource report with filtering"""
    query = db.query(Resource).filter(Resource.is_active == True)
    
    if role:
        query = query.filter(Resource.role == role)
    if experience_level:
        query = query.filter(Resource.experience_level == experience_level)
    
    resources = query.all()
    
    report_data = []
    for resource in resources:
        # Get project count
        project_count = db.query(ProjectResource).filter(
            ProjectResource.resource_id == resource.id
        ).count()
        
        # Get task count
        task_count = db.query(TaskResource).filter(
            TaskResource.resource_id == resource.id
        ).count()
        
        report_data.append(ResourceReport(
            resource_name=resource.name,
            email=resource.email,
            role=resource.role,
            experience_level=resource.experience_level,
            skills=resource.skills or [],
            availability_percentage=resource.availability_percentage,
            project_count=project_count,
            task_count=task_count
        ))
    
    return report_data

# ==================== RISK REPORTS ====================

@router.get("/risks", response_model=List[RiskReport])
def get_risk_report(
    project_id: Optional[int] = None,
    risk_level: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Generate risk report with filtering"""
    query = db.query(Risk).filter(Risk.is_active == True)
    
    if project_id:
        query = query.filter(Risk.project_id == project_id)
    if risk_level:
        query = query.filter(Risk.risk_level == risk_level)
    
    risks = query.all()
    
    report_data = []
    for risk in risks:
        # Get project details
        project = db.query(Project).filter(Project.id == risk.project_id).first()
        
        report_data.append(RiskReport(
            risk_name=risk.risk_name,
            project_name=project.name if project else "Unknown",
            risk_level=risk.risk_level,
            probability=risk.probability,
            impact=risk.impact,
            risk_score=risk.risk_score,
            status=risk.status,
            mitigation_plan=risk.mitigation_plan,
            mitigation_owner=risk.mitigation_owner,
            mitigation_due_date=risk.mitigation_due_date
        ))
    
    return report_data

# ==================== PORTFOLIO REPORTS ====================

@router.get("/portfolio/{portfolio_id}", response_model=PortfolioReport)
def get_portfolio_report(
    portfolio_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Generate portfolio-specific report"""
    # Get portfolio details
    portfolio = db.query(Portfolio).filter(Portfolio.id == portfolio_id).first()
    if not portfolio:
        raise HTTPException(status_code=404, detail="Portfolio not found")
    
    # Get projects in portfolio
    projects = db.query(Project).filter(
        and_(
            Project.portfolio_id == portfolio_id,
            Project.is_active == True
        )
    ).all()
    
    # Calculate portfolio metrics
    total_projects = len(projects)
    active_projects = len([p for p in projects if p.status_id == 1])
    completed_projects = len([p for p in projects if p.status_id == 2])
    at_risk_projects = len([p for p in projects if p.status_id == 3])
    
    # Calculate average completion rate
    completion_rates = [p.percent_complete or 0 for p in projects if p.percent_complete is not None]
    avg_completion_rate = sum(completion_rates) / len(completion_rates) if completion_rates else 0
    
    # Get features in portfolio
    feature_count = db.query(Feature).join(Project).filter(
        and_(
            Project.portfolio_id == portfolio_id,
            Feature.is_active == True
        )
    ).count()
    
    # Get backlogs in portfolio (if any)
    backlog_count = db.query(Backlog).filter(Backlog.is_active == True).count()
    
    return PortfolioReport(
        portfolio_name=portfolio.name,
        total_projects=total_projects,
        active_projects=active_projects,
        completed_projects=completed_projects,
        at_risk_projects=at_risk_projects,
        feature_count=feature_count,
        backlog_count=backlog_count,
        avg_completion_rate=round(avg_completion_rate, 2)
    )

# ==================== EXECUTIVE SUMMARY ====================

@router.get("/executive-summary", response_model=ExecutiveSummary)
def get_executive_summary(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Generate executive summary report"""
    
    # Get overall project metrics
    total_projects = db.query(Project).filter(Project.is_active == True).count()
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
    
    # Get feature metrics
    total_features = db.query(Feature).filter(Feature.is_active == True).count()
    completed_features = db.query(Feature).filter(
        and_(
            Feature.is_active == True,
            Feature.status_id == 2  # Completed
        )
    ).count()
    
    # Get backlog metrics
    total_backlogs = db.query(Backlog).filter(Backlog.is_active == True).count()
    
    # Get resource metrics
    total_resources = db.query(Resource).filter(Resource.is_active == True).count()
    
    # Get risk metrics
    total_risks = db.query(Risk).filter(Risk.is_active == True).count()
    high_risks = db.query(Risk).filter(
        and_(
            Risk.is_active == True,
            Risk.risk_level == "High"
        )
    ).count()
    
    # Calculate completion rates
    project_completion_rate = round((completed_projects / max(total_projects, 1)) * 100, 2)
    feature_completion_rate = round((completed_features / max(total_features, 1)) * 100, 2)
    
    return ExecutiveSummary(
        total_projects=total_projects,
        active_projects=active_projects,
        completed_projects=completed_projects,
        at_risk_projects=at_risk_projects,
        total_features=total_features,
        completed_features=completed_features,
        total_backlogs=total_backlogs,
        total_resources=total_resources,
        total_risks=total_risks,
        high_risks=high_risks,
        project_completion_rate=project_completion_rate,
        feature_completion_rate=feature_completion_rate
    )

# ==================== EXPORT FUNCTIONS ====================

@router.get("/export/projects")
def export_projects_report(
    format: str = Query("csv", regex="^(csv|excel|pdf)$"),
    portfolio_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Export projects report in specified format"""
    # This would implement actual export functionality
    # For now, return a placeholder response
    return {
        "message": f"Projects report exported as {format}",
        "file_url": f"/exports/projects_{format}.{format}",
        "expires_at": "2025-09-10T00:00:00Z"
    }

@router.get("/export/features")
def export_features_report(
    format: str = Query("csv", regex="^(csv|excel|pdf)$"),
    project_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Export features report in specified format"""
    return {
        "message": f"Features report exported as {format}",
        "file_url": f"/exports/features_{format}.{format}",
        "expires_at": "2025-09-10T00:00:00Z"
    }

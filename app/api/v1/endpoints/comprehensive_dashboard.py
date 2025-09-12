"""
Comprehensive Dashboard API endpoints
Matching the exact metrics and charts from the screenshot
"""
from typing import List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_

from app.database import get_db
from app.api.deps import get_current_user
from app.models.main_tables import Project
from app.models.lookup_tables import (
    BusinessUnit, InvestmentClass, BenefitCategory, 
    InvestmentType, Priority, Status
)
from app.core.logging import get_logger, log_api_endpoint

# Initialize logger
logger = get_logger("api.comprehensive_dashboard")

router = APIRouter()

@router.get("/comprehensive-dashboard")
def get_comprehensive_dashboard(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get comprehensive dashboard data matching the screenshot exactly"""
    
    # Get KPI metrics
    kpis = get_kpi_metrics(db)
    
    # Get chart data
    benefit_plans_by_category = get_benefit_plans_by_category(db)
    projects_planned_benefits_by_category = get_projects_planned_benefits_by_category(db)
    projects_by_business_unit = get_projects_by_business_unit(db)
    projects_by_investment_type = get_projects_by_investment_type(db)
    projects_by_investment_class = get_projects_by_investment_class(db)
    projects_by_priority = get_projects_by_priority(db)
    
    return {
        "kpis": kpis,
        "charts": {
            "benefit_plans_by_category": benefit_plans_by_category,
            "projects_planned_benefits_by_category": projects_planned_benefits_by_category,
            "projects_by_business_unit": projects_by_business_unit,
            "projects_by_investment_type": projects_by_investment_type,
            "projects_by_investment_class": projects_by_investment_class,
            "projects_by_priority": projects_by_priority
        }
    }

def get_kpi_metrics(db: Session) -> Dict[str, Any]:
    """Get KPI metrics matching the screenshot"""
    
    # Active Projects: 128
    active_projects = db.query(Project).filter(
        and_(
            Project.is_active == True,
            Project.status_id == 1  # Active status
        )
    ).count()
    
    # Financial metrics
    financial_data = db.query(Project).with_entities(
        func.sum(Project.planned_cost).label('planned_cost'),
        func.sum(Project.planned_benefits).label('planned_benefits'),
        func.sum(Project.estimate_at_completion).label('estimate_at_completion'),
        func.sum(Project.actual_cost).label('actual_cost'),
        func.sum(Project.actual_benefits).label('actual_benefits')
    ).filter(Project.is_active == True).first()
    
    return {
        "active_projects": active_projects,
        "planned_cost": float(financial_data.planned_cost or 0),
        "planned_benefits": float(financial_data.planned_benefits or 0),
        "estimate_at_completion": float(financial_data.estimate_at_completion or 0),
        "actual_cost": float(financial_data.actual_cost or 0),
        "actual_benefits": float(financial_data.actual_benefits or 0)
    }

def get_benefit_plans_by_category(db: Session) -> Dict[str, Any]:
    """Get benefit plans by category (donut chart)"""
    
    # Get benefit category counts
    benefit_counts = db.query(
        BenefitCategory.name,
        func.count(Project.id).label('count')
    ).join(Project, Project.benefit_category_id == BenefitCategory.id)\
     .filter(Project.is_active == True)\
     .group_by(BenefitCategory.name)\
     .all()
    
    # Format for donut chart
    labels = []
    data = []
    colors = [
        '#28a745', '#fd7e14', '#ffc107', '#6f42c1', '#17a2b8',
        '#dc3545', '#20c997', '#6c757d', '#e83e8c', '#fd7e14'
    ]
    
    for i, (name, count) in enumerate(benefit_counts):
        labels.append(name)
        data.append(count)
    
    return {
        "labels": labels,
        "data": data,
        "colors": colors[:len(labels)],
        "total": sum(data)
    }

def get_projects_planned_benefits_by_category(db: Session) -> Dict[str, Any]:
    """Get projects planned benefits by category (horizontal bar chart)"""
    
    # Get planned benefits by category
    benefits_data = db.query(
        BenefitCategory.name,
        func.sum(Project.planned_benefits).label('total_benefits')
    ).join(Project, Project.benefit_category_id == BenefitCategory.id)\
     .filter(Project.is_active == True)\
     .group_by(BenefitCategory.name)\
     .order_by(func.sum(Project.planned_benefits).desc())\
     .all()
    
    labels = []
    data = []
    colors = [
        '#28a745', '#fd7e14', '#ffc107', '#6f42c1', '#17a2b8',
        '#dc3545', '#20c997', '#6c757d', '#e83e8c', '#fd7e14'
    ]
    
    for i, (name, total_benefits) in enumerate(benefits_data):
        labels.append(name)
        data.append(float(total_benefits or 0))
    
    return {
        "labels": labels,
        "data": data,
        "colors": colors[:len(labels)]
    }

def get_projects_by_business_unit(db: Session) -> Dict[str, Any]:
    """Get projects by business unit (donut chart)"""
    
    # Get business unit counts
    bu_counts = db.query(
        BusinessUnit.name,
        func.count(Project.id).label('count')
    ).join(Project, Project.business_unit_id == BusinessUnit.id)\
     .filter(Project.is_active == True)\
     .group_by(BusinessUnit.name)\
     .all()
    
    labels = []
    data = []
    colors = [
        '#007bff', '#28a745', '#ffc107', '#fd7e14', '#6f42c1',
        '#17a2b8', '#dc3545'
    ]
    
    for i, (name, count) in enumerate(bu_counts):
        labels.append(name if name else "(empty)")
        data.append(count)
    
    return {
        "labels": labels,
        "data": data,
        "colors": colors[:len(labels)],
        "total": sum(data)
    }

def get_projects_by_investment_type(db: Session) -> Dict[str, Any]:
    """Get projects by investment type (donut chart)"""
    
    # Get investment type counts
    it_counts = db.query(
        InvestmentType.name,
        func.count(Project.id).label('count')
    ).join(Project, Project.investment_type_id == InvestmentType.id)\
     .filter(Project.is_active == True)\
     .group_by(InvestmentType.name)\
     .all()
    
    labels = []
    data = []
    colors = [
        '#007bff', '#28a745', '#6f42c1', '#dc3545'
    ]
    
    for i, (name, count) in enumerate(it_counts):
        labels.append(name)
        data.append(count)
    
    return {
        "labels": labels,
        "data": data,
        "colors": colors[:len(labels)],
        "total": sum(data)
    }

def get_projects_by_investment_class(db: Session) -> Dict[str, Any]:
    """Get projects by investment class (donut chart)"""
    
    # Get investment class counts
    ic_counts = db.query(
        InvestmentClass.name,
        func.count(Project.id).label('count')
    ).join(Project, Project.investment_class_id == InvestmentClass.id)\
     .filter(Project.is_active == True)\
     .group_by(InvestmentClass.name)\
     .all()
    
    labels = []
    data = []
    colors = [
        '#007bff', '#ffc107', '#28a745'
    ]
    
    for i, (name, count) in enumerate(ic_counts):
        labels.append(name if name else "(empty)")
        data.append(count)
    
    return {
        "labels": labels,
        "data": data,
        "colors": colors[:len(labels)],
        "total": sum(data)
    }

def get_projects_by_priority(db: Session) -> Dict[str, Any]:
    """Get projects by priority (horizontal bar chart)"""
    
    # Get priority counts
    priority_counts = db.query(
        Priority.name,
        func.count(Project.id).label('count')
    ).join(Project, Project.priority_id == Priority.id)\
     .filter(Project.is_active == True)\
     .group_by(Priority.name, Priority.level)\
     .order_by(Priority.level.desc())\
     .all()
    
    labels = []
    data = []
    colors = [
        '#17a2b8', '#dc3545', '#ffc107', '#fd7e14'
    ]
    
    for i, (name, count) in enumerate(priority_counts):
        labels.append(name)
        data.append(count)
    
    return {
        "labels": labels,
        "data": data,
        "colors": colors[:len(labels)]
    }

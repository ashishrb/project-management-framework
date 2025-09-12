"""
View routes for GenAI Metrics Dashboard
"""
from fastapi import APIRouter, Request, Depends, HTTPException
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
import os

from app.database import get_db
from app.api.deps import get_current_user
from app.middleware.csrf import csrf_protection

# Initialize templates
templates = Jinja2Templates(directory="templates")

# Create router
router = APIRouter()

@router.get("/", response_class=HTMLResponse)
async def home(request: Request, db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    """Home page view"""
    try:
        return templates.TemplateResponse("home.html", {
            "request": request,
            "user": current_user
        })
    except Exception as e:
        return HTMLResponse(f"<h1>Error loading home page: {str(e)}</h1>", status_code=500)

@router.get("/dashboard", response_class=HTMLResponse)
async def dashboard_page(request: Request, db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    """Dashboard page"""
    return templates.TemplateResponse("dashboard.html", {
        "request": request,
        "user": current_user
    })

@router.get("/comprehensive-dashboard", response_class=HTMLResponse)
async def comprehensive_dashboard_page(request: Request, db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    """Comprehensive Dashboard page matching the screenshot"""
    return templates.TemplateResponse("comprehensive_dashboard.html", {
        "request": request,
        "user": current_user
    })

@router.get("/projects", response_class=HTMLResponse)
async def projects_list(request: Request, db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    """Projects list view"""
    return templates.TemplateResponse("projects.html", {
        "request": request,
        "user": current_user
    })

@router.get("/work-plan", response_class=HTMLResponse)
async def work_plan_page(request: Request, db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    """Work Plan page with Gantt chart functionality"""
    return templates.TemplateResponse("work_plan.html", {
        "request": request,
        "user": current_user
    })

@router.get("/projects/{project_id}", response_class=HTMLResponse)
async def project_detail(request: Request, project_id: str, db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    """Comprehensive Project Detail view matching the screenshots"""
    from app.models.main_tables import Project
    from app.models.lookup_tables import Status, Priority
    
    # Fetch project data from database
    project = db.query(Project).filter(Project.project_id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # Get status, priority, project type, and portfolio names
    status = db.query(Status).filter(Status.id == project.status_id).first()
    priority = db.query(Priority).filter(Priority.id == project.priority_id).first()
    from app.models.lookup_tables import ProjectType, Portfolio
    project_type = db.query(ProjectType).filter(ProjectType.id == project.project_type_id).first()
    portfolio = db.query(Portfolio).filter(Portfolio.id == project.portfolio_id).first()
    
    # Get real lookup data from database
    from app.models.project_detail_lookups import (
        DemandCategory, ModernizationDomain, DigitizationCategory,
        DeliveryOrganization, ExpenseType, BusinessProcess,
        GenerativeAIImpact, ProjectPhase, ProjectState,
        NISTDomain, NISTMapping
    )
    from app.models.project_detail_models import (
        ProjectStakeholder, ProjectCharter, ProjectNIST, 
        ProjectLifecycle, ProjectDependency, ProjectApplication,
        ProjectBaseline, ProjectStatusDetail
    )
    
    lookup_data = {
        "demand_categories": db.query(DemandCategory).all(),
        "modernization_domains": db.query(ModernizationDomain).all(),
        "digitization_categories": db.query(DigitizationCategory).all(),
        "delivery_organizations": db.query(DeliveryOrganization).all(),
        "expense_types": db.query(ExpenseType).all(),
        "business_processes": db.query(BusinessProcess).all(),
        "generative_ai_impacts": db.query(GenerativeAIImpact).all(),
        "project_phases": db.query(ProjectPhase).all(),
        "project_states": db.query(ProjectState).all(),
        "nist_domains": db.query(NISTDomain).all(),
        "nist_mappings": db.query(NISTMapping).all(),
    }
    
    # Get comprehensive project detail data
    stakeholders = db.query(ProjectStakeholder).filter(ProjectStakeholder.project_id == project.id).all()
    charter = db.query(ProjectCharter).filter(ProjectCharter.project_id == project.id).first()
    nist_info = db.query(ProjectNIST).filter(ProjectNIST.project_id == project.id).first()
    lifecycle = db.query(ProjectLifecycle).filter(ProjectLifecycle.project_id == project.id).first()
    dependencies = db.query(ProjectDependency).filter(ProjectDependency.project_id == project.id).all()
    applications = db.query(ProjectApplication).filter(ProjectApplication.project_id == project.id).all()
    baseline = db.query(ProjectBaseline).filter(ProjectBaseline.project_id == project.id).first()
    status_detail = db.query(ProjectStatusDetail).filter(ProjectStatusDetail.project_id == project.id).first()
    
    # Template functions for badge classes
    def get_status_badge_class(status_name):
        if not status_name:
            return "status-active"
        status_map = {
            'active': 'status-active',
            'completed': 'status-completed', 
            'at-risk': 'status-at-risk',
            'off-track': 'status-off-track'
        }
        return status_map.get(status_name.lower(), 'status-active')
    
    def get_priority_badge_class(priority_name):
        if not priority_name:
            return "priority-medium"
        priority_map = {
            'critical': 'priority-critical',
            'high': 'priority-high',
            'medium': 'priority-medium',
            'low': 'priority-low'
        }
        return priority_map.get(priority_name.lower(), 'priority-medium')
    
    return templates.TemplateResponse("project_detail.html", {
        "request": request,
        "user": current_user,
        "project": project,
        "project_status": status.name if status else "Active",
        "project_priority": priority.name if priority else "Medium",
        "project_type_name": project_type.name if project_type else "N/A",
        "portfolio_name": portfolio.name if portfolio else "N/A",
        "stakeholders": stakeholders,
        "charter": charter,
        "nist_info": nist_info,
        "lifecycle": lifecycle,
        "dependencies": dependencies,
        "applications": applications,
        "baseline": baseline,
        "status_detail": status_detail,
        "lookup_data": lookup_data,
        "getStatusBadgeClass": get_status_badge_class,
        "getPriorityBadgeClass": get_priority_badge_class
    })

@router.get("/resources", response_class=HTMLResponse)
async def resources_list(request: Request, db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    """Resources list view"""
    return templates.TemplateResponse("resources.html", {
        "request": request,
        "user": current_user
    })

@router.get("/gantt", response_class=HTMLResponse)
async def gantt_chart(request: Request, db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    """Gantt chart view"""
    return templates.TemplateResponse("gantt_chart.html", {
        "request": request,
        "user": current_user
    })

@router.get("/dashboard/manager", response_class=HTMLResponse)
async def manager_dashboard(request: Request, current_user: dict = Depends(get_current_user)):
    if (current_user.get("role") or "").lower() not in ["admin", "owner", "manager"]:
        raise HTTPException(status_code=403, detail="Forbidden")
    return templates.TemplateResponse("generic.html", {
        "request": request,
        "user": current_user,
        "page_title": "Manager Dashboard"
    })

@router.get("/dashboard/portfolio", response_class=HTMLResponse)
async def portfolio_dashboard(request: Request, current_user: dict = Depends(get_current_user)):
    if (current_user.get("role") or "").lower() not in ["admin", "portfolio"]:
        raise HTTPException(status_code=403, detail="Forbidden")
    return templates.TemplateResponse("generic.html", {
        "request": request,
        "user": current_user,
        "page_title": "Portfolio Dashboard"
    })

@router.get("/risks", response_class=HTMLResponse)
async def risk_management(request: Request, db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    """Risk management view"""
    return templates.TemplateResponse("risk_management.html", {
        "request": request,
        "user": current_user
    })

@router.get("/reports", response_class=HTMLResponse)
async def reports(request: Request, db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    """Reports view"""
    return templates.TemplateResponse("generic.html", {
        "request": request,
        "user": current_user,
        "page_title": "Reports"
    })

@router.get("/ai-copilot", response_class=HTMLResponse)
async def ai_copilot(request: Request, db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    """AI Copilot Console view"""
    return templates.TemplateResponse("ai_copilot.html", {
        "request": request,
        "user": current_user,
        "page_title": "AI Copilot Console"
    })

@router.get("/features", response_class=HTMLResponse)
async def features_list(request: Request, db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    """Features list view"""
    return templates.TemplateResponse("generic.html", {
        "request": request,
        "user": current_user,
        "page_title": "Features"
    })

@router.get("/backlog", response_class=HTMLResponse)
async def backlog_list(request: Request, db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    """Backlog list view"""
    return templates.TemplateResponse("backlog.html", {
        "request": request,
        "user": current_user,
        "page_title": "Backlog Management"
    })

@router.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    token = csrf_protection.generate_token(csrf_protection.get_session_id(request))
    return templates.TemplateResponse("login.html", {
        "request": request,
        "csrf_token": token
    })

@router.get("/admin", response_class=HTMLResponse)
async def admin_page(request: Request, current_user: dict = Depends(get_current_user)):
    if (current_user.get("role") or "").lower() != "admin":
        raise HTTPException(status_code=403, detail="Forbidden")
    token = csrf_protection.generate_token(csrf_protection.get_session_id(request))
    return templates.TemplateResponse("admin.html", {
        "request": request,
        "user": current_user,
        "page_title": "Admin",
        "csrf_token": token
    })

"""
View routes for GenAI Metrics Dashboard
"""
from fastapi import APIRouter, Request, Depends
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
import os

from app.database import get_db
from app.api.deps import get_current_user

# Initialize templates
templates = Jinja2Templates(directory="templates")

# Create router
router = APIRouter()

@router.get("/", response_class=HTMLResponse)
async def dashboard(request: Request, db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    """Main dashboard view"""
    try:
        return templates.TemplateResponse("dashboard.html", {
            "request": request,
            "user": current_user
        })
    except Exception as e:
        return HTMLResponse(f"<h1>Error loading dashboard: {str(e)}</h1>", status_code=500)

@router.get("/dashboard", response_class=HTMLResponse)
async def dashboard_page(request: Request, db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    """Dashboard page"""
    return templates.TemplateResponse("dashboard.html", {
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

@router.get("/projects/{project_id}", response_class=HTMLResponse)
async def project_detail(request: Request, project_id: int, db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    """Project detail view"""
    # For now, just render the template without project data
    return templates.TemplateResponse("project_detail.html", {
        "request": request,
        "user": current_user,
        "project": {"id": project_id, "name": "Sample Project"}
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
    """AI Copilot view"""
    return templates.TemplateResponse("generic.html", {
        "request": request,
        "user": current_user,
        "page_title": "AI Copilot"
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
    return templates.TemplateResponse("generic.html", {
        "request": request,
        "user": current_user,
        "page_title": "Backlog"
    })

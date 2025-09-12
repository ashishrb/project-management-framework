"""
Main API router for GenAI Metrics Dashboard
"""
from fastapi import APIRouter

from app.api.v1.endpoints import (
    projects, 
    dashboards, 
    comprehensive_dashboard,
    ai_analysis,
    lookup, 
    resources, 
    reports,
    ai_services,
    analytics,
    user,
    risks,
    ai,
    ai_dashboard,
    performance,
    rag,
    ai_insights,
    features,
    logs,
    backlogs,
    health,
    monitoring,
    ai_copilot,
    project_detail,
    file_upload,
    approval_workflow
)

api_router = APIRouter()

# Include all endpoint routers
api_router.include_router(projects.router, prefix="/projects", tags=["projects"])
api_router.include_router(dashboards.router, prefix="/dashboards", tags=["dashboards"])
api_router.include_router(comprehensive_dashboard.router, prefix="/comprehensive-dashboard", tags=["comprehensive-dashboard"])
api_router.include_router(ai_analysis.router, prefix="/ai-analysis", tags=["ai-analysis"])
api_router.include_router(lookup.router, prefix="/lookup", tags=["lookup"])
api_router.include_router(resources.router, prefix="/resources", tags=["resources"])
api_router.include_router(features.router, prefix="/features", tags=["features"])
api_router.include_router(reports.router, prefix="/reports", tags=["reports"])
api_router.include_router(ai_services.router, prefix="/ai-services", tags=["ai-services"])
api_router.include_router(analytics.router, prefix="/analytics", tags=["analytics"])
api_router.include_router(user.router, prefix="/user", tags=["user"])
api_router.include_router(risks.router, prefix="/risks", tags=["risks"])
api_router.include_router(ai.router, prefix="/ai", tags=["ai"])
api_router.include_router(ai_dashboard.router, prefix="/ai-dashboard", tags=["ai-dashboard"])
api_router.include_router(performance.router, prefix="/performance", tags=["performance"])
api_router.include_router(rag.router, prefix="/rag", tags=["rag"])
api_router.include_router(ai_insights.router, prefix="/ai-insights", tags=["ai-insights"])
api_router.include_router(logs.router, prefix="/logs", tags=["logs"])
api_router.include_router(backlogs.router, prefix="/backlogs", tags=["backlogs"])
api_router.include_router(health.router, prefix="/health", tags=["health"])
api_router.include_router(monitoring.router, prefix="/monitoring", tags=["monitoring"])
api_router.include_router(ai_copilot.router, prefix="/ai/copilot", tags=["ai-copilot"])
api_router.include_router(project_detail.router, prefix="/project-detail", tags=["project-detail"])
api_router.include_router(file_upload.router, prefix="/file-upload", tags=["file-upload"])
api_router.include_router(approval_workflow.router, prefix="/approval-workflow", tags=["approval-workflow"])

"""
API Version 2 Router for GenAI Metrics Dashboard
Enhanced API with improved features, pagination, and better error handling
"""
from fastapi import APIRouter
from app.api.v2.endpoints import (
    projects, features, resources, risks, backlogs, 
    reports, analytics, performance, ai_services, 
    ai_insights, ai_dashboard, logs, lookup
)

# Create API v2 router
api_router = APIRouter()

# Include all v2 endpoints
api_router.include_router(projects.router, prefix="/projects", tags=["projects-v2"])
api_router.include_router(features.router, prefix="/features", tags=["features-v2"])
api_router.include_router(resources.router, prefix="/resources", tags=["resources-v2"])
api_router.include_router(risks.router, prefix="/risks", tags=["risks-v2"])
api_router.include_router(backlogs.router, prefix="/backlogs", tags=["backlogs-v2"])
api_router.include_router(reports.router, prefix="/reports", tags=["reports-v2"])
api_router.include_router(analytics.router, prefix="/analytics", tags=["analytics-v2"])
api_router.include_router(performance.router, prefix="/performance", tags=["performance-v2"])
api_router.include_router(ai_services.router, prefix="/ai-services", tags=["ai-services-v2"])
api_router.include_router(ai_insights.router, prefix="/ai-insights", tags=["ai-insights-v2"])
api_router.include_router(ai_dashboard.router, prefix="/ai-dashboard", tags=["ai-dashboard-v2"])
api_router.include_router(logs.router, prefix="/logs", tags=["logs-v2"])
api_router.include_router(lookup.router, prefix="/lookup", tags=["lookup-v2"])

# API v2 metadata
api_router.metadata = {
    "title": "GenAI Metrics Dashboard API v2",
    "description": "Enhanced API with improved features and better performance",
    "version": "2.0.0",
    "contact": {
        "name": "GenAI Metrics Team",
        "email": "support@genai-metrics.com"
    },
    "license": {
        "name": "MIT",
        "url": "https://opensource.org/licenses/MIT"
    }
}

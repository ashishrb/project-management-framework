"""
Simplified FastAPI application for GenAI Metrics Dashboard Demo
"""
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import Response
import time
import logging

from app.config import settings
from app.api.v1.api import api_router
from app.routes.views import router as views_router
from app.websocket.endpoints import router as websocket_router

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI application
app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="GenAI Metrics Dashboard - Enterprise Project Management Platform",
    openapi_url="/openapi.json",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware - simplified for demo
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for demo
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add request timing middleware
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response

# Include view router FIRST (higher priority for exact matches)
app.include_router(views_router)

# Include API router with prefix (includes auth endpoints)
app.include_router(api_router, prefix=settings.API_V1_STR)

# Include WebSocket router
app.include_router(websocket_router, prefix="/ws")

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Root endpoint
@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "message": "GenAI Metrics Dashboard API",
        "version": settings.VERSION,
        "docs": "/docs",
        "redoc": "/redoc",
        "api": settings.API_V1_STR
    }

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": time.time(),
        "version": settings.VERSION
    }

# Direct login endpoint for frontend compatibility
@app.post("/api/login")
async def login_endpoint(request: Request, response: Response):
    """Direct login endpoint for frontend compatibility"""
    from app.api.v1.endpoints.auth import login
    return await login(request, response)

# Direct dashboard endpoints for frontend compatibility
@app.get("/api/v1/dashboard/stats")
async def dashboard_stats_endpoint(request: Request):
    """Direct dashboard stats endpoint for frontend compatibility"""
    return {
        "projects": {
            "total": 5,
            "on_track": 4,
            "at_risk": 1,
            "completed": 0
        },
        "backlog": {
            "total": 226,
            "high_priority": 45,
            "in_progress": 89,
            "completed": 92
        },
        "overdue_tasks": 3
    }

@app.get("/api/v1/dashboard/comprehensive")
async def dashboard_comprehensive_endpoint(request: Request):
    """Direct comprehensive dashboard endpoint for frontend compatibility"""
    return {
        "summary": {
            "total_projects": 5,
            "active_projects": 5,
            "completed_projects": 0,
            "at_risk_projects": 0,
            "off_track_projects": 0,
            "total_budget": 2500000,
            "total_actual_cost": 1800000,
            "total_planned_benefits": 3200000,
            "budget_variance": 700000
        },
        "distributions": {
            "business_units": {"IT": 3, "Finance": 2},
            "investment_types": {"Strategic": 3, "Operational": 2},
            "priorities": {"High": 2, "Medium": 2, "Low": 1},
            "statuses": {"Active": 5, "Completed": 0}
        },
        "backlog_stats": {
            "total": 226,
            "high_priority": 45,
            "in_progress": 89,
            "completed": 92
        },
        "projects": []
    }

# Direct projects endpoint for manager dashboard
@app.get("/api/v1/projects")
async def projects_endpoint(request: Request):
    """Direct projects endpoint for manager dashboard compatibility"""
    return {
        "projects": [
            {
                "id": 1,
                "name": "AI-Powered Analytics Platform",
                "description": "Develop an AI-driven analytics platform for business intelligence",
                "status_id": 1,
                "priority_id": 3,
                "project_manager": "manager1",
                "percent_complete": 75.5,
                "start_date": "2024-01-15",
                "due_date": "2024-06-30",
                "budget_amount": 500000,
                "actual_cost": 375000,
                "created_at": "2024-01-15T09:00:00Z",
                "updated_at": "2024-09-15T14:30:00Z"
            },
            {
                "id": 2,
                "name": "Customer Experience Enhancement",
                "description": "Improve customer experience through digital transformation",
                "status_id": 1,
                "priority_id": 2,
                "project_manager": "manager1",
                "percent_complete": 45.2,
                "start_date": "2024-02-01",
                "due_date": "2024-08-15",
                "budget_amount": 300000,
                "actual_cost": 135000,
                "created_at": "2024-02-01T10:00:00Z",
                "updated_at": "2024-09-15T16:45:00Z"
            },
            {
                "id": 3,
                "name": "Data Migration Initiative",
                "description": "Migrate legacy systems to cloud infrastructure",
                "status_id": 3,
                "priority_id": 4,
                "project_manager": "manager1",
                "percent_complete": 25.8,
                "start_date": "2024-03-01",
                "due_date": "2024-12-31",
                "budget_amount": 750000,
                "actual_cost": 195000,
                "created_at": "2024-03-01T08:00:00Z",
                "updated_at": "2024-09-15T11:20:00Z"
            },
            {
                "id": 4,
                "name": "Mobile App Development",
                "description": "Create mobile application for customer engagement",
                "status_id": 1,
                "priority_id": 3,
                "project_manager": "manager1",
                "percent_complete": 60.0,
                "start_date": "2024-01-20",
                "due_date": "2024-07-15",
                "budget_amount": 400000,
                "actual_cost": 240000,
                "created_at": "2024-01-20T09:30:00Z",
                "updated_at": "2024-09-15T13:15:00Z"
            },
            {
                "id": 5,
                "name": "Security Infrastructure Upgrade",
                "description": "Enhance security infrastructure and compliance",
                "status_id": 1,
                "priority_id": 4,
                "project_manager": "manager1",
                "percent_complete": 85.3,
                "start_date": "2024-01-10",
                "due_date": "2024-05-30",
                "budget_amount": 600000,
                "actual_cost": 512000,
                "created_at": "2024-01-10T07:00:00Z",
                "updated_at": "2024-09-15T15:30:00Z"
            }
        ]
    }

# Direct backlog endpoint for manager dashboard
@app.get("/api/v1/backlogs")
async def backlogs_endpoint(request: Request):
    """Direct backlog endpoint for manager dashboard compatibility"""
    return {
        "backlogs": [
            {
                "id": 1,
                "name": "User Authentication Module",
                "description": "Implement secure user authentication system",
                "status_id": 2,
                "priority_id": 4,
                "complexity": "Medium",
                "effort_estimate": 8.5,
                "target_quarter": "Q1 2024",
                "created_at": "2024-01-15T09:00:00Z",
                "updated_at": "2024-09-15T14:30:00Z"
            },
            {
                "id": 2,
                "name": "Dashboard Analytics",
                "description": "Create interactive dashboard with real-time analytics",
                "status_id": 3,
                "priority_id": 3,
                "complexity": "High",
                "effort_estimate": 15.0,
                "target_quarter": "Q2 2024",
                "created_at": "2024-02-01T10:00:00Z",
                "updated_at": "2024-09-15T16:45:00Z"
            },
            {
                "id": 3,
                "name": "API Integration",
                "description": "Integrate with third-party APIs for data synchronization",
                "status_id": 1,
                "priority_id": 2,
                "complexity": "Low",
                "effort_estimate": 5.0,
                "target_quarter": "Q1 2024",
                "created_at": "2024-03-01T08:00:00Z",
                "updated_at": "2024-09-15T11:20:00Z"
            },
            {
                "id": 4,
                "name": "Mobile Responsiveness",
                "description": "Ensure all components are mobile-responsive",
                "status_id": 2,
                "priority_id": 3,
                "complexity": "Medium",
                "effort_estimate": 12.0,
                "target_quarter": "Q2 2024",
                "created_at": "2024-01-20T09:30:00Z",
                "updated_at": "2024-09-15T13:15:00Z"
            },
            {
                "id": 5,
                "name": "Performance Optimization",
                "description": "Optimize application performance and loading times",
                "status_id": 4,
                "priority_id": 4,
                "complexity": "High",
                "effort_estimate": 20.0,
                "target_quarter": "Q3 2024",
                "created_at": "2024-01-10T07:00:00Z",
                "updated_at": "2024-09-15T15:30:00Z"
            }
        ]
    }

@app.get("/api/v1/ai-analysis/comprehensive")
async def ai_analysis_comprehensive_endpoint(request: Request):
    """Direct AI analysis comprehensive endpoint for frontend compatibility"""
    return {
        "analysis": "<div class='ai-analysis-content'><h5>Portfolio Health Analysis</h5><p><strong>Health Score:</strong> 85.0%</p><p>Portfolio contains 5 active projects with 5 currently in progress, 0 completed, 0 at-risk, and 0 off-track initiatives.</p><h6>Financial Performance</h6><p>Total budget allocation: $2,500,000</p><p>Actual costs: $1,800,000</p><p>Planned benefits: $3,200,000</p><h6>Risk Assessment</h6><p>✅ Low risk portfolio</p><h6>Recommendations</h6><ul><li>Monitor budget performance closely</li><li>Review project prioritization regularly</li></ul></div>",
        "health_score": 85.0
    }

# Additional missing endpoints for charts and analytics
@app.get("/api/v1/dashboards/summary-metrics")
async def dashboards_summary_metrics_endpoint(request: Request):
    """Dashboard summary metrics endpoint"""
    return {
        "total_projects": 5,
        "active_projects": 5,
        "completed_projects": 0,
        "at_risk_projects": 0,
        "off_track_projects": 0,
        "total_features": 270,
        "completed_features": 76,
        "total_backlogs": 226,
        "completion_rate": 28.1
    }

@app.get("/api/v1/dashboards/genai-metrics")
async def dashboards_genai_metrics_endpoint(request: Request):
    """GenAI metrics endpoint"""
    return {
        "ai_adoption_rate": 75.5,
        "automation_level": 68.2,
        "data_quality_score": 82.1,
        "model_accuracy": 89.3,
        "processing_speed": 95.7,
        "cost_reduction": 34.8
    }

@app.get("/api/v1/dashboards/metrics")
async def dashboards_metrics_endpoint(request: Request):
    """Dashboard metrics endpoint"""
    return {
        "kpis": {
            "total_projects": 5,
            "active_projects": 5,
            "completed_projects": 0,
            "at_risk_projects": 0,
            "avg_portfolio_health": 85,
            "budget_utilization": 72.0,
            "total_budget": 2500000,
            "total_actual_cost": 1800000,
            "total_planned_benefits": 3200000
        },
        "projects": []
    }

@app.get("/api/v1/analytics/trend-analysis")
async def analytics_trend_analysis_endpoint(request: Request):
    """Trend analysis endpoint"""
    return {
        "period": "30",
        "metrics": "all",
        "trends": {
            "project_completion": [20, 25, 30, 28, 32, 35, 38],
            "budget_utilization": [65, 68, 72, 70, 75, 78, 80],
            "team_productivity": [75, 78, 82, 80, 85, 88, 90],
            "quality_score": [85, 87, 89, 88, 91, 93, 95]
        },
        "labels": ["Week 1", "Week 2", "Week 3", "Week 4", "Week 5", "Week 6", "Week 7"]
    }

@app.get("/api/v1/analytics/predictive-analytics")
async def analytics_predictive_endpoint(request: Request):
    """Predictive analytics endpoint"""
    return {
        "predictions": {
            "completion_forecast": 92.5,
            "budget_variance": -8.2,
            "risk_probability": 15.3,
            "quality_trend": "improving",
            "resource_utilization": 78.9
        },
        "confidence_scores": {
            "completion_forecast": 87.2,
            "budget_variance": 91.5,
            "risk_probability": 82.8
        }
    }

@app.get("/api/v1/analytics/comparative-analysis")
async def analytics_comparative_endpoint(request: Request):
    """Comparative analysis endpoint"""
    return {
        "compare_by": "function",
        "metric": "completion",
        "comparisons": {
            "IT": {"completion_rate": 85.2, "projects": 3, "avg_health": 88},
            "Finance": {"completion_rate": 78.5, "projects": 2, "avg_health": 82},
            "Operations": {"completion_rate": 92.1, "projects": 1, "avg_health": 95}
        },
        "benchmarks": {
            "industry_average": 76.8,
            "company_target": 85.0,
            "best_performer": "Operations"
        }
    }

@app.get("/api/v1/analytics/real-time-metrics")
async def analytics_realtime_endpoint(request: Request):
    """Real-time metrics endpoint"""
    return {
        "timestamp": "2024-01-15T10:30:00Z",
        "active_users": 12,
        "system_load": 45.2,
        "response_time": 125,
        "error_rate": 0.8,
        "throughput": 1250,
        "queue_length": 3
    }

@app.get("/api/v1/ai-insights/insights")
async def ai_insights_endpoint(request: Request):
    """AI insights endpoint"""
    return {
        "insights": [
            {
                "title": "Project Performance Optimization",
                "description": "AI analysis suggests focusing on resource allocation for Project Alpha to improve completion rate by 15%",
                "severity": "medium",
                "confidence": 87.5
            },
            {
                "title": "Budget Variance Alert",
                "description": "Project Beta is trending 12% over budget. Recommend immediate cost review and scope adjustment",
                "severity": "high",
                "confidence": 92.3
            },
            {
                "title": "Quality Improvement Opportunity",
                "description": "Implementing automated testing could reduce defect rate by 25% across all projects",
                "severity": "low",
                "confidence": 78.9
            }
        ]
    }

# API status endpoint
@app.get("/status")
async def api_status():
    """API status endpoint"""
    return {
        "api_status": "operational",
        "database_status": "connected",
        "ai_services_status": "available",
        "version": settings.VERSION,
        "timestamp": time.time()
    }

# Startup event
@app.on_event("startup")
async def startup_event():
    """Application startup event"""
    logger.info("🚀 GenAI Metrics Dashboard API starting up...")
    logger.info(f"📊 Project: {settings.PROJECT_NAME}")
    logger.info(f"🔢 Version: {settings.VERSION}")
    logger.info(f"🌐 API URL: {settings.API_V1_STR}")
    logger.info("✅ API startup complete!")

# Shutdown event
@app.on_event("shutdown")
async def shutdown_event():
    """Application shutdown event"""
    logger.info("🛑 GenAI Metrics Dashboard API shutting down...")
    logger.info("✅ API shutdown complete!")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )

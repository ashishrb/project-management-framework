"""
Analytics endpoints for advanced dashboard features
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
import random
from datetime import datetime, timedelta

from app.api.deps import get_db, get_current_user, get_demo_project_ids
from app.config import settings
from app.models.main_tables import Project
from app.schemas.analytics_schemas import (
    TrendAnalysisResponse,
    PredictiveAnalyticsResponse,
    ComparativeAnalysisResponse,
    CustomReportRequest,
    CustomReportResponse
)

router = APIRouter()

@router.get("/trend-analysis", response_model=TrendAnalysisResponse)
async def get_trend_analysis(
    period: int = Query(30, description="Time period in days"),
    metrics: str = Query("all", description="Metrics to include"),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get trend analysis data for the specified period and metrics"""
    try:
        # Optionally scope to curated projects for demo
        demo_project_ids = []
        if settings.DEMO_MODE:
            demo_project_ids = get_demo_project_ids(db, limit=10)
        # Generate sample trend data based on period
        days = min(period, 365)  # Cap at 1 year
        labels = []
        datasets = []
        
        # Generate date labels
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        for i in range(days):
            date = start_date + timedelta(days=i)
            labels.append(date.strftime("%Y-%m-%d"))
        
        # Generate sample data based on metrics
        if metrics == "all" or metrics == "features":
            datasets.append({
                "label": "Features Completed",
                "data": [random.randint(5, 25) for _ in range(days)],
                "borderColor": "#28a745",
                "backgroundColor": "rgba(40, 167, 69, 0.1)",
                "tension": 0.4
            })
        
        if metrics == "all" or metrics == "backlogs":
            datasets.append({
                "label": "Backlogs Added",
                "data": [random.randint(2, 15) for _ in range(days)],
                "borderColor": "#ffc107",
                "backgroundColor": "rgba(255, 193, 7, 0.1)",
                "tension": 0.4
            })
        
        if metrics == "all" or metrics == "resources":
            datasets.append({
                "label": "Resource Utilization",
                "data": [random.randint(60, 95) for _ in range(days)],
                "borderColor": "#007bff",
                "backgroundColor": "rgba(0, 123, 255, 0.1)",
                "tension": 0.4
            })
        
        return TrendAnalysisResponse(
            labels=labels,
            datasets=datasets,
            period_days=days,
            metrics_included=metrics
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating trend analysis: {str(e)}")

@router.get("/predictive-analytics", response_model=PredictiveAnalyticsResponse)
async def get_predictive_analytics(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get predictive analytics data"""
    try:
        demo_project_ids = []
        if settings.DEMO_MODE:
            demo_project_ids = get_demo_project_ids(db, limit=10)
        # Generate sample predictive data
        completion_rate = random.randint(75, 95)
        predicted_risks = random.randint(5, 20)
        resource_shortage = random.randint(3, 12)
        
        # Generate prediction timeline
        labels = []
        completion_data = []
        risk_data = []
        
        for i in range(12):  # Next 12 months
            month = datetime.now() + timedelta(days=30 * i)
            labels.append(month.strftime("%Y-%m"))
            
            # Simulate trend
            completion_data.append(max(0, min(100, completion_rate + random.randint(-5, 5) + i * 2)))
            risk_data.append(max(0, predicted_risks + random.randint(-3, 3) - i))
        
        datasets = [
            {
                "label": "Predicted Completion Rate",
                "data": completion_data,
                "borderColor": "#28a745",
                "backgroundColor": "rgba(40, 167, 69, 0.1)",
                "tension": 0.4,
                "fill": True
            },
            {
                "label": "Predicted Risks",
                "data": risk_data,
                "borderColor": "#dc3545",
                "backgroundColor": "rgba(220, 53, 69, 0.1)",
                "tension": 0.4,
                "fill": False
            }
        ]
        
        return PredictiveAnalyticsResponse(
            completion_rate=completion_rate,
            predicted_risks=predicted_risks,
            resource_shortage=resource_shortage,
            labels=labels,
            datasets=datasets,
            confidence_score=random.uniform(0.75, 0.95)
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating predictive analytics: {str(e)}")

@router.get("/comparative-analysis", response_model=ComparativeAnalysisResponse)
async def get_comparative_analysis(
    compare_by: str = Query("function", description="Compare by function, platform, project, or team"),
    metric: str = Query("completion", description="Metric to compare"),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get comparative analysis data"""
    try:
        demo_project_ids = []
        if settings.DEMO_MODE:
            demo_project_ids = get_demo_project_ids(db, limit=10)
        # Generate sample comparative data based on comparison type
        if compare_by == "function":
            labels = ["Engineering", "Marketing", "Sales", "Support", "Operations"]
        elif compare_by == "platform":
            labels = ["Web", "Mobile", "Desktop", "API", "Cloud"]
        elif compare_by == "project":
            labels = ["Project A", "Project B", "Project C", "Project D", "Project E"]
        else:  # team
            labels = ["Team Alpha", "Team Beta", "Team Gamma", "Team Delta", "Team Epsilon"]
        
        # Generate data based on metric
        if metric == "completion":
            data = [random.randint(60, 95) for _ in labels]
            color = "#28a745"
        elif metric == "efficiency":
            data = [random.randint(70, 100) for _ in labels]
            color = "#007bff"
        elif metric == "quality":
            data = [random.randint(80, 100) for _ in labels]
            color = "#17a2b8"
        else:  # timeline
            data = [random.randint(75, 100) for _ in labels]
            color = "#ffc107"
        
        datasets = [{
            "label": f"{metric.title()} Score",
            "data": data,
            "backgroundColor": [color] * len(labels),
            "borderColor": color,
            "borderWidth": 1
        }]
        
        return ComparativeAnalysisResponse(
            labels=labels,
            datasets=datasets,
            compare_by=compare_by,
            metric=metric,
            total_items=len(labels)
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating comparative analysis: {str(e)}")

@router.post("/custom-report", response_model=CustomReportResponse)
async def generate_custom_report(
    request: CustomReportRequest,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Generate a custom report based on user specifications"""
    try:
        # Generate report based on request
        report_id = f"RPT_{random.randint(10000, 99999)}"
        
        # Simulate report generation
        sections = []
        if request.include_overview:
            sections.append("Project Overview")
        if request.include_genai:
            sections.append("GenAI Metrics")
        if request.include_resources:
            sections.append("Resource Analysis")
        if request.include_risks:
            sections.append("Risk Assessment")
        
        # Generate sample data for each section
        report_data = {
            "report_id": report_id,
            "report_name": request.report_name or f"Custom Report {report_id}",
            "report_type": request.report_type,
            "period": request.period,
            "sections": sections,
            "generated_at": datetime.now().isoformat(),
            "generated_by": current_user.get("username", "Unknown"),
            "status": "completed",
            "file_url": f"/reports/download/{report_id}.pdf"
        }
        
        return CustomReportResponse(**report_data)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating custom report: {str(e)}")

@router.get("/export/{format}")
async def export_dashboard(
    format: str,
    include_charts: bool = Query(True, description="Include charts in export"),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Export dashboard data in specified format"""
    try:
        # Simulate export generation
        export_id = f"EXP_{random.randint(10000, 99999)}"
        
        # Generate export data based on format
        if format == "pdf":
            content_type = "application/pdf"
            file_url = f"/exports/{export_id}.pdf"
        elif format == "excel":
            content_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            file_url = f"/exports/{export_id}.xlsx"
        elif format == "csv":
            content_type = "text/csv"
            file_url = f"/exports/{export_id}.csv"
        elif format == "image":
            content_type = "image/png"
            file_url = f"/exports/{export_id}.png"
        else:
            raise HTTPException(status_code=400, detail="Invalid export format")
        
        return {
            "export_id": export_id,
            "format": format,
            "include_charts": include_charts,
            "file_url": file_url,
            "status": "completed",
            "generated_at": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error exporting dashboard: {str(e)}")

@router.get("/real-time-metrics")
async def get_real_time_metrics(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get real-time metrics for dashboard updates"""
    try:
        # Generate real-time metrics
        current_time = datetime.now()
        
        metrics = {
            "timestamp": current_time.isoformat(),
            "active_users": random.randint(10, 50),
            "projects_active": random.randint(5, 20),
            "features_completed_today": random.randint(10, 30),
            "backlogs_added_today": random.randint(5, 15),
            "resource_utilization": random.randint(70, 95),
            "risk_count": random.randint(5, 25),
            "ai_insights_generated": random.randint(3, 10)
        }
        
        return metrics
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting real-time metrics: {str(e)}")

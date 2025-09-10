"""
Analytics schemas for advanced dashboard features
"""
from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel

class TrendAnalysisResponse(BaseModel):
    labels: List[str]
    datasets: List[Dict[str, Any]]
    period_days: int
    metrics_included: str
    
    class Config:
        from_attributes = True

class PredictiveAnalyticsResponse(BaseModel):
    completion_rate: int
    predicted_risks: int
    resource_shortage: int
    labels: List[str]
    datasets: List[Dict[str, Any]]
    confidence_score: float
    
    class Config:
        from_attributes = True

class ComparativeAnalysisResponse(BaseModel):
    labels: List[str]
    datasets: List[Dict[str, Any]]
    compare_by: str
    metric: str
    total_items: int
    
    class Config:
        from_attributes = True

class CustomReportRequest(BaseModel):
    report_name: Optional[str] = None
    report_type: str = "summary"
    period: str = "month"
    include_overview: bool = True
    include_genai: bool = True
    include_resources: bool = True
    include_risks: bool = True
    
    class Config:
        from_attributes = True

class CustomReportResponse(BaseModel):
    report_id: str
    report_name: str
    report_type: str
    period: str
    sections: List[str]
    generated_at: str
    generated_by: str
    status: str
    file_url: str
    
    class Config:
        from_attributes = True

class ExportRequest(BaseModel):
    format: str
    include_charts: bool = True
    
    class Config:
        from_attributes = True

class ExportResponse(BaseModel):
    export_id: str
    format: str
    include_charts: bool
    file_url: str
    status: str
    generated_at: str
    
    class Config:
        from_attributes = True

class RealTimeMetrics(BaseModel):
    timestamp: str
    active_users: int
    projects_active: int
    features_completed_today: int
    backlogs_added_today: int
    resource_utilization: int
    risk_count: int
    ai_insights_generated: int
    
    class Config:
        from_attributes = True

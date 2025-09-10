"""
Pydantic schemas for reports and analytics
"""
from pydantic import BaseModel
from typing import Optional, List
from datetime import date, datetime
from decimal import Decimal

# ==================== PROJECT REPORT SCHEMAS ====================

class ProjectReport(BaseModel):
    """Project report data"""
    project_id: str
    name: str
    status: str
    priority: str
    portfolio: str
    start_date: Optional[date] = None
    due_date: Optional[date] = None
    percent_complete: float
    feature_count: int
    task_count: int
    project_manager: Optional[str] = None
    business_owner: Optional[str] = None

# ==================== FEATURE REPORT SCHEMAS ====================

class FeatureReport(BaseModel):
    """Feature report data"""
    feature_name: str
    project_name: str
    status: str
    priority: str
    complexity: Optional[str] = None
    effort_estimate: Optional[Decimal] = None
    percent_complete: float
    planned_start_date: Optional[date] = None
    planned_end_date: Optional[date] = None
    business_value: Optional[str] = None

# ==================== BACKLOG REPORT SCHEMAS ====================

class BacklogReport(BaseModel):
    """Backlog report data"""
    backlog_id: str
    name: str
    status: str
    priority: str
    complexity: Optional[str] = None
    effort_estimate: Optional[Decimal] = None
    target_quarter: Optional[str] = None
    planned_start_date: Optional[date] = None
    planned_end_date: Optional[date] = None
    business_value: Optional[str] = None

# ==================== RESOURCE REPORT SCHEMAS ====================

class ResourceReport(BaseModel):
    """Resource report data"""
    resource_name: str
    email: str
    role: Optional[str] = None
    experience_level: Optional[str] = None
    skills: List[str] = []
    availability_percentage: float
    project_count: int
    task_count: int

# ==================== RISK REPORT SCHEMAS ====================

class RiskReport(BaseModel):
    """Risk report data"""
    risk_name: str
    project_name: str
    risk_level: str
    probability: float
    impact: float
    risk_score: float
    status: str
    mitigation_plan: Optional[str] = None
    mitigation_owner: Optional[str] = None
    mitigation_due_date: Optional[date] = None

# ==================== PORTFOLIO REPORT SCHEMAS ====================

class PortfolioReport(BaseModel):
    """Portfolio report data"""
    portfolio_name: str
    total_projects: int
    active_projects: int
    completed_projects: int
    at_risk_projects: int
    feature_count: int
    backlog_count: int
    avg_completion_rate: float

# ==================== EXECUTIVE SUMMARY SCHEMAS ====================

class ExecutiveSummary(BaseModel):
    """Executive summary report data"""
    total_projects: int
    active_projects: int
    completed_projects: int
    at_risk_projects: int
    total_features: int
    completed_features: int
    total_backlogs: int
    total_resources: int
    total_risks: int
    high_risks: int
    project_completion_rate: float
    feature_completion_rate: float

# ==================== CHART DATA SCHEMAS ====================

class ChartDataPoint(BaseModel):
    """Chart data point"""
    label: str
    value: float
    color: Optional[str] = None

class ChartSeries(BaseModel):
    """Chart series data"""
    name: str
    data: List[ChartDataPoint]
    color: Optional[str] = None

class ChartConfig(BaseModel):
    """Chart configuration"""
    title: str
    type: str  # bar, line, pie, etc.
    series: List[ChartSeries]
    x_axis_label: Optional[str] = None
    y_axis_label: Optional[str] = None

# ==================== EXPORT SCHEMAS ====================

class ExportRequest(BaseModel):
    """Export request parameters"""
    format: str  # csv, excel, pdf
    report_type: str  # projects, features, backlogs, resources, risks
    filters: Optional[dict] = None
    include_charts: bool = True

class ExportResponse(BaseModel):
    """Export response"""
    file_url: str
    file_name: str
    file_size: int
    expires_at: str
    download_count: int = 0

# ==================== ANALYTICS SCHEMAS ====================

class TrendData(BaseModel):
    """Trend analysis data"""
    period: str
    value: float
    change: float
    change_percentage: float

class ComparisonData(BaseModel):
    """Comparison analysis data"""
    metric: str
    current_value: float
    previous_value: float
    change: float
    change_percentage: float

class PerformanceMetrics(BaseModel):
    """Performance metrics"""
    metric_name: str
    current_value: float
    target_value: float
    variance: float
    status: str  # on_track, at_risk, off_track

# ==================== DASHBOARD WIDGET SCHEMAS ====================

class WidgetData(BaseModel):
    """Dashboard widget data"""
    widget_id: str
    widget_type: str
    title: str
    data: dict
    config: dict
    last_updated: datetime

class DashboardWidget(BaseModel):
    """Dashboard widget configuration"""
    widget_id: str
    widget_type: str
    title: str
    position: dict  # x, y, width, height
    config: dict
    data_source: str
    refresh_interval: int  # seconds

"""
Pydantic schemas for dashboard and analytics
"""
from pydantic import BaseModel
from typing import List, Optional
from decimal import Decimal

# ==================== DASHBOARD METRICS ====================

class DashboardMetrics(BaseModel):
    """Overall dashboard metrics"""
    total_projects: int
    active_projects: int
    completed_projects: int
    at_risk_projects: int
    off_track_projects: int
    total_features: int
    completed_features: int
    total_backlogs: int
    completion_rate: float

# ==================== FUNCTION METRICS ====================

class FunctionMetrics(BaseModel):
    """Function-based metrics for GenAI analytics"""
    function_id: int
    function_name: str
    completed: int
    on_track: int
    at_risk: int
    off_track: int

# ==================== PLATFORM METRICS ====================

class PlatformMetrics(BaseModel):
    """Platform-based metrics for GenAI analytics"""
    platform_id: int
    platform_name: str
    completed: int
    on_track: int
    at_risk: int
    off_track: int

# ==================== GENAI METRICS ====================

class GenAIMetrics(BaseModel):
    """4-panel GenAI metrics as per wire diagram"""
    active_features_by_function: List[FunctionMetrics]
    backlogs_by_function: List[FunctionMetrics]
    active_features_by_platform: List[PlatformMetrics]
    backlogs_by_platform: List[PlatformMetrics]

# ==================== ALL PROJECTS DASHBOARD ====================

class AllProjectsDashboard(BaseModel):
    """All Projects Dashboard response"""
    current_projects: int
    approved_projects: int
    backlog_projects: int
    total_projects: int
    genai_metrics: GenAIMetrics

# ==================== PORTFOLIO DASHBOARD ====================

class PortfolioDashboard(BaseModel):
    """Portfolio Dashboard response"""
    total_projects: int
    active_projects: int
    completed_projects: int
    budget_utilization: float
    genai_metrics: GenAIMetrics

# ==================== CHART DATA ====================

class ChartDataPoint(BaseModel):
    """Individual data point for charts"""
    label: str
    value: int
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

# ==================== EXPORT FORMATS ====================

class ExportRequest(BaseModel):
    """Export request parameters"""
    format: str  # pdf, excel, csv
    dashboard_type: str  # all-projects, portfolio
    portfolio_id: Optional[int] = None
    include_charts: bool = True
    include_data: bool = True

class ExportResponse(BaseModel):
    """Export response"""
    file_url: str
    file_name: str
    file_size: int
    expires_at: str

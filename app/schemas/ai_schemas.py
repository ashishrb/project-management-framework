"""
Pydantic schemas for AI services
"""
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime

# ==================== AI COPILOT SCHEMAS ====================

class AICopilotRequest(BaseModel):
    """AI Copilot chat request"""
    message: str
    context: Optional[Dict[str, Any]] = None
    session_id: Optional[str] = None

class AICopilotResponse(BaseModel):
    """AI Copilot chat response"""
    response: str
    context: Dict[str, Any]
    suggestions: Optional[List[str]] = None

# ==================== RISK ANALYSIS SCHEMAS ====================

class RiskAnalysisRequest(BaseModel):
    """Risk analysis request"""
    project_id: int
    analysis_type: str = "comprehensive"  # comprehensive, quick, detailed
    include_mitigation: bool = True

class RiskAnalysisResponse(BaseModel):
    """Risk analysis response"""
    analysis: Dict[str, Any]
    confidence_score: float
    generated_at: str

# ==================== DEPENDENCY RESOLUTION SCHEMAS ====================

class DependencyResolutionRequest(BaseModel):
    """Dependency resolution request"""
    project_id: int
    resolution_type: str = "automatic"  # automatic, manual, hybrid
    include_recommendations: bool = True

class DependencyResolutionResponse(BaseModel):
    """Dependency resolution response"""
    analysis: Dict[str, Any]
    resolution_confidence: float
    generated_at: str

# ==================== GENAI ANALYTICS SCHEMAS ====================

class GenAIAnalyticsRequest(BaseModel):
    """GenAI analytics request"""
    portfolio_id: Optional[int] = None
    analysis_period: str = "quarterly"  # weekly, monthly, quarterly, yearly
    include_predictions: bool = True
    include_recommendations: bool = True

class GenAIAnalyticsResponse(BaseModel):
    """GenAI analytics response"""
    analytics: Dict[str, Any]
    generated_at: str
    model_version: str
    
    class Config:
        protected_namespaces = ()

# ==================== AI PREDICTIONS SCHEMAS ====================

class AIPredictionRequest(BaseModel):
    """AI prediction request"""
    prediction_type: str = "comprehensive"  # comprehensive, project, resource, budget
    time_horizon: str = "quarterly"  # monthly, quarterly, yearly
    include_confidence: bool = True

class AIPredictionResponse(BaseModel):
    """AI prediction response"""
    predictions: Dict[str, Any]
    confidence_scores: Dict[str, float]
    generated_at: str
    model_version: str
    
    class Config:
        protected_namespaces = ()

# ==================== AI RECOMMENDATIONS SCHEMAS ====================

class AIRecommendation(BaseModel):
    """AI recommendation"""
    id: int
    type: str  # optimization, risk_mitigation, process_improvement
    title: str
    description: str
    priority: str  # High, Medium, Low
    impact: str  # High, Medium, Low
    effort: str  # High, Medium, Low
    confidence: float

class AIRecommendationRequest(BaseModel):
    """AI recommendation request"""
    project_id: Optional[int] = None
    recommendation_type: Optional[str] = None
    priority_filter: Optional[str] = None
    limit: int = 10

class AIRecommendationResponse(BaseModel):
    """AI recommendation response"""
    recommendations: List[AIRecommendation]
    total_count: int
    generated_at: str

# ==================== AI INSIGHTS SCHEMAS ====================

class AIInsight(BaseModel):
    """AI insight"""
    id: int
    type: str  # pattern, anomaly, trend, prediction
    title: str
    description: str
    confidence: float
    actionable: bool
    impact: Optional[str] = None

class AIInsightRequest(BaseModel):
    """AI insight request"""
    insight_type: Optional[str] = None
    time_period: Optional[str] = None
    include_historical: bool = False

class AIInsightResponse(BaseModel):
    """AI insight response"""
    insights: List[AIInsight]
    total_count: int
    generated_at: str

# ==================== AI MODELS SCHEMAS ====================

class AIModel(BaseModel):
    """AI model information"""
    model_id: str
    name: str
    version: str
    type: str  # copilot, analytics, prediction, recommendation
    status: str  # active, training, deprecated
    accuracy: Optional[float] = None
    last_trained: Optional[datetime] = None
    
    class Config:
        protected_namespaces = ()

class AIModelRequest(BaseModel):
    """AI model request"""
    model_type: str
    training_data: Optional[Dict[str, Any]] = None
    parameters: Optional[Dict[str, Any]] = None
    
    class Config:
        protected_namespaces = ()

class AIModelResponse(BaseModel):
    """AI model response"""
    model: AIModel
    status: str
    message: str

# ==================== AI CONFIGURATION SCHEMAS ====================

class AIConfiguration(BaseModel):
    """AI configuration"""
    model_settings: Dict[str, Any]
    response_settings: Dict[str, Any]
    training_settings: Dict[str, Any]
    monitoring_settings: Dict[str, Any]
    
    class Config:
        protected_namespaces = ()

class AIConfigurationRequest(BaseModel):
    """AI configuration request"""
    configuration: AIConfiguration
    apply_immediately: bool = False

class AIConfigurationResponse(BaseModel):
    """AI configuration response"""
    status: str
    message: str
    applied_at: Optional[datetime] = None

# ==================== AI MONITORING SCHEMAS ====================

class AIMetrics(BaseModel):
    """AI performance metrics"""
    model_id: str
    accuracy: float
    response_time: float
    usage_count: int
    error_rate: float
    last_updated: datetime
    
    class Config:
        protected_namespaces = ()

class AIMonitoringRequest(BaseModel):
    """AI monitoring request"""
    model_id: Optional[str] = None
    time_period: str = "daily"  # hourly, daily, weekly, monthly
    include_details: bool = True

class AIMonitoringResponse(BaseModel):
    """AI monitoring response"""
    metrics: List[AIMetrics]
    summary: Dict[str, Any]
    generated_at: str

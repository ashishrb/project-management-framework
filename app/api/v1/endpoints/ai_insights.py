"""
AI Insights API Endpoints
Provides AI-powered insights, analytics, and intelligent recommendations
"""

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from datetime import datetime, timedelta

from app.core.advanced_ai import (
    get_advanced_ai_service, AIInsightType, PredictionType, AutomationTask
)
from app.core.vector_db import get_vector_db, get_rag_service
from app.core.ai_client import get_ai_service, AIMessage
from app.core.logging import get_logger, log_api_endpoint
from app.database import get_db
from sqlalchemy.orm import Session

logger = get_logger(__name__)
router = APIRouter()


# Request/Response Models
class IntelligentDashboardRequest(BaseModel):
    """Intelligent dashboard request."""
    user_id: Optional[str] = None
    include_predictions: bool = True
    include_insights: bool = True
    include_recommendations: bool = True
    include_automation: bool = False
    time_horizon: int = Field(default=30, ge=1, le=365)


class IntelligentDashboardResponse(BaseModel):
    """Intelligent dashboard response."""
    dashboard_data: Dict[str, Any]
    ai_insights: List[Dict[str, Any]]
    predictions: List[Dict[str, Any]]
    recommendations: List[str]
    automation_suggestions: List[Dict[str, Any]]
    confidence_scores: Dict[str, float]
    timestamp: datetime


class SmartAnalysisRequest(BaseModel):
    """Smart analysis request."""
    analysis_type: str = Field(..., description="Type of analysis to perform")
    data_filters: Optional[Dict[str, Any]] = Field(default_factory=dict)
    parameters: Optional[Dict[str, Any]] = Field(default_factory=dict)


class SmartAnalysisResponse(BaseModel):
    """Smart analysis response."""
    analysis_type: str
    insights: List[Dict[str, Any]]
    patterns: List[Dict[str, Any]]
    anomalies: List[Dict[str, Any]]
    recommendations: List[str]
    confidence: float
    model_used: str
    processing_time: float
    timestamp: datetime


class PredictiveAnalyticsRequest(BaseModel):
    """Predictive analytics request."""
    prediction_types: List[PredictionType]
    time_horizon: int = Field(default=30, ge=1, le=365)
    filters: Optional[Dict[str, Any]] = Field(default_factory=dict)


class PredictiveAnalyticsResponse(BaseModel):
    """Predictive analytics response."""
    predictions: Dict[str, List[Dict[str, Any]]]
    confidence_scores: Dict[str, float]
    risk_factors: List[str]
    opportunities: List[str]
    time_horizon: int
    model_used: str
    processing_time: float
    timestamp: datetime


class IntelligentRecommendationRequest(BaseModel):
    """Intelligent recommendation request."""
    context: Dict[str, Any]
    recommendation_categories: List[str] = Field(default=["optimization", "risk_mitigation", "efficiency"])
    priority_level: str = Field(default="medium", description="Priority level: low, medium, high, critical")


class IntelligentRecommendationResponse(BaseModel):
    """Intelligent recommendation response."""
    recommendations: Dict[str, List[Dict[str, Any]]]
    priority_ranking: List[str]
    impact_assessment: Dict[str, str]
    implementation_effort: Dict[str, str]
    expected_benefits: Dict[str, str]
    confidence: float
    model_used: str
    processing_time: float
    timestamp: datetime


class AutomationWorkflowRequest(BaseModel):
    """Automation workflow request."""
    workflow_name: str
    trigger_conditions: Dict[str, Any]
    actions: List[Dict[str, Any]]
    schedule: Optional[str] = None


class AutomationWorkflowResponse(BaseModel):
    """Automation workflow response."""
    workflow_id: str
    workflow_name: str
    status: str
    trigger_conditions: Dict[str, Any]
    actions: List[Dict[str, Any]]
    schedule: Optional[str]
    created_at: datetime
    next_execution: Optional[datetime]


class KnowledgeQueryRequest(BaseModel):
    """Knowledge base query request."""
    query: str
    context: Optional[Dict[str, Any]] = Field(default_factory=dict)
    search_collections: Optional[List[str]] = Field(default=None)
    include_sources: bool = Field(default=True)


class KnowledgeQueryResponse(BaseModel):
    """Knowledge base query response."""
    answer: str
    sources: List[Dict[str, Any]]
    confidence: float
    related_queries: List[str]
    knowledge_gaps: List[str]
    model_used: str
    processing_time: float
    timestamp: datetime


# Intelligent Dashboard Endpoints
@router.post("/intelligent-dashboard", response_model=IntelligentDashboardResponse)
@log_api_endpoint
async def get_intelligent_dashboard(
    request: IntelligentDashboardRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Get AI-powered intelligent dashboard with insights, predictions, and recommendations."""
    try:
        start_time = datetime.now()
        
        # Get basic dashboard data
        from app.api.v1.endpoints.dashboards import get_all_projects_dashboard
        dashboard_data = await get_all_projects_dashboard(db)
        
        ai_insights = []
        predictions = []
        recommendations = []
        automation_suggestions = []
        confidence_scores = {}
        
        # Generate AI insights
        if request.include_insights:
            try:
                insights = await _generate_comprehensive_insights(dashboard_data, request.time_horizon)
                ai_insights = [insight.dict() for insight in insights]
                confidence_scores["insights"] = np.mean([insight.confidence for insight in insights]) if insights else 0.0
            except Exception as e:
                logger.warning(f"Failed to generate insights: {e}")
        
        # Generate predictions
        if request.include_predictions:
            try:
                predictions_data = await _generate_comprehensive_predictions(dashboard_data, request.time_horizon)
                predictions = [pred.dict() for pred in predictions_data]
                confidence_scores["predictions"] = np.mean([pred.confidence for pred in predictions_data]) if predictions_data else 0.0
            except Exception as e:
                logger.warning(f"Failed to generate predictions: {e}")
        
        # Generate recommendations
        if request.include_recommendations:
            try:
                recommendations = await _generate_intelligent_recommendations(dashboard_data, request.time_horizon)
                confidence_scores["recommendations"] = 0.8  # Default confidence for recommendations
            except Exception as e:
                logger.warning(f"Failed to generate recommendations: {e}")
        
        # Generate automation suggestions
        if request.include_automation:
            try:
                automation_suggestions = await _generate_automation_suggestions(dashboard_data)
                confidence_scores["automation"] = 0.7  # Default confidence for automation
            except Exception as e:
                logger.warning(f"Failed to generate automation suggestions: {e}")
        
        processing_time = (datetime.now() - start_time).total_seconds()
        
        return IntelligentDashboardResponse(
            dashboard_data=dashboard_data,
            ai_insights=ai_insights,
            predictions=predictions,
            recommendations=recommendations,
            automation_suggestions=automation_suggestions,
            confidence_scores=confidence_scores,
            timestamp=datetime.now()
        )
        
    except Exception as e:
        logger.error(f"Error generating intelligent dashboard: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/smart-analysis", response_model=SmartAnalysisResponse)
@log_api_endpoint
async def perform_smart_analysis(
    request: SmartAnalysisRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Perform comprehensive smart analysis using AI."""
    try:
        start_time = datetime.now()
        
        # Get relevant data based on analysis type
        data = await _get_data_for_analysis(request.analysis_type, request.data_filters, db)
        
        advanced_ai = await get_advanced_ai_service()
        
        insights = []
        patterns = []
        anomalies = []
        recommendations = []
        
        # Perform different types of analysis
        if request.analysis_type == "comprehensive":
            # Trend analysis
            trend_insight = await advanced_ai.analyze_trends(data)
            insights.append(trend_insight.dict())
            
            # Pattern detection
            pattern_insight = await advanced_ai.detect_patterns(data)
            patterns.append(pattern_insight.dict())
            
            # Anomaly detection
            anomaly_insight = await advanced_ai.detect_anomalies(data)
            anomalies.append(anomaly_insight.dict())
            
        elif request.analysis_type == "trend":
            trend_insight = await advanced_ai.analyze_trends(data, **request.parameters)
            insights.append(trend_insight.dict())
            
        elif request.analysis_type == "pattern":
            pattern_insight = await advanced_ai.detect_patterns(data, **request.parameters)
            patterns.append(pattern_insight.dict())
            
        elif request.analysis_type == "anomaly":
            anomaly_insight = await advanced_ai.detect_anomalies(data, **request.parameters)
            anomalies.append(anomaly_insight.dict())
        
        # Generate recommendations based on analysis
        if insights or patterns or anomalies:
            analysis_context = {
                "insights": insights,
                "patterns": patterns,
                "anomalies": anomalies,
                "analysis_type": request.analysis_type
            }
            recommendations = await advanced_ai.generate_smart_recommendations(analysis_context)
        
        # Calculate overall confidence
        all_insights = insights + patterns + anomalies
        confidence = np.mean([insight.get("confidence", 0.5) for insight in all_insights]) if all_insights else 0.5
        
        processing_time = (datetime.now() - start_time).total_seconds()
        
        return SmartAnalysisResponse(
            analysis_type=request.analysis_type,
            insights=insights,
            patterns=patterns,
            anomalies=anomalies,
            recommendations=recommendations,
            confidence=confidence,
            model_used="llama3:8b",
            processing_time=processing_time,
            timestamp=datetime.now()
        )
        
    except Exception as e:
        logger.error(f"Error performing smart analysis: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/predictive-analytics", response_model=PredictiveAnalyticsResponse)
@log_api_endpoint
async def generate_predictive_analytics(
    request: PredictiveAnalyticsRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Generate comprehensive predictive analytics."""
    try:
        start_time = datetime.now()
        
        # Get relevant data
        data = await _get_data_for_predictions(request.filters, db)
        
        advanced_ai = await get_advanced_ai_service()
        
        predictions = {}
        confidence_scores = {}
        
        # Generate predictions for each type
        for prediction_type in request.prediction_types:
            preds = await advanced_ai.generate_predictions(
                data=data,
                prediction_type=prediction_type,
                time_horizon=request.time_horizon
            )
            
            predictions[prediction_type.value] = [pred.dict() for pred in preds]
            confidence_scores[prediction_type.value] = np.mean([pred.confidence for pred in preds]) if preds else 0.5
        
        # Generate risk factors and opportunities
        risk_factors = await _identify_risk_factors(predictions, data)
        opportunities = await _identify_opportunities(predictions, data)
        
        processing_time = (datetime.now() - start_time).total_seconds()
        
        return PredictiveAnalyticsResponse(
            predictions=predictions,
            confidence_scores=confidence_scores,
            risk_factors=risk_factors,
            opportunities=opportunities,
            time_horizon=request.time_horizon,
            model_used="llama3:8b",
            processing_time=processing_time,
            timestamp=datetime.now()
        )
        
    except Exception as e:
        logger.error(f"Error generating predictive analytics: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/intelligent-recommendations", response_model=IntelligentRecommendationResponse)
@log_api_endpoint
async def generate_intelligent_recommendations(
    request: IntelligentRecommendationRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Generate intelligent, context-aware recommendations."""
    try:
        start_time = datetime.now()
        
        # Enhance context with current data
        enhanced_context = await _enhance_recommendation_context(request.context, db)
        
        advanced_ai = await get_advanced_ai_service()
        
        recommendations = {}
        priority_ranking = []
        impact_assessment = {}
        implementation_effort = {}
        expected_benefits = {}
        
        # Generate recommendations for each category
        for category in request.recommendation_categories:
            category_context = {
                **enhanced_context,
                "category": category,
                "priority_level": request.priority_level
            }
            
            category_recommendations = await advanced_ai.generate_smart_recommendations(
                context=category_context,
                recommendation_type=category
            )
            
            recommendations[category] = [
                {
                    "recommendation": rec,
                    "category": category,
                    "priority": request.priority_level,
                    "impact": "Medium",  # Default impact
                    "effort": "Medium",  # Default effort
                    "benefits": "Improved efficiency"  # Default benefits
                }
                for rec in category_recommendations
            ]
            
            # Generate priority ranking
            priority_ranking.extend([rec["recommendation"] for rec in recommendations[category]])
            
            # Generate assessments
            for rec in recommendations[category]:
                impact_assessment[rec["recommendation"]] = rec["impact"]
                implementation_effort[rec["recommendation"]] = rec["effort"]
                expected_benefits[rec["recommendation"]] = rec["benefits"]
        
        # Sort by priority
        priority_ranking = priority_ranking[:10]  # Top 10 recommendations
        
        processing_time = (datetime.now() - start_time).total_seconds()
        
        return IntelligentRecommendationResponse(
            recommendations=recommendations,
            priority_ranking=priority_ranking,
            impact_assessment=impact_assessment,
            implementation_effort=implementation_effort,
            expected_benefits=expected_benefits,
            confidence=0.8,
            model_used="llama3:8b",
            processing_time=processing_time,
            timestamp=datetime.now()
        )
        
    except Exception as e:
        logger.error(f"Error generating intelligent recommendations: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/knowledge-query", response_model=KnowledgeQueryResponse)
@log_api_endpoint
async def query_knowledge_base(request: KnowledgeQueryRequest):
    """Query the AI-powered knowledge base using RAG."""
    try:
        start_time = datetime.now()
        
        rag_service = await get_rag_service()
        
        # Generate answer using RAG
        response = await rag_service.generate_answer(
            query=request.query,
            collection_names=request.search_collections,
            top_k=5,
            include_sources=request.include_sources
        )
        
        # Generate related queries
        related_queries = await _generate_related_queries(request.query, response.sources)
        
        # Identify knowledge gaps
        knowledge_gaps = await _identify_knowledge_gaps(request.query, response.sources)
        
        processing_time = (datetime.now() - start_time).total_seconds()
        
        return KnowledgeQueryResponse(
            answer=response.answer,
            sources=[source.dict() for source in response.sources] if request.include_sources else [],
            confidence=response.confidence,
            related_queries=related_queries,
            knowledge_gaps=knowledge_gaps,
            model_used=response.model_used,
            processing_time=processing_time,
            timestamp=datetime.now()
        )
        
    except Exception as e:
        logger.error(f"Error querying knowledge base: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/automation/workflow", response_model=AutomationWorkflowResponse)
@log_api_endpoint
async def create_automation_workflow(request: AutomationWorkflowRequest):
    """Create an intelligent automation workflow."""
    try:
        workflow_id = str(uuid.uuid4())
        
        # Create workflow (simplified implementation)
        workflow = {
            "workflow_id": workflow_id,
            "workflow_name": request.workflow_name,
            "status": "active",
            "trigger_conditions": request.trigger_conditions,
            "actions": request.actions,
            "schedule": request.schedule,
            "created_at": datetime.now(),
            "next_execution": datetime.now() + timedelta(hours=1) if request.schedule else None
        }
        
        return AutomationWorkflowResponse(**workflow)
        
    except Exception as e:
        logger.error(f"Error creating automation workflow: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Helper Functions
async def _generate_comprehensive_insights(dashboard_data: Dict[str, Any], time_horizon: int) -> List:
    """Generate comprehensive AI insights."""
    try:
        advanced_ai = await get_advanced_ai_service()
        
        insights = []
        
        # Project health insights
        if dashboard_data.get("projects"):
            project_data = [
                {
                    "name": p.get("name", ""),
                    "percent_complete": p.get("percent_complete", 0),
                    "budget_amount": p.get("budget_amount", 0),
                    "status_id": p.get("status_id", 0),
                    "created_at": datetime.now().isoformat()
                }
                for p in dashboard_data["projects"]
            ]
            
            trend_insight = await advanced_ai.analyze_trends(project_data)
            insights.append(trend_insight)
            
            pattern_insight = await advanced_ai.detect_patterns(project_data)
            insights.append(pattern_insight)
        
        return insights
        
    except Exception as e:
        logger.error(f"Error generating comprehensive insights: {e}")
        return []


async def _generate_comprehensive_predictions(dashboard_data: Dict[str, Any], time_horizon: int) -> List:
    """Generate comprehensive predictions."""
    try:
        advanced_ai = await get_advanced_ai_service()
        
        predictions = []
        
        # Project completion predictions
        if dashboard_data.get("projects"):
            project_data = [
                {
                    "percent_complete": p.get("percent_complete", 0),
                    "due_date": p.get("due_date", ""),
                    "start_date": p.get("start_date", ""),
                    "budget_amount": p.get("budget_amount", 0)
                }
                for p in dashboard_data["projects"]
            ]
            
            completion_preds = await advanced_ai.generate_predictions(
                data=project_data,
                prediction_type=PredictionType.PROJECT_COMPLETION,
                time_horizon=time_horizon
            )
            predictions.extend(completion_preds)
            
            budget_preds = await advanced_ai.generate_predictions(
                data=project_data,
                prediction_type=PredictionType.BUDGET_CONSUMPTION,
                time_horizon=time_horizon
            )
            predictions.extend(budget_preds)
        
        return predictions
        
    except Exception as e:
        logger.error(f"Error generating comprehensive predictions: {e}")
        return []


async def _generate_intelligent_recommendations(dashboard_data: Dict[str, Any], time_horizon: int) -> List[str]:
    """Generate intelligent recommendations."""
    try:
        advanced_ai = await get_advanced_ai_service()
        
        context = {
            "dashboard_data": dashboard_data,
            "time_horizon": time_horizon,
            "timestamp": datetime.now().isoformat()
        }
        
        recommendations = await advanced_ai.generate_smart_recommendations(context)
        
        return recommendations
        
    except Exception as e:
        logger.error(f"Error generating intelligent recommendations: {e}")
        return ["Review current processes", "Implement monitoring systems"]


async def _generate_automation_suggestions(dashboard_data: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Generate automation suggestions."""
    try:
        suggestions = []
        
        # Suggest data sync automation
        if dashboard_data.get("projects"):
            suggestions.append({
                "name": "Project Data Sync",
                "description": "Automatically sync project data to vector database",
                "frequency": "daily",
                "priority": "medium"
            })
        
        # Suggest report automation
        suggestions.append({
            "name": "Automated Reporting",
            "description": "Generate and distribute reports automatically",
            "frequency": "weekly",
            "priority": "high"
        })
        
        # Suggest notification automation
        suggestions.append({
            "name": "Smart Notifications",
            "description": "Send intelligent notifications based on project status",
            "frequency": "real-time",
            "priority": "high"
        })
        
        return suggestions
        
    except Exception as e:
        logger.error(f"Error generating automation suggestions: {e}")
        return []


async def _get_data_for_analysis(analysis_type: str, filters: Dict[str, Any], db: Session) -> List[Dict[str, Any]]:
    """Get data for analysis."""
    try:
        if analysis_type in ["comprehensive", "trend", "pattern", "anomaly"]:
            from app.models.main_tables import Project
            projects = db.query(Project).all()
            
            data = []
            for project in projects:
                data.append({
                    "id": project.id,
                    "name": project.name,
                    "percent_complete": project.percent_complete,
                    "budget_amount": float(project.budget_amount) if project.budget_amount else 0,
                    "status_id": project.status_id,
                    "priority_id": project.priority_id,
                    "created_at": project.created_at.isoformat() if project.created_at else datetime.now().isoformat(),
                    "value": project.percent_complete  # For trend analysis
                })
            
            return data
        
        return []
        
    except Exception as e:
        logger.error(f"Error getting data for analysis: {e}")
        return []


async def _get_data_for_predictions(filters: Dict[str, Any], db: Session) -> List[Dict[str, Any]]:
    """Get data for predictions."""
    try:
        from app.models.main_tables import Project
        projects = db.query(Project).all()
        
        data = []
        for project in projects:
            data.append({
                "id": project.id,
                "name": project.name,
                "percent_complete": project.percent_complete,
                "budget_amount": float(project.budget_amount) if project.budget_amount else 0,
                "start_date": project.start_date.isoformat() if project.start_date else None,
                "due_date": project.due_date.isoformat() if project.due_date else None,
                "status_id": project.status_id,
                "priority_id": project.priority_id
            })
        
        return data
        
    except Exception as e:
        logger.error(f"Error getting data for predictions: {e}")
        return []


async def _enhance_recommendation_context(context: Dict[str, Any], db: Session) -> Dict[str, Any]:
    """Enhance recommendation context with current data."""
    try:
        # Add current project metrics
        from app.models.main_tables import Project
        projects = db.query(Project).all()
        
        enhanced_context = {
            **context,
            "total_projects": len(projects),
            "active_projects": len([p for p in projects if p.is_active]),
            "avg_completion": np.mean([p.percent_complete for p in projects]) if projects else 0,
            "total_budget": sum([float(p.budget_amount) if p.budget_amount else 0 for p in projects])
        }
        
        return enhanced_context
        
    except Exception as e:
        logger.error(f"Error enhancing recommendation context: {e}")
        return context


async def _identify_risk_factors(predictions: Dict[str, List], data: List[Dict[str, Any]]) -> List[str]:
    """Identify risk factors from predictions."""
    try:
        risk_factors = []
        
        # Analyze prediction confidence levels
        for pred_type, preds in predictions.items():
            if preds:
                avg_confidence = np.mean([pred.get("confidence", 0.5) for pred in preds])
                if avg_confidence < 0.6:
                    risk_factors.append(f"Low confidence in {pred_type} predictions")
        
        # Analyze data patterns
        if data:
            completion_rates = [d.get("percent_complete", 0) for d in data]
            if np.mean(completion_rates) < 30:
                risk_factors.append("Low overall project completion rates")
        
        return risk_factors
        
    except Exception as e:
        logger.error(f"Error identifying risk factors: {e}")
        return ["Data analysis error"]


async def _identify_opportunities(predictions: Dict[str, List], data: List[Dict[str, Any]]) -> List[str]:
    """Identify opportunities from predictions."""
    try:
        opportunities = []
        
        # Analyze prediction trends
        for pred_type, preds in predictions.items():
            if preds:
                avg_confidence = np.mean([pred.get("confidence", 0.5) for pred in preds])
                if avg_confidence > 0.8:
                    opportunities.append(f"High confidence in {pred_type} predictions")
        
        # Analyze data patterns
        if data:
            completion_rates = [d.get("percent_complete", 0) for d in data]
            if np.mean(completion_rates) > 70:
                opportunities.append("High project completion rates indicate good performance")
        
        return opportunities
        
    except Exception as e:
        logger.error(f"Error identifying opportunities: {e}")
        return ["Data analysis error"]


async def _generate_related_queries(query: str, sources: List) -> List[str]:
    """Generate related queries based on the original query and sources."""
    try:
        ai_service = await get_ai_service()
        
        source_summaries = [source.content[:200] for source in sources[:3]]
        
        messages = [
            AIMessage(
                role="system",
                content="""You are a helpful assistant that generates related queries.
                Based on the original query and source content, generate 3-5 related questions that users might want to ask.
                Make them specific and actionable."""
            ),
            AIMessage(
                role="user",
                content=f"""Original query: {query}
                
                Source content summaries:
                {chr(10).join(source_summaries)}
                
                Generate related queries."""
            )
        ]
        
        response = await ai_service.ollama_client.generate_text(
            model="llama3:8b",
            messages=messages,
            temperature=0.4
        )
        
        # Parse related queries
        related_queries = []
        lines = response.content.split('\n')
        for line in lines:
            if line.strip() and ('?' in line or line.strip().startswith(('1.', '2.', '3.', '4.', '5.'))):
                clean_query = line.strip().lstrip('123456789. •-').strip()
                if clean_query:
                    related_queries.append(clean_query)
        
        return related_queries[:5]
        
    except Exception as e:
        logger.error(f"Error generating related queries: {e}")
        return []


async def _identify_knowledge_gaps(query: str, sources: List) -> List[str]:
    """Identify knowledge gaps based on query and available sources."""
    try:
        if not sources:
            return ["No relevant information found for this query"]
        
        # Simple gap identification based on source confidence
        gaps = []
        
        if len(sources) < 3:
            gaps.append("Limited information available")
        
        # Check source relevance (simplified)
        source_confidences = [getattr(source, 'similarity_score', 0.5) for source in sources]
        avg_confidence = np.mean(source_confidences) if source_confidences else 0.5
        
        if avg_confidence < 0.6:
            gaps.append("Low relevance of available information")
        
        return gaps
        
    except Exception as e:
        logger.error(f"Error identifying knowledge gaps: {e}")
        return ["Analysis error"]

"""
AI Dashboard API Endpoints
Provides AI-enhanced dashboard features
"""

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from datetime import datetime

from app.core.ai_client import get_ai_service
from app.core.ai_copilot import get_copilot, CopilotTaskType, CopilotPriority
from app.core.logging import get_logger, log_api_endpoint
from app.database import get_db
from sqlalchemy.orm import Session

logger = get_logger(__name__)
router = APIRouter()


# Request/Response Models
class AIDashboardRequest(BaseModel):
    """AI dashboard request."""
    user_id: Optional[str] = None
    include_insights: bool = True
    include_predictions: bool = True
    include_recommendations: bool = True


class AIDashboardResponse(BaseModel):
    """AI dashboard response."""
    dashboard_data: Dict[str, Any]
    ai_insights: Optional[Dict[str, Any]] = None
    predictions: Optional[Dict[str, Any]] = None
    recommendations: Optional[Dict[str, Any]] = None
    timestamp: datetime


class AIInsightsRequest(BaseModel):
    """AI insights request."""
    insight_type: str = Field(..., description="Type of insight to generate")
    filters: Optional[Dict[str, Any]] = None


class AIInsightsResponse(BaseModel):
    """AI insights response."""
    insights: Dict[str, Any]
    insight_type: str
    model_used: str
    tokens_used: int
    response_time: float
    timestamp: datetime


class AIPredictionRequest(BaseModel):
    """AI prediction request."""
    prediction_type: str = Field(..., description="Type of prediction to generate")
    time_horizon: int = Field(default=30, description="Prediction time horizon in days")
    filters: Optional[Dict[str, Any]] = None


class AIPredictionResponse(BaseModel):
    """AI prediction response."""
    predictions: Dict[str, Any]
    prediction_type: str
    time_horizon: int
    confidence_score: float
    model_used: str
    tokens_used: int
    response_time: float
    timestamp: datetime


class AIRecommendationRequest(BaseModel):
    """AI recommendation request."""
    recommendation_type: str = Field(..., description="Type of recommendation to generate")
    context: Optional[Dict[str, Any]] = None


class AIRecommendationResponse(BaseModel):
    """AI recommendation response."""
    recommendations: Dict[str, Any]
    recommendation_type: str
    priority: str
    model_used: str
    tokens_used: int
    response_time: float
    timestamp: datetime


class AIProjectSummaryRequest(BaseModel):
    """AI project summary request."""
    project_id: str
    summary_type: str = Field(default="comprehensive", description="Type of summary to generate")


class AIProjectSummaryResponse(BaseModel):
    """AI project summary response."""
    summary: Dict[str, Any]
    project_id: str
    summary_type: str
    model_used: str
    tokens_used: int
    response_time: float
    timestamp: datetime


# AI Dashboard Endpoints
@router.post("/ai-dashboard", response_model=AIDashboardResponse)
@log_api_endpoint
async def get_ai_dashboard(
    request: AIDashboardRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Get AI-enhanced dashboard data."""
    try:
        # Get basic dashboard data
        from app.api.v1.endpoints.dashboards import get_all_projects_dashboard
        dashboard_data = await get_all_projects_dashboard(db)
        
        ai_insights = None
        predictions = None
        recommendations = None
        
        # Generate AI insights if requested
        if request.include_insights:
            try:
                ai_insights = await _generate_dashboard_insights(dashboard_data)
            except Exception as e:
                logger.warning(f"Failed to generate AI insights: {e}")
        
        # Generate predictions if requested
        if request.include_predictions:
            try:
                predictions = await _generate_dashboard_predictions(dashboard_data)
            except Exception as e:
                logger.warning(f"Failed to generate predictions: {e}")
        
        # Generate recommendations if requested
        if request.include_recommendations:
            try:
                recommendations = await _generate_dashboard_recommendations(dashboard_data)
            except Exception as e:
                logger.warning(f"Failed to generate recommendations: {e}")
        
        return AIDashboardResponse(
            dashboard_data=dashboard_data,
            ai_insights=ai_insights,
            predictions=predictions,
            recommendations=recommendations,
            timestamp=datetime.now()
        )
    except Exception as e:
        logger.error(f"Error getting AI dashboard: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/insights", response_model=AIInsightsResponse)
@log_api_endpoint
async def generate_insights(
    request: AIInsightsRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Generate AI insights for dashboard."""
    try:
        # Get relevant data based on insight type
        data = await _get_data_for_insights(request.insight_type, request.filters, db)
        
        # Generate insights using AI
        ai_service = await get_ai_service()
        
        if request.insight_type == "project_health":
            insights_result = await ai_service.generate_project_insights(data)
        elif request.insight_type == "portfolio_analysis":
            insights_result = await ai_service.generate_project_insights(data)
        elif request.insight_type == "resource_utilization":
            insights_result = await _generate_resource_insights(data)
        elif request.insight_type == "budget_analysis":
            insights_result = await _generate_budget_insights(data)
        else:
            raise HTTPException(status_code=400, detail=f"Unknown insight type: {request.insight_type}")
        
        return AIInsightsResponse(
            insights=insights_result.get("insights", {}),
            insight_type=request.insight_type,
            model_used=insights_result.get("model_used", "unknown"),
            tokens_used=insights_result.get("tokens_used", 0),
            response_time=insights_result.get("response_time", 0),
            timestamp=datetime.now()
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating insights: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/predictions", response_model=AIPredictionResponse)
@log_api_endpoint
async def generate_predictions(
    request: AIPredictionRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Generate AI predictions for dashboard."""
    try:
        # Get relevant data based on prediction type
        data = await _get_data_for_predictions(request.prediction_type, request.filters, db)
        
        # Generate predictions using AI
        predictions_result = await _generate_predictions(
            request.prediction_type,
            data,
            request.time_horizon
        )
        
        return AIPredictionResponse(
            predictions=predictions_result.get("predictions", {}),
            prediction_type=request.prediction_type,
            time_horizon=request.time_horizon,
            confidence_score=predictions_result.get("confidence_score", 0.7),
            model_used=predictions_result.get("model_used", "unknown"),
            tokens_used=predictions_result.get("tokens_used", 0),
            response_time=predictions_result.get("response_time", 0),
            timestamp=datetime.now()
        )
    except Exception as e:
        logger.error(f"Error generating predictions: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/recommendations", response_model=AIRecommendationResponse)
@log_api_endpoint
async def generate_recommendations(
    request: AIRecommendationRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Generate AI recommendations for dashboard."""
    try:
        # Get relevant data based on recommendation type
        data = await _get_data_for_recommendations(request.recommendation_type, request.context, db)
        
        # Generate recommendations using AI
        recommendations_result = await _generate_recommendations(
            request.recommendation_type,
            data,
            request.context
        )
        
        return AIRecommendationResponse(
            recommendations=recommendations_result.get("recommendations", {}),
            recommendation_type=request.recommendation_type,
            priority=recommendations_result.get("priority", "medium"),
            model_used=recommendations_result.get("model_used", "unknown"),
            tokens_used=recommendations_result.get("tokens_used", 0),
            response_time=recommendations_result.get("response_time", 0),
            timestamp=datetime.now()
        )
    except Exception as e:
        logger.error(f"Error generating recommendations: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/project-summary", response_model=AIProjectSummaryResponse)
@log_api_endpoint
async def generate_project_summary(
    request: AIProjectSummaryRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Generate AI-powered project summary."""
    try:
        # Get project data from database
        from app.models.main_tables import Project
        project = db.query(Project).filter(Project.id == request.project_id).first()
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")
        
        # Convert project to dict
        project_data = {
            "id": project.id,
            "project_id": project.project_id,
            "name": project.name,
            "description": project.description,
            "status_id": project.status_id,
            "priority_id": project.priority_id,
            "criticality_id": project.criticality_id,
            "portfolio_id": project.portfolio_id,
            "budget_amount": float(project.budget_amount) if project.budget_amount else 0,
            "start_date": project.start_date.isoformat() if project.start_date else None,
            "due_date": project.due_date.isoformat() if project.due_date else None,
            "percent_complete": project.percent_complete,
            "project_manager": project.project_manager,
            "is_active": project.is_active
        }
        
        # Generate summary using AI
        ai_service = await get_ai_service()
        summary_result = await ai_service.analyze_project_health(project_data)
        
        return AIProjectSummaryResponse(
            summary=summary_result.get("analysis", {}),
            project_id=request.project_id,
            summary_type=request.summary_type,
            model_used=summary_result.get("model_used", "unknown"),
            tokens_used=summary_result.get("tokens_used", 0),
            response_time=summary_result.get("response_time", 0),
            timestamp=datetime.now()
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating project summary: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Helper Functions
async def _generate_dashboard_insights(dashboard_data: Dict[str, Any]) -> Dict[str, Any]:
    """Generate dashboard insights using AI."""
    try:
        ai_service = await get_ai_service()
        
        # Prepare dashboard summary
        dashboard_summary = f"""
        Dashboard Analysis Request:
        Total Projects: {len(dashboard_data.get('projects', []))}
        Total Features: {len(dashboard_data.get('features', []))}
        Total Backlogs: {len(dashboard_data.get('backlogs', []))}
        Total Resources: {len(dashboard_data.get('resources', []))}
        
        Metrics:
        - Total Projects: {dashboard_data.get('metrics', {}).get('total_projects', 0)}
        - Active Projects: {dashboard_data.get('metrics', {}).get('active_projects', 0)}
        - Total Features: {dashboard_data.get('metrics', {}).get('total_features', 0)}
        - Total Backlogs: {dashboard_data.get('metrics', {}).get('total_backlogs', 0)}
        - Total Resources: {dashboard_data.get('metrics', {}).get('total_resources', 0)}
        """
        
        # Generate insights
        insights_result = await ai_service.generate_project_insights(dashboard_data.get('projects', []))
        
        return insights_result
    except Exception as e:
        logger.error(f"Error generating dashboard insights: {e}")
        return {
            "error": str(e),
            "insights": {
                "portfolio_health": 70,
                "top_risks": ["Analysis failed"],
                "resource_insights": ["Manual review required"],
                "timeline_analysis": ["Unable to analyze"],
                "budget_analysis": ["Data unavailable"],
                "strategic_recommendations": ["Contact support"]
            }
        }


async def _generate_dashboard_predictions(dashboard_data: Dict[str, Any]) -> Dict[str, Any]:
    """Generate dashboard predictions using AI."""
    try:
        ai_service = await get_ai_service()
        
        # Prepare prediction prompt
        prediction_prompt = f"""
        Dashboard Prediction Request:
        Current Metrics:
        - Total Projects: {dashboard_data.get('metrics', {}).get('total_projects', 0)}
        - Active Projects: {dashboard_data.get('metrics', {}).get('active_projects', 0)}
        - Total Features: {dashboard_data.get('metrics', {}).get('total_features', 0)}
        - Total Backlogs: {dashboard_data.get('metrics', {}).get('total_backlogs', 0)}
        - Total Resources: {dashboard_data.get('metrics', {}).get('total_resources', 0)}
        
        Please provide predictions for:
        1. Project completion rates
        2. Resource utilization trends
        3. Budget consumption patterns
        4. Risk factors
        5. Timeline projections
        
        Respond in JSON format with predictions and confidence scores.
        """
        
        messages = [
            AIMessage(
                role="system",
                content="""You are a project management prediction expert. Analyze the dashboard data and provide predictions.
                Focus on:
                1. Project completion rates
                2. Resource utilization trends
                3. Budget consumption patterns
                4. Risk factors
                5. Timeline projections
                
                Provide confidence scores (0-1) for each prediction.
                Respond in JSON format."""
            ),
            AIMessage(role="user", content=prediction_prompt)
        ]
        
        response = await ai_service.ollama_client.generate_text(
            model="llama3:8b",
            messages=messages,
            temperature=0.3
        )
        
        # Parse response
        try:
            predictions = json.loads(response.content)
        except json.JSONDecodeError:
            predictions = {
                "project_completion": {"prediction": "70%", "confidence": 0.7},
                "resource_utilization": {"prediction": "85%", "confidence": 0.6},
                "budget_consumption": {"prediction": "90%", "confidence": 0.8},
                "risk_factors": {"prediction": "Medium", "confidence": 0.7},
                "timeline_projections": {"prediction": "On track", "confidence": 0.6}
            }
        
        return {
            "predictions": predictions,
            "model_used": response.model,
            "tokens_used": response.tokens_used,
            "response_time": response.response_time,
            "timestamp": response.timestamp
        }
    except Exception as e:
        logger.error(f"Error generating dashboard predictions: {e}")
        return {
            "error": str(e),
            "predictions": {
                "project_completion": {"prediction": "Unknown", "confidence": 0.5},
                "resource_utilization": {"prediction": "Unknown", "confidence": 0.5},
                "budget_consumption": {"prediction": "Unknown", "confidence": 0.5},
                "risk_factors": {"prediction": "Unknown", "confidence": 0.5},
                "timeline_projections": {"prediction": "Unknown", "confidence": 0.5}
            }
        }


async def _generate_dashboard_recommendations(dashboard_data: Dict[str, Any]) -> Dict[str, Any]:
    """Generate dashboard recommendations using AI."""
    try:
        ai_service = await get_ai_service()
        
        # Prepare recommendation prompt
        recommendation_prompt = f"""
        Dashboard Recommendation Request:
        Current Metrics:
        - Total Projects: {dashboard_data.get('metrics', {}).get('total_projects', 0)}
        - Active Projects: {dashboard_data.get('metrics', {}).get('active_projects', 0)}
        - Total Features: {dashboard_data.get('metrics', {}).get('total_features', 0)}
        - Total Backlogs: {dashboard_data.get('metrics', {}).get('total_backlogs', 0)}
        - Total Resources: {dashboard_data.get('metrics', {}).get('total_resources', 0)}
        
        Please provide recommendations for:
        1. Project optimization
        2. Resource allocation
        3. Risk mitigation
        4. Process improvement
        5. Strategic planning
        
        Respond in JSON format with recommendations and priority levels.
        """
        
        messages = [
            AIMessage(
                role="system",
                content="""You are a project management consultant. Analyze the dashboard data and provide actionable recommendations.
                Focus on:
                1. Project optimization
                2. Resource allocation
                3. Risk mitigation
                4. Process improvement
                5. Strategic planning
                
                Provide priority levels (Low/Medium/High/Critical) for each recommendation.
                Respond in JSON format."""
            ),
            AIMessage(role="user", content=recommendation_prompt)
        ]
        
        response = await ai_service.ollama_client.generate_text(
            model="llama3:8b",
            messages=messages,
            temperature=0.4
        )
        
        # Parse response
        try:
            recommendations = json.loads(response.content)
        except json.JSONDecodeError:
            recommendations = {
                "project_optimization": {"recommendation": "Review project timelines", "priority": "Medium"},
                "resource_allocation": {"recommendation": "Balance workload distribution", "priority": "High"},
                "risk_mitigation": {"recommendation": "Implement risk monitoring", "priority": "High"},
                "process_improvement": {"recommendation": "Streamline approval processes", "priority": "Medium"},
                "strategic_planning": {"recommendation": "Align projects with business goals", "priority": "Critical"}
            }
        
        return {
            "recommendations": recommendations,
            "model_used": response.model,
            "tokens_used": response.tokens_used,
            "response_time": response.response_time,
            "timestamp": response.timestamp
        }
    except Exception as e:
        logger.error(f"Error generating dashboard recommendations: {e}")
        return {
            "error": str(e),
            "recommendations": {
                "project_optimization": {"recommendation": "Manual review required", "priority": "Medium"},
                "resource_allocation": {"recommendation": "Contact resource manager", "priority": "Medium"},
                "risk_mitigation": {"recommendation": "Risk assessment needed", "priority": "Medium"},
                "process_improvement": {"recommendation": "Process review required", "priority": "Medium"},
                "strategic_planning": {"recommendation": "Strategic planning session needed", "priority": "Medium"}
            }
        }


async def _get_data_for_insights(insight_type: str, filters: Optional[Dict[str, Any]], db: Session) -> List[Dict[str, Any]]:
    """Get data for insights generation."""
    try:
        if insight_type == "project_health":
            from app.models.main_tables import Project
            projects = db.query(Project).all()
            return [{
                "id": p.id,
                "name": p.name,
                "status_id": p.status_id,
                "priority_id": p.priority_id,
                "percent_complete": p.percent_complete,
                "budget_amount": float(p.budget_amount) if p.budget_amount else 0,
                "start_date": p.start_date.isoformat() if p.start_date else None,
                "due_date": p.due_date.isoformat() if p.due_date else None
            } for p in projects]
        
        elif insight_type == "portfolio_analysis":
            from app.models.main_tables import Project
            projects = db.query(Project).all()
            return [{
                "id": p.id,
                "name": p.name,
                "portfolio_id": p.portfolio_id,
                "status_id": p.status_id,
                "priority_id": p.priority_id,
                "percent_complete": p.percent_complete,
                "budget_amount": float(p.budget_amount) if p.budget_amount else 0
            } for p in projects]
        
        elif insight_type == "resource_utilization":
            from app.models.main_tables import Resource
            resources = db.query(Resource).all()
            return [{
                "id": r.id,
                "name": r.name,
                "role": r.role,
                "skills": r.skills,
                "experience_level": r.experience_level,
                "availability_percentage": r.availability_percentage,
                "is_active": r.is_active
            } for r in resources]
        
        elif insight_type == "budget_analysis":
            from app.models.main_tables import Project
            projects = db.query(Project).all()
            return [{
                "id": p.id,
                "name": p.name,
                "budget_amount": float(p.budget_amount) if p.budget_amount else 0,
                "percent_complete": p.percent_complete,
                "start_date": p.start_date.isoformat() if p.start_date else None,
                "due_date": p.due_date.isoformat() if p.due_date else None
            } for p in projects]
        
        else:
            return []
    except Exception as e:
        logger.error(f"Error getting data for insights: {e}")
        return []


async def _get_data_for_predictions(prediction_type: str, filters: Optional[Dict[str, Any]], db: Session) -> List[Dict[str, Any]]:
    """Get data for predictions generation."""
    try:
        if prediction_type == "project_completion":
            from app.models.main_tables import Project
            projects = db.query(Project).all()
            return [{
                "id": p.id,
                "name": p.name,
                "percent_complete": p.percent_complete,
                "start_date": p.start_date.isoformat() if p.start_date else None,
                "due_date": p.due_date.isoformat() if p.due_date else None,
                "status_id": p.status_id
            } for p in projects]
        
        elif prediction_type == "resource_utilization":
            from app.models.main_tables import Resource
            resources = db.query(Resource).all()
            return [{
                "id": r.id,
                "name": r.name,
                "role": r.role,
                "availability_percentage": r.availability_percentage,
                "is_active": r.is_active
            } for r in resources]
        
        elif prediction_type == "budget_consumption":
            from app.models.main_tables import Project
            projects = db.query(Project).all()
            return [{
                "id": p.id,
                "name": p.name,
                "budget_amount": float(p.budget_amount) if p.budget_amount else 0,
                "percent_complete": p.percent_complete,
                "start_date": p.start_date.isoformat() if p.start_date else None,
                "due_date": p.due_date.isoformat() if p.due_date else None
            } for p in projects]
        
        else:
            return []
    except Exception as e:
        logger.error(f"Error getting data for predictions: {e}")
        return []


async def _get_data_for_recommendations(recommendation_type: str, context: Optional[Dict[str, Any]], db: Session) -> List[Dict[str, Any]]:
    """Get data for recommendations generation."""
    try:
        if recommendation_type == "project_optimization":
            from app.models.main_tables import Project
            projects = db.query(Project).all()
            return [{
                "id": p.id,
                "name": p.name,
                "status_id": p.status_id,
                "priority_id": p.priority_id,
                "percent_complete": p.percent_complete,
                "budget_amount": float(p.budget_amount) if p.budget_amount else 0,
                "start_date": p.start_date.isoformat() if p.start_date else None,
                "due_date": p.due_date.isoformat() if p.due_date else None
            } for p in projects]
        
        elif recommendation_type == "resource_allocation":
            from app.models.main_tables import Resource
            resources = db.query(Resource).all()
            return [{
                "id": r.id,
                "name": r.name,
                "role": r.role,
                "skills": r.skills,
                "experience_level": r.experience_level,
                "availability_percentage": r.availability_percentage,
                "is_active": r.is_active
            } for r in resources]
        
        else:
            return []
    except Exception as e:
        logger.error(f"Error getting data for recommendations: {e}")
        return []


async def _generate_resource_insights(data: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Generate resource insights using AI."""
    try:
        ai_service = await get_ai_service()
        
        # Prepare resource summary
        resource_summary = f"""
        Resource Analysis Request:
        Total Resources: {len(data)}
        
        Resource Summary:
        """
        
        for i, resource in enumerate(data[:10]):  # Limit to first 10 resources
            resource_summary += f"""
        Resource {i+1}:
        - Name: {resource.get('name', 'Unknown')}
        - Role: {resource.get('role', 'Unknown')}
        - Skills: {', '.join(resource.get('skills', []))}
        - Experience: {resource.get('experience_level', 'Unknown')}
        - Availability: {resource.get('availability_percentage', 0)}%
        """
        
        messages = [
            AIMessage(
                role="system",
                content="""You are a resource management expert. Analyze the resource data and provide insights.
                Focus on:
                1. Skill distribution
                2. Availability patterns
                3. Experience levels
                4. Utilization trends
                5. Capacity planning
                
                Respond in JSON format with insights."""
            ),
            AIMessage(role="user", content=resource_summary)
        ]
        
        response = await ai_service.ollama_client.generate_text(
            model="llama3:8b",
            messages=messages,
            temperature=0.4
        )
        
        # Parse response
        try:
            insights = json.loads(response.content)
        except json.JSONDecodeError:
            insights = {
                "skill_distribution": {"analysis": "Manual review required"},
                "availability_patterns": {"analysis": "Pattern analysis needed"},
                "experience_levels": {"analysis": "Experience review required"},
                "utilization_trends": {"analysis": "Utilization analysis needed"},
                "capacity_planning": {"analysis": "Capacity planning required"}
            }
        
        return {
            "insights": insights,
            "model_used": response.model,
            "tokens_used": response.tokens_used,
            "response_time": response.response_time,
            "timestamp": response.timestamp
        }
    except Exception as e:
        logger.error(f"Error generating resource insights: {e}")
        return {
            "error": str(e),
            "insights": {
                "skill_distribution": {"analysis": "Analysis failed"},
                "availability_patterns": {"analysis": "Manual review required"},
                "experience_levels": {"analysis": "Experience review required"},
                "utilization_trends": {"analysis": "Utilization analysis needed"},
                "capacity_planning": {"analysis": "Capacity planning required"}
            }
        }


async def _generate_budget_insights(data: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Generate budget insights using AI."""
    try:
        ai_service = await get_ai_service()
        
        # Prepare budget summary
        budget_summary = f"""
        Budget Analysis Request:
        Total Projects: {len(data)}
        
        Budget Summary:
        """
        
        total_budget = sum(project.get('budget_amount', 0) for project in data)
        avg_completion = sum(project.get('percent_complete', 0) for project in data) / len(data) if data else 0
        
        budget_summary += f"""
        Total Budget: ${total_budget:,.2f}
        Average Completion: {avg_completion:.1f}%
        """
        
        for i, project in enumerate(data[:10]):  # Limit to first 10 projects
            budget_summary += f"""
        Project {i+1}:
        - Name: {project.get('name', 'Unknown')}
        - Budget: ${project.get('budget_amount', 0):,.2f}
        - Completion: {project.get('percent_complete', 0)}%
        """
        
        messages = [
            AIMessage(
                role="system",
                content="""You are a financial analysis expert. Analyze the budget data and provide insights.
                Focus on:
                1. Budget utilization
                2. Cost efficiency
                3. Spending patterns
                4. Risk factors
                5. Optimization opportunities
                
                Respond in JSON format with insights."""
            ),
            AIMessage(role="user", content=budget_summary)
        ]
        
        response = await ai_service.ollama_client.generate_text(
            model="llama3:8b",
            messages=messages,
            temperature=0.3
        )
        
        # Parse response
        try:
            insights = json.loads(response.content)
        except json.JSONDecodeError:
            insights = {
                "budget_utilization": {"analysis": "Manual review required"},
                "cost_efficiency": {"analysis": "Efficiency analysis needed"},
                "spending_patterns": {"analysis": "Spending pattern analysis required"},
                "risk_factors": {"analysis": "Risk assessment needed"},
                "optimization_opportunities": {"analysis": "Optimization review required"}
            }
        
        return {
            "insights": insights,
            "model_used": response.model,
            "tokens_used": response.tokens_used,
            "response_time": response.response_time,
            "timestamp": response.timestamp
        }
    except Exception as e:
        logger.error(f"Error generating budget insights: {e}")
        return {
            "error": str(e),
            "insights": {
                "budget_utilization": {"analysis": "Analysis failed"},
                "cost_efficiency": {"analysis": "Manual review required"},
                "spending_patterns": {"analysis": "Spending pattern analysis required"},
                "risk_factors": {"analysis": "Risk assessment needed"},
                "optimization_opportunities": {"analysis": "Optimization review required"}
            }
        }


async def _generate_predictions(prediction_type: str, data: List[Dict[str, Any]], time_horizon: int) -> Dict[str, Any]:
    """Generate predictions using AI."""
    try:
        ai_service = await get_ai_service()
        
        # Prepare prediction prompt
        prediction_prompt = f"""
        Prediction Request:
        Type: {prediction_type}
        Time Horizon: {time_horizon} days
        Data Points: {len(data)}
        
        Please provide predictions for the next {time_horizon} days.
        """
        
        messages = [
            AIMessage(
                role="system",
                content="""You are a prediction expert. Analyze the data and provide predictions.
                Focus on:
                1. Trend analysis
                2. Pattern recognition
                3. Future projections
                4. Confidence levels
                5. Risk factors
                
                Provide confidence scores (0-1) for each prediction.
                Respond in JSON format."""
            ),
            AIMessage(role="user", content=prediction_prompt)
        ]
        
        response = await ai_service.ollama_client.generate_text(
            model="llama3:8b",
            messages=messages,
            temperature=0.3
        )
        
        # Parse response
        try:
            predictions = json.loads(response.content)
        except json.JSONDecodeError:
            predictions = {
                "trend_analysis": {"prediction": "Stable", "confidence": 0.7},
                "pattern_recognition": {"prediction": "Consistent", "confidence": 0.6},
                "future_projections": {"prediction": "Positive", "confidence": 0.7},
                "risk_factors": {"prediction": "Low", "confidence": 0.8}
            }
        
        return {
            "predictions": predictions,
            "model_used": response.model,
            "tokens_used": response.tokens_used,
            "response_time": response.response_time,
            "timestamp": response.timestamp
        }
    except Exception as e:
        logger.error(f"Error generating predictions: {e}")
        return {
            "error": str(e),
            "predictions": {
                "trend_analysis": {"prediction": "Unknown", "confidence": 0.5},
                "pattern_recognition": {"prediction": "Unknown", "confidence": 0.5},
                "future_projections": {"prediction": "Unknown", "confidence": 0.5},
                "risk_factors": {"prediction": "Unknown", "confidence": 0.5}
            }
        }


async def _generate_recommendations(recommendation_type: str, data: List[Dict[str, Any]], context: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    """Generate recommendations using AI."""
    try:
        ai_service = await get_ai_service()
        
        # Prepare recommendation prompt
        recommendation_prompt = f"""
        Recommendation Request:
        Type: {recommendation_type}
        Data Points: {len(data)}
        Context: {context or 'No specific context'}
        
        Please provide actionable recommendations.
        """
        
        messages = [
            AIMessage(
                role="system",
                content="""You are a management consultant. Analyze the data and provide actionable recommendations.
                Focus on:
                1. Immediate actions
                2. Strategic initiatives
                3. Process improvements
                4. Risk mitigation
                5. Optimization opportunities
                
                Provide priority levels (Low/Medium/High/Critical) for each recommendation.
                Respond in JSON format."""
            ),
            AIMessage(role="user", content=recommendation_prompt)
        ]
        
        response = await ai_service.ollama_client.generate_text(
            model="llama3:8b",
            messages=messages,
            temperature=0.4
        )
        
        # Parse response
        try:
            recommendations = json.loads(response.content)
        except json.JSONDecodeError:
            recommendations = {
                "immediate_actions": {"recommendation": "Review current processes", "priority": "Medium"},
                "strategic_initiatives": {"recommendation": "Align with business goals", "priority": "High"},
                "process_improvements": {"recommendation": "Streamline workflows", "priority": "Medium"},
                "risk_mitigation": {"recommendation": "Implement monitoring", "priority": "High"},
                "optimization_opportunities": {"recommendation": "Identify bottlenecks", "priority": "Medium"}
            }
        
        return {
            "recommendations": recommendations,
            "model_used": response.model,
            "tokens_used": response.tokens_used,
            "response_time": response.response_time,
            "timestamp": response.timestamp
        }
    except Exception as e:
        logger.error(f"Error generating recommendations: {e}")
        return {
            "error": str(e),
            "recommendations": {
                "immediate_actions": {"recommendation": "Manual review required", "priority": "Medium"},
                "strategic_initiatives": {"recommendation": "Strategic planning needed", "priority": "Medium"},
                "process_improvements": {"recommendation": "Process review required", "priority": "Medium"},
                "risk_mitigation": {"recommendation": "Risk assessment needed", "priority": "Medium"},
                "optimization_opportunities": {"recommendation": "Optimization review required", "priority": "Medium"}
            }
        }

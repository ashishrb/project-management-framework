"""
AI API Endpoints
Provides REST API for AI-powered features
"""

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from datetime import datetime

from app.core.ai_client import get_ai_service, OllamaClient, AIMessage
from app.core.ai_copilot import get_copilot, CopilotTask, CopilotTaskType, CopilotPriority
from app.core.logging import get_logger, log_api_endpoint
from app.database import get_db
from sqlalchemy.orm import Session

logger = get_logger(__name__)
router = APIRouter()


# Request/Response Models
class AIHealthResponse(BaseModel):
    """AI service health response."""
    status: str
    models: List[Dict[str, Any]]
    timestamp: datetime


class AIModelInfo(BaseModel):
    """AI model information."""
    name: str
    size: int
    modified_at: str
    description: Optional[str] = None
    max_tokens: Optional[int] = None
    use_cases: Optional[List[str]] = None


class AIGenerateRequest(BaseModel):
    """AI text generation request."""
    model: str = Field(..., description="Model to use for generation")
    messages: List[Dict[str, str]] = Field(..., description="List of messages")
    temperature: float = Field(default=0.7, ge=0.0, le=2.0, description="Temperature for generation")
    max_tokens: Optional[int] = Field(default=None, description="Maximum tokens to generate")


class AIGenerateResponse(BaseModel):
    """AI text generation response."""
    content: str
    model: str
    tokens_used: int
    response_time: float
    timestamp: datetime


class AIEmbeddingRequest(BaseModel):
    """AI embedding request."""
    text: str = Field(..., description="Text to embed")
    model: str = Field(default="nomic-embed-text:latest", description="Embedding model to use")


class AIEmbeddingResponse(BaseModel):
    """AI embedding response."""
    embedding: List[float]
    model: str
    timestamp: datetime


class CopilotTaskRequest(BaseModel):
    """Copilot task request."""
    type: CopilotTaskType
    priority: CopilotPriority = CopilotPriority.MEDIUM
    title: str
    description: str
    context: Dict[str, Any]


class CopilotTaskResponse(BaseModel):
    """Copilot task response."""
    task_id: str
    status: str
    created_at: datetime
    estimated_completion: Optional[datetime] = None


class ProjectAnalysisRequest(BaseModel):
    """Project analysis request."""
    project_id: str
    priority: CopilotPriority = CopilotPriority.MEDIUM


class ProjectAnalysisResponse(BaseModel):
    """Project analysis response."""
    task_id: str
    status: str
    analysis: Optional[Dict[str, Any]] = None
    created_at: datetime


class PortfolioInsightsRequest(BaseModel):
    """Portfolio insights request."""
    portfolio_id: str
    priority: CopilotPriority = CopilotPriority.HIGH


class PortfolioInsightsResponse(BaseModel):
    """Portfolio insights response."""
    task_id: str
    status: str
    insights: Optional[Dict[str, Any]] = None
    created_at: datetime


class CodeReviewRequest(BaseModel):
    """Code review request."""
    code_id: str
    code_content: str
    review_type: str = "general"
    priority: CopilotPriority = CopilotPriority.MEDIUM


class CodeReviewResponse(BaseModel):
    """Code review response."""
    task_id: str
    status: str
    suggestions: Optional[str] = None
    created_at: datetime


class DocumentationRequest(BaseModel):
    """Documentation generation request."""
    doc_id: str
    content: str
    doc_type: str = "API"
    priority: CopilotPriority = CopilotPriority.LOW


class DocumentationResponse(BaseModel):
    """Documentation generation response."""
    task_id: str
    status: str
    documentation: Optional[str] = None
    created_at: datetime


class RiskAssessmentRequest(BaseModel):
    """Risk assessment request."""
    project_id: str
    priority: CopilotPriority = CopilotPriority.HIGH


class RiskAssessmentResponse(BaseModel):
    """Risk assessment response."""
    task_id: str
    status: str
    risk_analysis: Optional[Dict[str, Any]] = None
    created_at: datetime


class ResourceOptimizationRequest(BaseModel):
    """Resource optimization request."""
    priority: CopilotPriority = CopilotPriority.MEDIUM


class ResourceOptimizationResponse(BaseModel):
    """Resource optimization response."""
    task_id: str
    status: str
    optimization_analysis: Optional[Dict[str, Any]] = None
    created_at: datetime


class TimelineAnalysisRequest(BaseModel):
    """Timeline analysis request."""
    project_id: str
    priority: CopilotPriority = CopilotPriority.MEDIUM


class TimelineAnalysisResponse(BaseModel):
    """Timeline analysis response."""
    task_id: str
    status: str
    timeline_analysis: Optional[Dict[str, Any]] = None
    created_at: datetime


class BudgetAnalysisRequest(BaseModel):
    """Budget analysis request."""
    project_id: str
    priority: CopilotPriority = CopilotPriority.HIGH


class BudgetAnalysisResponse(BaseModel):
    """Budget analysis response."""
    task_id: str
    status: str
    budget_analysis: Optional[Dict[str, Any]] = None
    created_at: datetime


class SemanticSearchRequest(BaseModel):
    """Semantic search request."""
    query: str
    documents: List[str]
    top_k: int = Field(default=5, ge=1, le=20)


class SemanticSearchResponse(BaseModel):
    """Semantic search response."""
    results: List[Dict[str, Any]]
    query: str
    total_documents: int
    timestamp: datetime


# AI Service Endpoints
@router.get("/health", response_model=AIHealthResponse)
async def get_ai_health():
    """Get AI service health status."""
    try:
        async with OllamaClient() as client:
            health = await client.check_health()
            return AIHealthResponse(**health)
    except Exception as e:
        logger.error(f"Error checking AI health: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/models", response_model=List[AIModelInfo])
async def get_ai_models():
    """Get available AI models."""
    try:
        async with OllamaClient() as client:
            models = await client.get_available_models()
            return [AIModelInfo(**model) for model in models]
    except Exception as e:
        logger.error(f"Error getting AI models: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/generate", response_model=AIGenerateResponse)
async def generate_text(request: AIGenerateRequest):
    """Generate text using AI model."""
    try:
        ai_service = await get_ai_service()
        
        # Convert messages to AIMessage objects
        messages = [AIMessage(role=msg["role"], content=msg["content"]) for msg in request.messages]
        
        response = await ai_service.ollama_client.generate_text(
            model=request.model,
            messages=messages,
            temperature=request.temperature,
            max_tokens=request.max_tokens
        )
        
        return AIGenerateResponse(
            content=response.content,
            model=response.model,
            tokens_used=response.tokens_used,
            response_time=response.response_time,
            timestamp=response.timestamp
        )
    except Exception as e:
        logger.error(f"Error generating text: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/embeddings", response_model=AIEmbeddingResponse)
async def generate_embeddings(request: AIEmbeddingRequest):
    """Generate embeddings for text."""
    try:
        async with OllamaClient() as client:
            embedding = await client.generate_embeddings(request.text, request.model)
            return AIEmbeddingResponse(
                embedding=embedding,
                model=request.model,
                timestamp=datetime.now()
            )
    except Exception as e:
        logger.error(f"Error generating embeddings: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/semantic-search", response_model=SemanticSearchResponse)
async def semantic_search(request: SemanticSearchRequest):
    """Perform semantic search using embeddings."""
    try:
        ai_service = await get_ai_service()
        
        results = await ai_service.semantic_search(
            query=request.query,
            documents=request.documents,
            top_k=request.top_k
        )
        
        return SemanticSearchResponse(
            results=results,
            query=request.query,
            total_documents=len(request.documents),
            timestamp=datetime.now()
        )
    except Exception as e:
        logger.error(f"Error performing semantic search: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Copilot Endpoints
@router.get("/copilot/tasks", response_model=List[CopilotTask])
async def get_copilot_tasks():
    """Get active copilot tasks."""
    try:
        copilot = await get_copilot()
        return copilot.get_active_tasks()
    except Exception as e:
        logger.error(f"Error getting copilot tasks: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/copilot/tasks/history", response_model=List[CopilotTask])
async def get_copilot_task_history(limit: int = 50):
    """Get copilot task history."""
    try:
        copilot = await get_copilot()
        return copilot.get_task_history(limit)
    except Exception as e:
        logger.error(f"Error getting copilot task history: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/copilot/tasks/{task_id}", response_model=CopilotTask)
async def get_copilot_task(task_id: str):
    """Get specific copilot task."""
    try:
        copilot = await get_copilot()
        task = copilot.get_task_by_id(task_id)
        if not task:
            raise HTTPException(status_code=404, detail="Task not found")
        return task
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting copilot task: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/copilot/tasks/{task_id}/cancel")
async def cancel_copilot_task(task_id: str):
    """Cancel a copilot task."""
    try:
        copilot = await get_copilot()
        success = await copilot.cancel_task(task_id)
        if not success:
            raise HTTPException(status_code=404, detail="Task not found or already completed")
        return {"message": "Task cancelled successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error cancelling copilot task: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/copilot/statistics")
async def get_copilot_statistics():
    """Get copilot statistics."""
    try:
        copilot = await get_copilot()
        return copilot.get_statistics()
    except Exception as e:
        logger.error(f"Error getting copilot statistics: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Project Analysis Endpoints
@router.post("/copilot/project-analysis", response_model=ProjectAnalysisResponse)
async def analyze_project_health(
    request: ProjectAnalysisRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Analyze project health using AI."""
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
        
        # Start analysis task
        copilot = await get_copilot()
        task = await copilot.analyze_project_health(
            project_id=request.project_id,
            project_data=project_data,
            priority=request.priority
        )
        
        return ProjectAnalysisResponse(
            task_id=task.id,
            status=task.status,
            analysis=task.result,
            created_at=task.created_at
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error analyzing project health: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/copilot/portfolio-insights", response_model=PortfolioInsightsResponse)
async def generate_portfolio_insights(
    request: PortfolioInsightsRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Generate portfolio insights using AI."""
    try:
        # Get projects data from database
        from app.models.main_tables import Project
        projects = db.query(Project).filter(Project.portfolio_id == request.portfolio_id).all()
        
        # Convert projects to dict
        projects_data = []
        for project in projects:
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
            projects_data.append(project_data)
        
        # Start insights generation task
        copilot = await get_copilot()
        task = await copilot.generate_portfolio_insights(
            portfolio_id=request.portfolio_id,
            projects_data=projects_data,
            priority=request.priority
        )
        
        return PortfolioInsightsResponse(
            task_id=task.id,
            status=task.status,
            insights=task.result,
            created_at=task.created_at
        )
    except Exception as e:
        logger.error(f"Error generating portfolio insights: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/copilot/code-review", response_model=CodeReviewResponse)
async def perform_code_review(request: CodeReviewRequest):
    """Perform AI-powered code review."""
    try:
        copilot = await get_copilot()
        task = await copilot.perform_code_review(
            code_id=request.code_id,
            code_content=request.code_content,
            review_type=request.review_type,
            priority=request.priority
        )
        
        return CodeReviewResponse(
            task_id=task.id,
            status=task.status,
            suggestions=task.result.get("suggestions") if task.result else None,
            created_at=task.created_at
        )
    except Exception as e:
        logger.error(f"Error performing code review: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/copilot/documentation", response_model=DocumentationResponse)
async def generate_documentation(request: DocumentationRequest):
    """Generate documentation using AI."""
    try:
        copilot = await get_copilot()
        task = await copilot.generate_documentation(
            doc_id=request.doc_id,
            content=request.content,
            doc_type=request.doc_type,
            priority=request.priority
        )
        
        return DocumentationResponse(
            task_id=task.id,
            status=task.status,
            documentation=task.result.get("documentation") if task.result else None,
            created_at=task.created_at
        )
    except Exception as e:
        logger.error(f"Error generating documentation: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/copilot/risk-assessment", response_model=RiskAssessmentResponse)
async def assess_risks(
    request: RiskAssessmentRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Assess project risks using AI."""
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
        
        # Start risk assessment task
        copilot = await get_copilot()
        task = await copilot.assess_risks(
            project_id=request.project_id,
            project_data=project_data,
            priority=request.priority
        )
        
        return RiskAssessmentResponse(
            task_id=task.id,
            status=task.status,
            risk_analysis=task.result,
            created_at=task.created_at
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error assessing risks: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/copilot/resource-optimization", response_model=ResourceOptimizationResponse)
async def optimize_resources(
    request: ResourceOptimizationRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Optimize resource allocation using AI."""
    try:
        # Get resources data from database
        from app.models.main_tables import Resource
        resources = db.query(Resource).all()
        
        # Convert resources to dict
        resources_data = []
        for resource in resources:
            resource_data = {
                "id": resource.id,
                "name": resource.name,
                "email": resource.email,
                "role": resource.role,
                "skills": resource.skills,
                "experience_level": resource.experience_level,
                "is_active": resource.is_active,
                "availability_percentage": resource.availability_percentage
            }
            resources_data.append(resource_data)
        
        # Start optimization task
        copilot = await get_copilot()
        task = await copilot.optimize_resources(
            resource_data=resources_data,
            priority=request.priority
        )
        
        return ResourceOptimizationResponse(
            task_id=task.id,
            status=task.status,
            optimization_analysis=task.result,
            created_at=task.created_at
        )
    except Exception as e:
        logger.error(f"Error optimizing resources: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/copilot/timeline-analysis", response_model=TimelineAnalysisResponse)
async def analyze_timeline(
    request: TimelineAnalysisRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Analyze project timeline using AI."""
    try:
        # Get project data from database
        from app.models.main_tables import Project
        project = db.query(Project).filter(Project.id == request.project_id).first()
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")
        
        # Prepare timeline data
        timeline_data = {
            "start_date": project.start_date.isoformat() if project.start_date else None,
            "due_date": project.due_date.isoformat() if project.due_date else None,
            "percent_complete": project.percent_complete,
            "milestones": [],  # TODO: Add milestones from database
            "dependencies": []  # TODO: Add dependencies from database
        }
        
        # Start timeline analysis task
        copilot = await get_copilot()
        task = await copilot.analyze_timeline(
            project_id=request.project_id,
            timeline_data=timeline_data,
            priority=request.priority
        )
        
        return TimelineAnalysisResponse(
            task_id=task.id,
            status=task.status,
            timeline_analysis=task.result,
            created_at=task.created_at
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error analyzing timeline: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/copilot/budget-analysis", response_model=BudgetAnalysisResponse)
async def analyze_budget(
    request: BudgetAnalysisRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Analyze project budget using AI."""
    try:
        # Get project data from database
        from app.models.main_tables import Project
        project = db.query(Project).filter(Project.id == request.project_id).first()
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")
        
        # Prepare budget data
        budget_data = {
            "total_budget": float(project.budget_amount) if project.budget_amount else 0,
            "spent_amount": 0,  # TODO: Calculate from actual spending
            "remaining_budget": float(project.budget_amount) if project.budget_amount else 0,
            "utilization_percentage": 0,  # TODO: Calculate utilization
            "cost_categories": {}  # TODO: Add cost categories
        }
        
        # Start budget analysis task
        copilot = await get_copilot()
        task = await copilot.analyze_budget(
            project_id=request.project_id,
            budget_data=budget_data,
            priority=request.priority
        )
        
        return BudgetAnalysisResponse(
            task_id=task.id,
            status=task.status,
            budget_analysis=task.result,
            created_at=task.created_at
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error analyzing budget: {e}")
        raise HTTPException(status_code=500, detail=str(e))

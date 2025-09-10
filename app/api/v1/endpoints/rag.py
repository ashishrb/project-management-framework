"""
RAG (Retrieval-Augmented Generation) API Endpoints
Provides RAG capabilities and vector database management
"""

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from datetime import datetime

from app.core.vector_db import (
    get_vector_db, get_rag_service, Document, QueryResult, RAGResponse
)
from app.core.advanced_ai import (
    get_advanced_ai_service, AIInsightType, PredictionType, AutomationTask
)
from app.core.logging import get_logger, log_api_endpoint
from app.database import get_db
from sqlalchemy.orm import Session

logger = get_logger(__name__)
router = APIRouter()


# Request/Response Models
class DocumentRequest(BaseModel):
    """Document creation request."""
    content: str = Field(..., description="Document content")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Document metadata")
    collection_name: str = Field(..., description="Target collection name")


class DocumentResponse(BaseModel):
    """Document response."""
    id: str
    content: str
    metadata: Dict[str, Any]
    collection_name: str
    created_at: datetime


class BulkDocumentRequest(BaseModel):
    """Bulk document creation request."""
    documents: List[DocumentRequest]
    collection_name: str = Field(..., description="Target collection name")
    generate_embeddings: bool = Field(default=True, description="Generate embeddings")


class BulkDocumentResponse(BaseModel):
    """Bulk document response."""
    added_count: int
    collection_name: str
    document_ids: List[str]


class SearchRequest(BaseModel):
    """Document search request."""
    query: str = Field(..., description="Search query")
    collection_name: str = Field(..., description="Collection to search")
    top_k: int = Field(default=5, ge=1, le=20, description="Number of results")
    filter_metadata: Optional[Dict[str, Any]] = Field(default=None, description="Metadata filters")


class SearchResponse(BaseModel):
    """Search response."""
    results: List[QueryResult]
    query: str
    collection_name: str
    total_results: int
    timestamp: datetime


class RAGRequest(BaseModel):
    """RAG query request."""
    query: str = Field(..., description="Question to answer")
    collection_names: Optional[List[str]] = Field(default=None, description="Collections to search")
    top_k: int = Field(default=5, ge=1, le=20, description="Number of documents to retrieve")
    model: str = Field(default="llama3:8b", description="Model to use for generation")
    temperature: float = Field(default=0.3, ge=0.0, le=2.0, description="Generation temperature")
    include_sources: bool = Field(default=True, description="Include source documents")


class RAGResponseModel(BaseModel):
    """RAG response model."""
    answer: str
    sources: List[Document]
    confidence: float
    query: str
    model_used: str
    tokens_used: int
    response_time: float
    timestamp: datetime
    
    class Config:
        protected_namespaces = ()


class SummaryRequest(BaseModel):
    """Summary generation request."""
    collection_name: str = Field(..., description="Collection to summarize")
    filter_metadata: Optional[Dict[str, Any]] = Field(default=None, description="Metadata filters")
    model: str = Field(default="llama3:8b", description="Model to use")
    max_documents: int = Field(default=20, ge=1, le=100, description="Maximum documents to include")


class SummaryResponse(BaseModel):
    """Summary response."""
    summary: str
    sources: List[Document]
    collection_name: str
    document_count: int
    model_used: str
    tokens_used: int
    timestamp: datetime
    
    class Config:
        protected_namespaces = ()


class CollectionStatsResponse(BaseModel):
    """Collection statistics response."""
    collection_name: str
    document_count: int
    description: str
    metadata_fields: List[str]
    timestamp: datetime


class AllStatsResponse(BaseModel):
    """All collections statistics response."""
    collections: Dict[str, CollectionStatsResponse]
    total_documents: int
    total_collections: int
    timestamp: datetime


class InsightRequest(BaseModel):
    """AI insight generation request."""
    insight_type: AIInsightType
    data: List[Dict[str, Any]]
    parameters: Optional[Dict[str, Any]] = Field(default_factory=dict)


class PredictionRequest(BaseModel):
    """Prediction generation request."""
    prediction_type: PredictionType
    data: List[Dict[str, Any]]
    time_horizon: int = Field(default=30, ge=1, le=365)


class RecommendationRequest(BaseModel):
    """Smart recommendation request."""
    context: Dict[str, Any]
    recommendation_type: str = Field(default="general")


class AutomationRequest(BaseModel):
    """Automation task request."""
    task_name: str
    task_type: str
    parameters: Dict[str, Any]


# Vector Database Endpoints
@router.post("/documents", response_model=DocumentResponse)
async def add_document(request: DocumentRequest):
    """Add a document to the vector database."""
    try:
        vector_db = await get_vector_db()
        
        document = Document(
            content=request.content,
            metadata=request.metadata
        )
        
        success = await vector_db.add_document(
            collection_name=request.collection_name,
            document=document,
            generate_embedding=True
        )
        
        if not success:
            raise HTTPException(status_code=500, detail="Failed to add document")
        
        return DocumentResponse(
            id=document.id,
            content=document.content,
            metadata=document.metadata,
            collection_name=request.collection_name,
            created_at=document.created_at
        )
        
    except Exception as e:
        logger.error(f"Error adding document: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/documents/bulk", response_model=BulkDocumentResponse)
async def add_documents_bulk(request: BulkDocumentRequest):
    """Add multiple documents to the vector database."""
    try:
        vector_db = await get_vector_db()
        
        documents = []
        for doc_req in request.documents:
            document = Document(
                content=doc_req.content,
                metadata=doc_req.metadata
            )
            documents.append(document)
        
        added_count = await vector_db.add_documents(
            collection_name=request.collection_name,
            documents=documents,
            generate_embeddings=request.generate_embeddings
        )
        
        document_ids = [doc.id for doc in documents[:added_count]]
        
        return BulkDocumentResponse(
            added_count=added_count,
            collection_name=request.collection_name,
            document_ids=document_ids
        )
        
    except Exception as e:
        logger.error(f"Error adding documents in bulk: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/documents/{collection_name}/{document_id}", response_model=DocumentResponse)
async def get_document(collection_name: str, document_id: str):
    """Get a specific document by ID."""
    try:
        vector_db = await get_vector_db()
        
        document = await vector_db.get_document(collection_name, document_id)
        
        if not document:
            raise HTTPException(status_code=404, detail="Document not found")
        
        return DocumentResponse(
            id=document.id,
            content=document.content,
            metadata=document.metadata,
            collection_name=collection_name,
            created_at=document.created_at
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting document: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/documents/{collection_name}/{document_id}")
async def update_document(
    collection_name: str,
    document_id: str,
    content: Optional[str] = None,
    metadata: Optional[Dict[str, Any]] = None
):
    """Update a document in the vector database."""
    try:
        vector_db = await get_vector_db()
        
        success = await vector_db.update_document(
            collection_name=collection_name,
            document_id=document_id,
            content=content,
            metadata=metadata,
            regenerate_embedding=True
        )
        
        if not success:
            raise HTTPException(status_code=404, detail="Document not found or update failed")
        
        return {"message": "Document updated successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating document: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/documents/{collection_name}/{document_id}")
async def delete_document(collection_name: str, document_id: str):
    """Delete a document from the vector database."""
    try:
        vector_db = await get_vector_db()
        
        success = await vector_db.delete_document(collection_name, document_id)
        
        if not success:
            raise HTTPException(status_code=404, detail="Document not found or deletion failed")
        
        return {"message": "Document deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting document: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/search", response_model=SearchResponse)
async def search_documents(request: SearchRequest):
    """Search for similar documents."""
    try:
        vector_db = await get_vector_db()
        
        results = await vector_db.search_documents(
            collection_name=request.collection_name,
            query=request.query,
            top_k=request.top_k,
            filter_metadata=request.filter_metadata
        )
        
        return SearchResponse(
            results=results,
            query=request.query,
            collection_name=request.collection_name,
            total_results=len(results),
            timestamp=datetime.now()
        )
        
    except Exception as e:
        logger.error(f"Error searching documents: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# RAG Endpoints
@router.post("/rag/query", response_model=RAGResponseModel)
async def rag_query(request: RAGRequest):
    """Generate an answer using RAG."""
    try:
        rag_service = await get_rag_service()
        
        response = await rag_service.generate_answer(
            query=request.query,
            collection_names=request.collection_names,
            top_k=request.top_k,
            model=request.model,
            temperature=request.temperature,
            include_sources=request.include_sources
        )
        
        return RAGResponseModel(
            answer=response.answer,
            sources=response.sources,
            confidence=response.confidence,
            query=response.query,
            model_used=response.model_used,
            tokens_used=response.tokens_used,
            response_time=response.response_time,
            timestamp=response.timestamp
        )
        
    except Exception as e:
        logger.error(f"Error in RAG query: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/rag/summary", response_model=SummaryResponse)
async def generate_summary(request: SummaryRequest):
    """Generate a summary of documents in a collection."""
    try:
        rag_service = await get_rag_service()
        
        response = await rag_service.generate_summary(
            collection_name=request.collection_name,
            filter_metadata=request.filter_metadata,
            model=request.model,
            max_documents=request.max_documents
        )
        
        return SummaryResponse(
            summary=response.answer,
            sources=response.sources,
            collection_name=request.collection_name,
            document_count=len(response.sources),
            model_used=response.model_used,
            tokens_used=response.tokens_used,
            timestamp=response.timestamp
        )
        
    except Exception as e:
        logger.error(f"Error generating summary: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Collection Management Endpoints
@router.get("/collections/stats", response_model=AllStatsResponse)
async def get_all_collection_stats():
    """Get statistics for all collections."""
    try:
        vector_db = await get_vector_db()
        
        stats = await vector_db.get_all_collection_stats()
        
        return AllStatsResponse(
            collections={
                name: CollectionStatsResponse(
                    collection_name=name,
                    document_count=data.get("document_count", 0),
                    description=data.get("description", ""),
                    metadata_fields=data.get("metadata_fields", []),
                    timestamp=data.get("timestamp", datetime.now())
                )
                for name, data in stats.get("collections", {}).items()
            },
            total_documents=stats.get("total_documents", 0),
            total_collections=stats.get("total_collections", 0),
            timestamp=stats.get("timestamp", datetime.now())
        )
        
    except Exception as e:
        logger.error(f"Error getting collection stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/collections/{collection_name}/stats", response_model=CollectionStatsResponse)
async def get_collection_stats(collection_name: str):
    """Get statistics for a specific collection."""
    try:
        vector_db = await get_vector_db()
        
        stats = await vector_db.get_collection_stats(collection_name)
        
        if not stats:
            raise HTTPException(status_code=404, detail="Collection not found")
        
        return CollectionStatsResponse(
            collection_name=stats["collection_name"],
            document_count=stats["document_count"],
            description=stats["description"],
            metadata_fields=stats["metadata_fields"],
            timestamp=stats["timestamp"]
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting collection stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/collections/{collection_name}")
async def clear_collection(collection_name: str):
    """Clear all documents from a collection."""
    try:
        vector_db = await get_vector_db()
        
        success = await vector_db.clear_collection(collection_name)
        
        if not success:
            raise HTTPException(status_code=404, detail="Collection not found or clear failed")
        
        return {"message": f"Collection '{collection_name}' cleared successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error clearing collection: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/collections/reset")
async def reset_database():
    """Reset the entire vector database."""
    try:
        vector_db = await get_vector_db()
        
        success = await vector_db.reset_database()
        
        if not success:
            raise HTTPException(status_code=500, detail="Database reset failed")
        
        return {"message": "Vector database reset successfully"}
        
    except Exception as e:
        logger.error(f"Error resetting database: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Advanced AI Endpoints
@router.post("/insights/generate")
async def generate_insight(request: InsightRequest):
    """Generate AI insights from data."""
    try:
        advanced_ai = await get_advanced_ai_service()
        
        if request.insight_type == AIInsightType.TREND_ANALYSIS:
            insight = await advanced_ai.analyze_trends(
                data=request.data,
                **request.parameters
            )
        elif request.insight_type == AIInsightType.PATTERN_DETECTION:
            insight = await advanced_ai.detect_patterns(
                data=request.data,
                **request.parameters
            )
        elif request.insight_type == AIInsightType.ANOMALY_DETECTION:
            insight = await advanced_ai.detect_anomalies(
                data=request.data,
                **request.parameters
            )
        else:
            raise HTTPException(status_code=400, detail=f"Unsupported insight type: {request.insight_type}")
        
        return insight
        
    except Exception as e:
        logger.error(f"Error generating insight: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/predictions/generate")
async def generate_predictions(request: PredictionRequest):
    """Generate predictions from data."""
    try:
        advanced_ai = await get_advanced_ai_service()
        
        predictions = await advanced_ai.generate_predictions(
            data=request.data,
            prediction_type=request.prediction_type,
            time_horizon=request.time_horizon
        )
        
        return {"predictions": predictions, "count": len(predictions)}
        
    except Exception as e:
        logger.error(f"Error generating predictions: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/recommendations/generate")
async def generate_recommendations(request: RecommendationRequest):
    """Generate smart recommendations."""
    try:
        advanced_ai = await get_advanced_ai_service()
        
        recommendations = await advanced_ai.generate_smart_recommendations(
            context=request.context,
            recommendation_type=request.recommendation_type
        )
        
        return {"recommendations": recommendations, "count": len(recommendations)}
        
    except Exception as e:
        logger.error(f"Error generating recommendations: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/automation/execute")
async def execute_automation_task(request: AutomationRequest):
    """Execute an automation task."""
    try:
        advanced_ai = await get_advanced_ai_service()
        
        task = await advanced_ai.automate_task(
            task_name=request.task_name,
            task_type=request.task_type,
            parameters=request.parameters
        )
        
        return task
        
    except Exception as e:
        logger.error(f"Error executing automation task: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/insights")
async def get_insights(insight_type: Optional[AIInsightType] = None):
    """Get AI insights."""
    try:
        advanced_ai = await get_advanced_ai_service()
        
        insights = advanced_ai.get_insights(insight_type)
        
        return {"insights": insights, "count": len(insights)}
        
    except Exception as e:
        logger.error(f"Error getting insights: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/predictions")
async def get_predictions(prediction_type: Optional[PredictionType] = None):
    """Get predictions."""
    try:
        advanced_ai = await get_advanced_ai_service()
        
        predictions = advanced_ai.get_predictions(prediction_type)
        
        return {"predictions": predictions, "count": len(predictions)}
        
    except Exception as e:
        logger.error(f"Error getting predictions: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/automation/tasks")
async def get_automation_tasks(status: Optional[str] = None):
    """Get automation tasks."""
    try:
        advanced_ai = await get_advanced_ai_service()
        
        tasks = advanced_ai.get_automation_tasks(status)
        
        return {"tasks": tasks, "count": len(tasks)}
        
    except Exception as e:
        logger.error(f"Error getting automation tasks: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/statistics")
async def get_advanced_ai_statistics():
    """Get advanced AI service statistics."""
    try:
        advanced_ai = await get_advanced_ai_service()
        
        stats = advanced_ai.get_statistics()
        
        return stats
        
    except Exception as e:
        logger.error(f"Error getting statistics: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Data Integration Endpoints
@router.post("/data/projects/sync")
async def sync_projects_data(
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Sync project data to vector database."""
    try:
        vector_db = await get_vector_db()
        
        # Get projects from database
        from app.models.main_tables import Project
        projects = db.query(Project).all()
        
        documents = []
        for project in projects:
            content = f"""
            Project: {project.name}
            Description: {project.description or 'No description'}
            Status: {project.status_id}
            Priority: {project.priority_id}
            Budget: ${project.budget_amount or 0:,.2f}
            Progress: {project.percent_complete}%
            Manager: {project.project_manager or 'Not assigned'}
            Start Date: {project.start_date or 'Not set'}
            Due Date: {project.due_date or 'Not set'}
            """
            
            document = Document(
                content=content.strip(),
                metadata={
                    "project_id": project.id,
                    "project_name": project.name,
                    "status_id": project.status_id,
                    "priority_id": project.priority_id,
                    "budget_amount": float(project.budget_amount) if project.budget_amount else 0,
                    "percent_complete": project.percent_complete,
                    "project_manager": project.project_manager,
                    "is_active": project.is_active
                }
            )
            documents.append(document)
        
        # Add documents to vector database
        added_count = await vector_db.add_documents(
            collection_name="projects",
            documents=documents,
            generate_embeddings=True
        )
        
        return {
            "message": f"Synced {added_count} projects to vector database",
            "synced_count": added_count,
            "total_projects": len(projects)
        }
        
    except Exception as e:
        logger.error(f"Error syncing projects data: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/data/features/sync")
async def sync_features_data(
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Sync features data to vector database."""
    try:
        vector_db = await get_vector_db()
        
        # Get features from database
        from app.models.main_tables import Feature
        features = db.query(Feature).all()
        
        documents = []
        for feature in features:
            content = f"""
            Feature: {feature.feature_name}
            Description: {feature.description or 'No description'}
            Project ID: {feature.project_id}
            Status: {feature.status_id}
            Priority: {feature.priority_id}
            Business Value: {feature.business_value or 'Not specified'}
            Acceptance Criteria: {feature.acceptance_criteria or 'Not specified'}
            Complexity: {feature.complexity or 'Not specified'}
            Effort Estimate: {feature.effort_estimate or 0} hours
            Progress: {feature.percent_complete}%
            """
            
            document = Document(
                content=content.strip(),
                metadata={
                    "feature_id": feature.id,
                    "feature_name": feature.feature_name,
                    "project_id": feature.project_id,
                    "status_id": feature.status_id,
                    "priority_id": feature.priority_id,
                    "business_value": feature.business_value,
                    "complexity": feature.complexity,
                    "effort_estimate": feature.effort_estimate,
                    "percent_complete": feature.percent_complete,
                    "is_active": feature.is_active
                }
            )
            documents.append(document)
        
        # Add documents to vector database
        added_count = await vector_db.add_documents(
            collection_name="features",
            documents=documents,
            generate_embeddings=True
        )
        
        return {
            "message": f"Synced {added_count} features to vector database",
            "synced_count": added_count,
            "total_features": len(features)
        }
        
    except Exception as e:
        logger.error(f"Error syncing features data: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/data/resources/sync")
async def sync_resources_data(
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Sync resources data to vector database."""
    try:
        vector_db = await get_vector_db()
        
        # Get resources from database
        from app.models.main_tables import Resource
        resources = db.query(Resource).all()
        
        documents = []
        for resource in resources:
            content = f"""
            Resource: {resource.name}
            Email: {resource.email}
            Role: {resource.role}
            Skills: {', '.join(resource.skills) if resource.skills else 'No skills specified'}
            Experience Level: {resource.experience_level or 'Not specified'}
            Availability: {resource.availability_percentage}%
            Active: {resource.is_active}
            """
            
            document = Document(
                content=content.strip(),
                metadata={
                    "resource_id": resource.id,
                    "name": resource.name,
                    "email": resource.email,
                    "role": resource.role,
                    "skills": resource.skills,
                    "experience_level": resource.experience_level,
                    "availability_percentage": resource.availability_percentage,
                    "is_active": resource.is_active
                }
            )
            documents.append(document)
        
        # Add documents to vector database
        added_count = await vector_db.add_documents(
            collection_name="resources",
            documents=documents,
            generate_embeddings=True
        )
        
        return {
            "message": f"Synced {added_count} resources to vector database",
            "synced_count": added_count,
            "total_resources": len(resources)
        }
        
    except Exception as e:
        logger.error(f"Error syncing resources data: {e}")
        raise HTTPException(status_code=500, detail=str(e))

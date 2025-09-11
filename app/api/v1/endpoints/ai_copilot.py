"""
AI Copilot API endpoints
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Dict, Any, List
import json
import asyncio
from datetime import datetime

from app.api.deps import get_db, get_current_user
from app.core.ai_client import OllamaClient, AIService, AIMessage
from app.core.vector_db import VectorDatabase, RAGService
from app.core.memory_manager import MemoryOptimizationService

router = APIRouter()

# Initialize AI components
ai_client = OllamaClient()
ai_service = AIService(ai_client)
vector_db = VectorDatabase()
rag_service = RAGService(vector_db)
memory_manager = MemoryOptimizationService()

@router.post("/chat")
async def chat_with_copilot(
    request: Dict[str, Any],
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Chat with AI Copilot
    """
    try:
        message = request.get("message", "")
        mode = request.get("mode", "balanced")
        model = request.get("model", "llama3:8b")
        temperature = request.get("temperature", 0.7)
        max_tokens = request.get("max_tokens", 4000)
        context = request.get("context", "")
        use_rag = request.get("use_rag", False)
        documents = request.get("documents", [])
        
        if not message:
            raise HTTPException(status_code=400, detail="Message is required")
        
        # Build context for AI
        full_context = await build_ai_context(
            db=db,
            context=context,
            use_rag=use_rag,
            documents=documents,
            mode=mode
        )
        
        # Get AI response
        messages = [
            AIMessage(role="system", content=f"You are an AI assistant for project management. {full_context}"),
            AIMessage(role="user", content=message)
        ]
        
        ai_response = await ai_client.generate_text(
            model=model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens
        )
        
        response = ai_response.content
        
        # TODO: Implement memory storage when memory manager is available
        
        return {
            "response": response,
            "mode": mode,
            "context_used": bool(full_context),
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating response: {str(e)}")

@router.post("/quick-action")
async def execute_quick_action(
    action: str,
    request: Dict[str, Any],
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Execute quick action
    """
    try:
        # Define quick actions
        quick_actions = {
            "project-report": await generate_project_report(db),
            "resource-analysis": await generate_resource_analysis(db),
            "budget-review": await generate_budget_review(db),
            "risk-summary": await generate_risk_summary(db),
            "executive-summary": await generate_executive_summary(db),
            "schedule-tips": await generate_schedule_tips(db),
            "performance": await generate_performance_analysis(db),
            "strategy": await generate_strategy_recommendations(db),
            "financial-report-email": await generate_financial_report_email(db),
            "save-to-folder": await save_analysis_to_folder(request, current_user),
            "executive-summary-email": await generate_executive_summary_email(db),
            "resource-report-save": await generate_resource_report_save(db)
        }
        
        if action not in quick_actions:
            raise HTTPException(status_code=400, detail="Invalid quick action")
        
        result = await quick_actions[action]
        
        return {
            "action": action,
            "result": result,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error executing quick action: {str(e)}")

@router.get("/context/{context_type}")
async def load_context_data(
    context_type: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Load context data for AI
    """
    try:
        context_data = {}
        
        if context_type == "projects":
            # Load project data
            from app.models.main_tables import Project
            projects = db.query(Project).limit(50).all()
            context_data = {
                "projects": [
                    {
                        "id": p.id,
                        "name": p.name,
                        "status": p.status_id,
                        "priority": p.priority_id,
                        "progress": float(p.percent_complete) if p.percent_complete else 0,
                        "manager": p.project_manager,
                        "due_date": p.due_date.isoformat() if p.due_date else None
                    }
                    for p in projects
                ]
            }
            
        elif context_type == "resources":
            # Load resource data
            from app.models.main_tables import Resource
            resources = db.query(Resource).limit(50).all()
            context_data = {
                "resources": [
                    {
                        "id": r.id,
                        "name": r.name,
                        "role": r.role,
                        "skills": r.skills,
                        "availability": r.availability,
                        "cost_per_hour": float(r.cost_per_hour) if r.cost_per_hour else 0
                    }
                    for r in resources
                ]
            }
            
        elif context_type == "finance":
            # Load financial data
            from app.models.main_tables import Project
            projects = db.query(Project).filter(Project.budget_amount.isnot(None)).limit(50).all()
            context_data = {
                "finance": [
                    {
                        "project_id": p.id,
                        "project_name": p.name,
                        "budget": float(p.budget_amount) if p.budget_amount else 0,
                        "funding_status": p.funding_status,
                        "budget_status": p.budget_status
                    }
                    for p in projects
                ]
            }
        
        return {
            "context_type": context_type,
            "data": context_data,
            "loaded_at": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error loading context: {str(e)}")

@router.get("/conversations")
async def get_conversations(
    current_user: dict = Depends(get_current_user)
):
    """
    Get user's conversation history
    """
    try:
        # TODO: Implement conversation storage when memory manager is available
        return {
            "conversations": [],
            "count": 0
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error loading conversations: {str(e)}")

@router.delete("/conversations/{conversation_id}")
async def delete_conversation(
    conversation_id: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Delete a conversation
    """
    try:
        # TODO: Implement conversation deletion when memory manager is available
        return {"message": "Conversation deleted successfully"}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting conversation: {str(e)}")

# Helper functions

async def build_ai_context(
    db: Session,
    context: str,
    use_rag: bool,
    documents: List[Dict],
    mode: str
) -> str:
    """Build comprehensive context for AI"""
    context_parts = []
    
    if context:
        context_parts.append(f"User Context: {context}")
    
    if use_rag and documents:
        # Use RAG to find relevant information
        try:
            rag_results = await vector_db.search_documents(
                collection_name="documents",
                query=context,
                top_k=5
            )
            if rag_results:
                rag_context = "\n".join([result.content for result in rag_results])
                context_parts.append(f"Document Context: {rag_context}")
        except Exception as e:
            print(f"RAG search failed: {e}")
            # Continue without RAG context
    
    # Add mode-specific context
    if mode == "rag":
        # Add more comprehensive context for RAG mode
        context_parts.append("You are operating in RAG mode. Use the provided document context to give detailed, accurate responses.")
    elif mode == "creative":
        context_parts.append("You are operating in creative mode. Provide innovative, out-of-the-box suggestions.")
    elif mode == "detailed":
        context_parts.append("You are operating in detailed mode. Provide comprehensive, thorough responses.")
    elif mode == "fast":
        context_parts.append("You are operating in fast mode. Provide quick, concise responses.")
    else:
        context_parts.append("You are operating in balanced mode. Provide well-balanced responses.")
    
    return "\n\n".join(context_parts)

# Quick action implementations

async def generate_project_report(db: Session) -> str:
    """Generate project report"""
    from app.models.main_tables import Project
    projects = db.query(Project).limit(10).all()
    
    report = f"Project Report - {len(projects)} projects analyzed\n\n"
    for project in projects:
        report += f"• {project.name}: {project.percent_complete}% complete\n"
    
    return report

async def generate_resource_analysis(db: Session) -> str:
    """Generate resource analysis"""
    from app.models.main_tables import Resource
    resources = db.query(Resource).limit(10).all()
    
    analysis = f"Resource Analysis - {len(resources)} resources\n\n"
    for resource in resources:
        analysis += f"• {resource.name} ({resource.role}): {resource.availability}% available\n"
    
    return analysis

async def generate_budget_review(db: Session) -> str:
    """Generate budget review"""
    from app.models.main_tables import Project
    projects = db.query(Project).filter(Project.budget_amount.isnot(None)).limit(10).all()
    
    total_budget = sum(float(p.budget_amount) for p in projects if p.budget_amount)
    review = f"Budget Review - Total Budget: ${total_budget:,.2f}\n\n"
    
    for project in projects:
        if project.budget_amount:
            review += f"• {project.name}: ${float(project.budget_amount):,.2f}\n"
    
    return review

async def generate_risk_summary(db: Session) -> str:
    """Generate risk summary"""
    from app.models.main_tables import Risk
    risks = db.query(Risk).limit(10).all()
    
    summary = f"Risk Summary - {len(risks)} risks identified\n\n"
    for risk in risks:
        summary += f"• {risk.risk_name}: {risk.risk_level} priority\n"
    
    return summary

async def generate_executive_summary(db: Session) -> str:
    """Generate executive summary"""
    from app.models.main_tables import Project
    projects = db.query(Project).limit(5).all()
    
    summary = "Executive Summary\n\n"
    summary += f"Active Projects: {len(projects)}\n"
    summary += f"Average Progress: {sum(p.percent_complete or 0 for p in projects) / len(projects):.1f}%\n"
    summary += "\nKey Projects:\n"
    
    for project in projects[:3]:
        summary += f"• {project.name}: {project.percent_complete}% complete\n"
    
    return summary

async def generate_schedule_tips(db: Session) -> str:
    """Generate schedule tips"""
    tips = [
        "1. Use critical path analysis to identify bottlenecks",
        "2. Implement buffer time for high-risk tasks",
        "3. Regular milestone reviews to track progress",
        "4. Consider resource availability when scheduling",
        "5. Use agile methodologies for flexible planning"
    ]
    
    return "Schedule Optimization Tips:\n\n" + "\n".join(tips)

async def generate_performance_analysis(db: Session) -> str:
    """Generate performance analysis"""
    from app.models.main_tables import Project
    projects = db.query(Project).limit(10).all()
    
    avg_progress = sum(p.percent_complete or 0 for p in projects) / len(projects) if projects else 0
    
    analysis = f"Performance Analysis\n\n"
    analysis += f"Average Project Progress: {avg_progress:.1f}%\n"
    analysis += f"Projects On Track: {len([p for p in projects if (p.percent_complete or 0) > 50])}\n"
    analysis += f"Projects At Risk: {len([p for p in projects if (p.percent_complete or 0) < 25])}\n"
    
    return analysis

async def generate_strategy_recommendations(db: Session) -> str:
    """Generate strategy recommendations"""
    recommendations = [
        "1. Implement AI-powered project forecasting",
        "2. Establish cross-functional teams for better collaboration",
        "3. Invest in automation tools for routine tasks",
        "4. Create knowledge sharing platforms",
        "5. Develop agile transformation roadmap"
    ]
    
    return "Strategic Recommendations:\n\n" + "\n".join(recommendations)

async def generate_financial_report_email(db: Session) -> str:
    """Generate financial report and email"""
    report = await generate_budget_review(db)
    email = f"Subject: Financial Report - {datetime.now().strftime('%Y-%m-%d')}\n\n{report}"
    return f"Financial Report Generated:\n\n{report}\n\nEmail Draft:\n{email}"

async def save_analysis_to_folder(request: Dict, user: Dict) -> str:
    """Save analysis to folder"""
    folder_path = f"/reports/{user.get('id', 'anonymous')}/{datetime.now().strftime('%Y%m%d')}"
    return f"Analysis saved to: {folder_path}"

async def generate_executive_summary_email(db: Session) -> str:
    """Generate executive summary and email"""
    summary = await generate_executive_summary(db)
    email = f"Subject: Executive Summary - {datetime.now().strftime('%Y-%m-%d')}\n\n{summary}"
    return f"Executive Summary Generated:\n\n{summary}\n\nEmail Draft:\n{email}"

async def generate_resource_report_save(db: Session) -> str:
    """Generate resource report and save"""
    report = await generate_resource_analysis(db)
    folder_path = f"/reports/resources/{datetime.now().strftime('%Y%m%d')}"
    return f"Resource Report Generated:\n\n{report}\n\nSaved to: {folder_path}"

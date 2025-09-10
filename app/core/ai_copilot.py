"""
AI Copilot Service
Provides intelligent assistance for project management tasks
"""

import asyncio
import json
import logging
from typing import Dict, List, Optional, Any, Union
from datetime import datetime, timedelta
from enum import Enum
from pydantic import BaseModel, Field

from app.core.ai_client import AIService, AIMessage
from app.core.cache import cache_result, cache_invalidate
from app.core.logging import get_logger

logger = get_logger(__name__)


class CopilotTaskType(str, Enum):
    """Types of copilot tasks."""
    PROJECT_ANALYSIS = "project_analysis"
    PORTFOLIO_INSIGHTS = "portfolio_insights"
    CODE_REVIEW = "code_review"
    DOCUMENTATION = "documentation"
    RISK_ASSESSMENT = "risk_assessment"
    RESOURCE_OPTIMIZATION = "resource_optimization"
    TIMELINE_ANALYSIS = "timeline_analysis"
    BUDGET_ANALYSIS = "budget_analysis"
    QUALITY_ASSURANCE = "quality_assurance"
    PERFORMANCE_OPTIMIZATION = "performance_optimization"


class CopilotPriority(str, Enum):
    """Copilot task priority levels."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class CopilotTask(BaseModel):
    """AI Copilot task model."""
    id: str
    type: CopilotTaskType
    priority: CopilotPriority
    title: str
    description: str
    context: Dict[str, Any]
    status: str = "pending"
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    completed_at: Optional[datetime] = None
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


class AICopilot:
    """AI Copilot service for intelligent project management assistance."""
    
    def __init__(self, ai_service: AIService):
        self.ai_service = ai_service
        self.logger = get_logger(__name__)
        self.active_tasks: Dict[str, CopilotTask] = {}
        self.task_history: List[CopilotTask] = []
    
    async def analyze_project_health(
        self,
        project_id: str,
        project_data: Dict[str, Any],
        priority: CopilotPriority = CopilotPriority.MEDIUM
    ) -> CopilotTask:
        """Analyze project health using AI."""
        task_id = f"health_analysis_{project_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        task = CopilotTask(
            id=task_id,
            type=CopilotTaskType.PROJECT_ANALYSIS,
            priority=priority,
            title=f"Health Analysis for Project: {project_data.get('name', 'Unknown')}",
            description="Comprehensive AI-powered project health analysis",
            context={
                "project_id": project_id,
                "project_data": project_data
            }
        )
        
        self.active_tasks[task_id] = task
        
        try:
            # Perform AI analysis
            analysis_result = await self.ai_service.analyze_project_health(project_data)
            
            # Update task
            task.status = "completed"
            task.completed_at = datetime.now()
            task.result = analysis_result
            task.updated_at = datetime.now()
            
            # Move to history
            self.task_history.append(task)
            del self.active_tasks[task_id]
            
            self.logger.info(f"Project health analysis completed for project {project_id}")
            return task
            
        except Exception as e:
            task.status = "failed"
            task.error = str(e)
            task.updated_at = datetime.now()
            
            self.logger.error(f"Project health analysis failed for project {project_id}: {e}")
            return task
    
    async def generate_portfolio_insights(
        self,
        portfolio_id: str,
        projects_data: List[Dict[str, Any]],
        priority: CopilotPriority = CopilotPriority.HIGH
    ) -> CopilotTask:
        """Generate portfolio insights using AI."""
        task_id = f"portfolio_insights_{portfolio_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        task = CopilotTask(
            id=task_id,
            type=CopilotTaskType.PORTFOLIO_INSIGHTS,
            priority=priority,
            title=f"Portfolio Insights for Portfolio: {portfolio_id}",
            description="AI-powered portfolio analysis and insights",
            context={
                "portfolio_id": portfolio_id,
                "projects_count": len(projects_data),
                "projects_data": projects_data
            }
        )
        
        self.active_tasks[task_id] = task
        
        try:
            # Perform AI analysis
            insights_result = await self.ai_service.generate_project_insights(projects_data)
            
            # Update task
            task.status = "completed"
            task.completed_at = datetime.now()
            task.result = insights_result
            task.updated_at = datetime.now()
            
            # Move to history
            self.task_history.append(task)
            del self.active_tasks[task_id]
            
            self.logger.info(f"Portfolio insights generated for portfolio {portfolio_id}")
            return task
            
        except Exception as e:
            task.status = "failed"
            task.error = str(e)
            task.updated_at = datetime.now()
            
            self.logger.error(f"Portfolio insights generation failed for portfolio {portfolio_id}: {e}")
            return task
    
    async def perform_code_review(
        self,
        code_id: str,
        code_content: str,
        review_type: str = "general",
        priority: CopilotPriority = CopilotPriority.MEDIUM
    ) -> CopilotTask:
        """Perform AI-powered code review."""
        task_id = f"code_review_{code_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        task = CopilotTask(
            id=task_id,
            type=CopilotTaskType.CODE_REVIEW,
            priority=priority,
            title=f"Code Review for: {code_id}",
            description=f"AI-powered {review_type} code review",
            context={
                "code_id": code_id,
                "code_content": code_content,
                "review_type": review_type
            }
        )
        
        self.active_tasks[task_id] = task
        
        try:
            # Perform AI code review
            review_result = await self.ai_service.generate_code_suggestions(
                code_content,
                f"Perform {review_type} code review and provide suggestions"
            )
            
            # Update task
            task.status = "completed"
            task.completed_at = datetime.now()
            task.result = review_result
            task.updated_at = datetime.now()
            
            # Move to history
            self.task_history.append(task)
            del self.active_tasks[task_id]
            
            self.logger.info(f"Code review completed for {code_id}")
            return task
            
        except Exception as e:
            task.status = "failed"
            task.error = str(e)
            task.updated_at = datetime.now()
            
            self.logger.error(f"Code review failed for {code_id}: {e}")
            return task
    
    async def generate_documentation(
        self,
        doc_id: str,
        content: str,
        doc_type: str = "API",
        priority: CopilotPriority = CopilotPriority.LOW
    ) -> CopilotTask:
        """Generate documentation using AI."""
        task_id = f"documentation_{doc_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        task = CopilotTask(
            id=task_id,
            type=CopilotTaskType.DOCUMENTATION,
            priority=priority,
            title=f"Documentation Generation for: {doc_id}",
            description=f"AI-powered {doc_type} documentation generation",
            context={
                "doc_id": doc_id,
                "content": content,
                "doc_type": doc_type
            }
        )
        
        self.active_tasks[task_id] = task
        
        try:
            # Generate documentation
            doc_result = await self.ai_service.generate_documentation(content, doc_type)
            
            # Update task
            task.status = "completed"
            task.completed_at = datetime.now()
            task.result = doc_result
            task.updated_at = datetime.now()
            
            # Move to history
            self.task_history.append(task)
            del self.active_tasks[task_id]
            
            self.logger.info(f"Documentation generated for {doc_id}")
            return task
            
        except Exception as e:
            task.status = "failed"
            task.error = str(e)
            task.updated_at = datetime.now()
            
            self.logger.error(f"Documentation generation failed for {doc_id}: {e}")
            return task
    
    async def assess_risks(
        self,
        project_id: str,
        project_data: Dict[str, Any],
        priority: CopilotPriority = CopilotPriority.HIGH
    ) -> CopilotTask:
        """Assess project risks using AI."""
        task_id = f"risk_assessment_{project_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        task = CopilotTask(
            id=task_id,
            type=CopilotTaskType.RISK_ASSESSMENT,
            priority=priority,
            title=f"Risk Assessment for Project: {project_data.get('name', 'Unknown')}",
            description="AI-powered project risk assessment",
            context={
                "project_id": project_id,
                "project_data": project_data
            }
        )
        
        self.active_tasks[task_id] = task
        
        try:
            # Prepare risk assessment prompt
            risk_prompt = f"""
            Project Risk Assessment Request:
            - Name: {project_data.get('name', 'Unknown')}
            - Status: {project_data.get('status', 'Unknown')}
            - Progress: {project_data.get('percent_complete', 0)}%
            - Budget: ${project_data.get('budget_amount', 0):,.2f}
            - Start Date: {project_data.get('start_date', 'Unknown')}
            - Due Date: {project_data.get('due_date', 'Unknown')}
            - Manager: {project_data.get('project_manager', 'Unknown')}
            
            Please assess:
            1. Technical Risks
            2. Schedule Risks
            3. Budget Risks
            4. Resource Risks
            5. External Risks
            6. Mitigation Strategies
            
            Provide risk scores (1-10) and detailed analysis.
            """
            
            messages = [
                AIMessage(
                    role="system",
                    content="""You are a project risk management expert. Analyze the project data and provide comprehensive risk assessment.
                    Focus on identifying potential issues and providing actionable mitigation strategies.
                    Respond in JSON format with risk categories and scores."""
                ),
                AIMessage(role="user", content=risk_prompt)
            ]
            
            # Use AI service for risk assessment
            response = await self.ai_service.ollama_client.generate_text(
                model="llama3:8b",
                messages=messages,
                temperature=0.3
            )
            
            # Parse response
            try:
                risk_analysis = json.loads(response.content)
            except json.JSONDecodeError:
                risk_analysis = {
                    "technical_risks": {"score": 5, "description": "Unable to parse AI response"},
                    "schedule_risks": {"score": 5, "description": "Manual review required"},
                    "budget_risks": {"score": 5, "description": "Data analysis needed"},
                    "resource_risks": {"score": 5, "description": "Resource review required"},
                    "external_risks": {"score": 5, "description": "External factor analysis needed"},
                    "mitigation_strategies": ["Contact project manager for detailed review"]
                }
            
            # Update task
            task.status = "completed"
            task.completed_at = datetime.now()
            task.result = {
                "risk_analysis": risk_analysis,
                "model_used": response.model,
                "tokens_used": response.tokens_used,
                "response_time": response.response_time,
                "timestamp": response.timestamp
            }
            task.updated_at = datetime.now()
            
            # Move to history
            self.task_history.append(task)
            del self.active_tasks[task_id]
            
            self.logger.info(f"Risk assessment completed for project {project_id}")
            return task
            
        except Exception as e:
            task.status = "failed"
            task.error = str(e)
            task.updated_at = datetime.now()
            
            self.logger.error(f"Risk assessment failed for project {project_id}: {e}")
            return task
    
    async def optimize_resources(
        self,
        resource_data: List[Dict[str, Any]],
        priority: CopilotPriority = CopilotPriority.MEDIUM
    ) -> CopilotTask:
        """Optimize resource allocation using AI."""
        task_id = f"resource_optimization_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        task = CopilotTask(
            id=task_id,
            type=CopilotTaskType.RESOURCE_OPTIMIZATION,
            priority=priority,
            title="Resource Allocation Optimization",
            description="AI-powered resource optimization analysis",
            context={
                "resource_count": len(resource_data),
                "resource_data": resource_data
            }
        )
        
        self.active_tasks[task_id] = task
        
        try:
            # Prepare resource optimization prompt
            resource_summary = f"""
            Resource Optimization Request:
            Total Resources: {len(resource_data)}
            
            Resource Summary:
            """
            
            for i, resource in enumerate(resource_data[:10]):  # Limit to first 10 resources
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
                    content="""You are a resource management expert. Analyze the resource data and provide optimization recommendations.
                    Focus on:
                    1. Skill matching
                    2. Availability optimization
                    3. Workload balancing
                    4. Capacity planning
                    5. Training needs
                    
                    Respond in JSON format with optimization strategies."""
                ),
                AIMessage(role="user", content=resource_summary)
            ]
            
            # Use AI service for resource optimization
            response = await self.ai_service.ollama_client.generate_text(
                model="llama3:8b",
                messages=messages,
                temperature=0.4
            )
            
            # Parse response
            try:
                optimization_analysis = json.loads(response.content)
            except json.JSONDecodeError:
                optimization_analysis = {
                    "skill_matching": {"score": 7, "recommendations": ["Manual review required"]},
                    "availability_optimization": {"score": 7, "recommendations": ["Capacity analysis needed"]},
                    "workload_balancing": {"score": 7, "recommendations": ["Workload review required"]},
                    "capacity_planning": {"score": 7, "recommendations": ["Capacity planning needed"]},
                    "training_needs": {"recommendations": ["Training assessment required"]}
                }
            
            # Update task
            task.status = "completed"
            task.completed_at = datetime.now()
            task.result = {
                "optimization_analysis": optimization_analysis,
                "model_used": response.model,
                "tokens_used": response.tokens_used,
                "response_time": response.response_time,
                "timestamp": response.timestamp
            }
            task.updated_at = datetime.now()
            
            # Move to history
            self.task_history.append(task)
            del self.active_tasks[task_id]
            
            self.logger.info("Resource optimization completed")
            return task
            
        except Exception as e:
            task.status = "failed"
            task.error = str(e)
            task.updated_at = datetime.now()
            
            self.logger.error(f"Resource optimization failed: {e}")
            return task
    
    async def analyze_timeline(
        self,
        project_id: str,
        timeline_data: Dict[str, Any],
        priority: CopilotPriority = CopilotPriority.MEDIUM
    ) -> CopilotTask:
        """Analyze project timeline using AI."""
        task_id = f"timeline_analysis_{project_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        task = CopilotTask(
            id=task_id,
            type=CopilotTaskType.TIMELINE_ANALYSIS,
            priority=priority,
            title=f"Timeline Analysis for Project: {project_id}",
            description="AI-powered project timeline analysis",
            context={
                "project_id": project_id,
                "timeline_data": timeline_data
            }
        )
        
        self.active_tasks[task_id] = task
        
        try:
            # Prepare timeline analysis prompt
            timeline_summary = f"""
            Timeline Analysis Request:
            Project ID: {project_id}
            Start Date: {timeline_data.get('start_date', 'Unknown')}
            Due Date: {timeline_data.get('due_date', 'Unknown')}
            Current Progress: {timeline_data.get('percent_complete', 0)}%
            Milestones: {timeline_data.get('milestones', [])}
            Dependencies: {timeline_data.get('dependencies', [])}
            """
            
            messages = [
                AIMessage(
                    role="system",
                    content="""You are a project timeline expert. Analyze the timeline data and provide insights.
                    Focus on:
                    1. Schedule adherence
                    2. Critical path analysis
                    3. Risk factors
                    4. Optimization opportunities
                    5. Recommendations
                    
                    Respond in JSON format with timeline insights."""
                ),
                AIMessage(role="user", content=timeline_summary)
            ]
            
            # Use AI service for timeline analysis
            response = await self.ai_service.ollama_client.generate_text(
                model="llama3:8b",
                messages=messages,
                temperature=0.3
            )
            
            # Parse response
            try:
                timeline_analysis = json.loads(response.content)
            except json.JSONDecodeError:
                timeline_analysis = {
                    "schedule_adherence": {"score": 7, "status": "On track"},
                    "critical_path": {"analysis": "Manual review required"},
                    "risk_factors": ["Data parsing error"],
                    "optimization_opportunities": ["Timeline review needed"],
                    "recommendations": ["Contact project manager"]
                }
            
            # Update task
            task.status = "completed"
            task.completed_at = datetime.now()
            task.result = {
                "timeline_analysis": timeline_analysis,
                "model_used": response.model,
                "tokens_used": response.tokens_used,
                "response_time": response.response_time,
                "timestamp": response.timestamp
            }
            task.updated_at = datetime.now()
            
            # Move to history
            self.task_history.append(task)
            del self.active_tasks[task_id]
            
            self.logger.info(f"Timeline analysis completed for project {project_id}")
            return task
            
        except Exception as e:
            task.status = "failed"
            task.error = str(e)
            task.updated_at = datetime.now()
            
            self.logger.error(f"Timeline analysis failed for project {project_id}: {e}")
            return task
    
    async def analyze_budget(
        self,
        project_id: str,
        budget_data: Dict[str, Any],
        priority: CopilotPriority = CopilotPriority.HIGH
    ) -> CopilotTask:
        """Analyze project budget using AI."""
        task_id = f"budget_analysis_{project_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        task = CopilotTask(
            id=task_id,
            type=CopilotTaskType.BUDGET_ANALYSIS,
            priority=priority,
            title=f"Budget Analysis for Project: {project_id}",
            description="AI-powered project budget analysis",
            context={
                "project_id": project_id,
                "budget_data": budget_data
            }
        )
        
        self.active_tasks[task_id] = task
        
        try:
            # Prepare budget analysis prompt
            budget_summary = f"""
            Budget Analysis Request:
            Project ID: {project_id}
            Total Budget: ${budget_data.get('total_budget', 0):,.2f}
            Spent Amount: ${budget_data.get('spent_amount', 0):,.2f}
            Remaining Budget: ${budget_data.get('remaining_budget', 0):,.2f}
            Budget Utilization: {budget_data.get('utilization_percentage', 0)}%
            Cost Categories: {budget_data.get('cost_categories', {})}
            """
            
            messages = [
                AIMessage(
                    role="system",
                    content="""You are a financial analysis expert. Analyze the budget data and provide insights.
                    Focus on:
                    1. Budget utilization
                    2. Cost efficiency
                    3. Risk factors
                    4. Optimization opportunities
                    5. Recommendations
                    
                    Respond in JSON format with budget insights."""
                ),
                AIMessage(role="user", content=budget_summary)
            ]
            
            # Use AI service for budget analysis
            response = await self.ai_service.ollama_client.generate_text(
                model="llama3:8b",
                messages=messages,
                temperature=0.3
            )
            
            # Parse response
            try:
                budget_analysis = json.loads(response.content)
            except json.JSONDecodeError:
                budget_analysis = {
                    "budget_utilization": {"score": 7, "status": "Within budget"},
                    "cost_efficiency": {"score": 7, "analysis": "Manual review required"},
                    "risk_factors": ["Data parsing error"],
                    "optimization_opportunities": ["Budget review needed"],
                    "recommendations": ["Contact project manager"]
                }
            
            # Update task
            task.status = "completed"
            task.completed_at = datetime.now()
            task.result = {
                "budget_analysis": budget_analysis,
                "model_used": response.model,
                "tokens_used": response.tokens_used,
                "response_time": response.response_time,
                "timestamp": response.timestamp
            }
            task.updated_at = datetime.now()
            
            # Move to history
            self.task_history.append(task)
            del self.active_tasks[task_id]
            
            self.logger.info(f"Budget analysis completed for project {project_id}")
            return task
            
        except Exception as e:
            task.status = "failed"
            task.error = str(e)
            task.updated_at = datetime.now()
            
            self.logger.error(f"Budget analysis failed for project {project_id}: {e}")
            return task
    
    def get_active_tasks(self) -> List[CopilotTask]:
        """Get list of active tasks."""
        return list(self.active_tasks.values())
    
    def get_task_history(self, limit: int = 50) -> List[CopilotTask]:
        """Get task history."""
        return self.task_history[-limit:]
    
    def get_task_by_id(self, task_id: str) -> Optional[CopilotTask]:
        """Get task by ID."""
        if task_id in self.active_tasks:
            return self.active_tasks[task_id]
        
        for task in self.task_history:
            if task.id == task_id:
                return task
        
        return None
    
    def get_tasks_by_type(self, task_type: CopilotTaskType) -> List[CopilotTask]:
        """Get tasks by type."""
        tasks = []
        
        # Check active tasks
        for task in self.active_tasks.values():
            if task.type == task_type:
                tasks.append(task)
        
        # Check history
        for task in self.task_history:
            if task.type == task_type:
                tasks.append(task)
        
        return tasks
    
    def get_tasks_by_priority(self, priority: CopilotPriority) -> List[CopilotTask]:
        """Get tasks by priority."""
        tasks = []
        
        # Check active tasks
        for task in self.active_tasks.values():
            if task.priority == priority:
                tasks.append(task)
        
        # Check history
        for task in self.task_history:
            if task.priority == priority:
                tasks.append(task)
        
        return tasks
    
    async def cancel_task(self, task_id: str) -> bool:
        """Cancel an active task."""
        if task_id in self.active_tasks:
            task = self.active_tasks[task_id]
            task.status = "cancelled"
            task.updated_at = datetime.now()
            
            # Move to history
            self.task_history.append(task)
            del self.active_tasks[task_id]
            
            self.logger.info(f"Task {task_id} cancelled")
            return True
        
        return False
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get copilot statistics."""
        total_tasks = len(self.active_tasks) + len(self.task_history)
        completed_tasks = len([t for t in self.task_history if t.status == "completed"])
        failed_tasks = len([t for t in self.task_history if t.status == "failed"])
        
        # Task type distribution
        type_distribution = {}
        for task in self.task_history:
            type_distribution[task.type] = type_distribution.get(task.type, 0) + 1
        
        # Priority distribution
        priority_distribution = {}
        for task in self.task_history:
            priority_distribution[task.priority] = priority_distribution.get(task.priority, 0) + 1
        
        return {
            "total_tasks": total_tasks,
            "active_tasks": len(self.active_tasks),
            "completed_tasks": completed_tasks,
            "failed_tasks": failed_tasks,
            "success_rate": (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0,
            "type_distribution": type_distribution,
            "priority_distribution": priority_distribution,
            "timestamp": datetime.now()
        }


# Global copilot instance
copilot: Optional[AICopilot] = None


async def get_copilot() -> AICopilot:
    """Get global copilot instance."""
    global copilot
    if copilot is None:
        ai_service = await get_ai_service()
        copilot = AICopilot(ai_service)
    return copilot

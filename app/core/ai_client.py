"""
AI Client for Ollama Integration
Provides unified interface for interacting with various Ollama models
"""

import asyncio
import json
import logging
from typing import Dict, List, Optional, Any, Union
from datetime import datetime
import httpx
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


class AIMessage(BaseModel):
    """AI message model."""
    role: str = Field(..., description="Message role: system, user, or assistant")
    content: str = Field(..., description="Message content")


class AIResponse(BaseModel):
    """AI response model."""
    model: str = Field(..., description="Model used for generation")
    content: str = Field(..., description="Generated content")
    tokens_used: int = Field(..., description="Number of tokens used")
    response_time: float = Field(..., description="Response time in seconds")
    timestamp: datetime = Field(default_factory=datetime.now)


class AIRequest(BaseModel):
    """AI request model."""
    model: str = Field(..., description="Model to use")
    messages: List[AIMessage] = Field(..., description="List of messages")
    temperature: float = Field(default=0.7, ge=0.0, le=2.0, description="Temperature for generation")
    max_tokens: Optional[int] = Field(default=None, description="Maximum tokens to generate")
    stream: bool = Field(default=False, description="Whether to stream response")


class OllamaClient:
    """Client for interacting with Ollama models."""
    
    def __init__(self, base_url: str = "http://localhost:11434"):
        self.base_url = base_url
        self.client = httpx.AsyncClient(timeout=30.0)
        self.available_models = {}
        self.model_configs = {
            "llama3:8b": {
                "name": "Llama 3 8B",
                "description": "General purpose language model for complex tasks",
                "max_tokens": 4096,
                "temperature": 0.7,
                "use_cases": ["code_generation", "analysis", "reasoning"]
            },
            "llama3.2:3b-instruct-q4_K_M": {
                "name": "Llama 3.2 3B Instruct",
                "description": "Instruction-tuned model for specific tasks",
                "max_tokens": 2048,
                "temperature": 0.5,
                "use_cases": ["instructions", "task_completion", "qa"]
            },
            "mistral:7b-instruct-v0.2-q4_K_M": {
                "name": "Mistral 7B Instruct",
                "description": "High-performance instruction model",
                "max_tokens": 4096,
                "temperature": 0.6,
                "use_cases": ["code_generation", "analysis", "reasoning"]
            },
            "codellama:7b-instruct-q4_K_M": {
                "name": "CodeLlama 7B Instruct",
                "description": "Specialized code generation model",
                "max_tokens": 4096,
                "temperature": 0.3,
                "use_cases": ["code_generation", "code_review", "debugging"]
            },
            "qwen2.5-coder:1.5b": {
                "name": "Qwen2.5 Coder 1.5B",
                "description": "Lightweight code generation model",
                "max_tokens": 2048,
                "temperature": 0.4,
                "use_cases": ["code_generation", "quick_tasks"]
            },
            "nomic-embed-text:latest": {
                "name": "Nomic Embed Text",
                "description": "Text embedding model for semantic search",
                "max_tokens": 512,
                "temperature": 0.0,
                "use_cases": ["embeddings", "similarity", "search"]
            }
        }
    
    async def __aenter__(self):
        """Async context manager entry."""
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.client.aclose()
    
    async def check_health(self) -> Dict[str, Any]:
        """Check Ollama service health."""
        try:
            response = await self.client.get(f"{self.base_url}/api/tags")
            if response.status_code == 200:
                data = response.json()
                return {
                    "status": "healthy",
                    "models": data.get("models", []),
                    "timestamp": datetime.now()
                }
            else:
                return {
                    "status": "unhealthy",
                    "error": f"HTTP {response.status_code}",
                    "timestamp": datetime.now()
                }
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e),
                "timestamp": datetime.now()
            }
    
    async def get_available_models(self) -> List[Dict[str, Any]]:
        """Get list of available models."""
        try:
            response = await self.client.get(f"{self.base_url}/api/tags")
            if response.status_code == 200:
                data = response.json()
                models = data.get("models", [])
                
                # Enhance model info with our configurations
                enhanced_models = []
                for model in models:
                    model_name = model.get("name", "")
                    enhanced_model = {
                        "name": model_name,
                        "size": model.get("size", 0),
                        "modified_at": model.get("modified_at", ""),
                        **self.model_configs.get(model_name, {})
                    }
                    enhanced_models.append(enhanced_model)
                
                return enhanced_models
            else:
                logger.error(f"Failed to get models: HTTP {response.status_code}")
                return []
        except Exception as e:
            logger.error(f"Error getting available models: {e}")
            return []
    
    async def generate_text(
        self,
        model: str,
        messages: List[AIMessage],
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        stream: bool = False
    ) -> AIResponse:
        """Generate text using specified model."""
        start_time = datetime.now()
        
        try:
            # Get model config
            model_config = self.model_configs.get(model, {})
            if not model_config:
                raise ValueError(f"Unknown model: {model}")
            
            # Prepare request
            request_data = {
                "model": model,
                "messages": [msg.dict() for msg in messages],
                "temperature": temperature,
                "stream": stream
            }
            
            if max_tokens:
                request_data["options"] = {"num_predict": max_tokens}
            elif model_config.get("max_tokens"):
                request_data["options"] = {"num_predict": model_config["max_tokens"]}
            
            # Make request
            response = await self.client.post(
                f"{self.base_url}/api/chat",
                json=request_data
            )
            
            if response.status_code != 200:
                raise Exception(f"HTTP {response.status_code}: {response.text}")
            
            response_data = response.json()
            
            # Calculate response time
            response_time = (datetime.now() - start_time).total_seconds()
            
            # Extract content and tokens
            content = response_data.get("message", {}).get("content", "")
            tokens_used = response_data.get("eval_count", 0)
            
            return AIResponse(
                model=model,
                content=content,
                tokens_used=tokens_used,
                response_time=response_time,
                timestamp=datetime.now()
            )
            
        except Exception as e:
            logger.error(f"Error generating text with {model}: {e}")
            raise
    
    async def generate_embeddings(
        self,
        text: str,
        model: str = "nomic-embed-text:latest"
    ) -> List[float]:
        """Generate embeddings for text."""
        try:
            request_data = {
                "model": model,
                "prompt": text
            }
            
            response = await self.client.post(
                f"{self.base_url}/api/embeddings",
                json=request_data
            )
            
            if response.status_code != 200:
                raise Exception(f"HTTP {response.status_code}: {response.text}")
            
            response_data = response.json()
            return response_data.get("embedding", [])
            
        except Exception as e:
            logger.error(f"Error generating embeddings: {e}")
            raise
    
    async def pull_model(self, model_name: str) -> Dict[str, Any]:
        """Pull/download a model."""
        try:
            request_data = {"name": model_name}
            
            response = await self.client.post(
                f"{self.base_url}/api/pull",
                json=request_data
            )
            
            if response.status_code != 200:
                raise Exception(f"HTTP {response.status_code}: {response.text}")
            
            return response.json()
            
        except Exception as e:
            logger.error(f"Error pulling model {model_name}: {e}")
            raise
    
    async def delete_model(self, model_name: str) -> Dict[str, Any]:
        """Delete a model."""
        try:
            request_data = {"name": model_name}
            
            response = await self.client.delete(
                f"{self.base_url}/api/delete",
                json=request_data
            )
            
            if response.status_code != 200:
                raise Exception(f"HTTP {response.status_code}: {response.text}")
            
            return response.json()
            
        except Exception as e:
            logger.error(f"Error deleting model {model_name}: {e}")
            raise


class AIService:
    """High-level AI service for application-specific tasks."""
    
    def __init__(self, ollama_client: OllamaClient):
        self.ollama_client = ollama_client
        self.logger = logging.getLogger(__name__)
    
    async def analyze_project_health(self, project_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze project health using AI."""
        try:
            # Prepare project summary
            project_summary = f"""
            Project Analysis Request:
            - Name: {project_data.get('name', 'Unknown')}
            - Status: {project_data.get('status', 'Unknown')}
            - Priority: {project_data.get('priority', 'Unknown')}
            - Progress: {project_data.get('percent_complete', 0)}%
            - Budget: ${project_data.get('budget_amount', 0):,.2f}
            - Start Date: {project_data.get('start_date', 'Unknown')}
            - Due Date: {project_data.get('due_date', 'Unknown')}
            - Manager: {project_data.get('project_manager', 'Unknown')}
            - Description: {project_data.get('description', 'No description')}
            """
            
            messages = [
                AIMessage(
                    role="system",
                    content="""You are a project management expert. Analyze the project data and provide:
                    1. Health Score (0-100)
                    2. Risk Assessment (Low/Medium/High)
                    3. Key Issues (if any)
                    4. Recommendations
                    5. Priority Actions
                    
                    Respond in JSON format with these fields."""
                ),
                AIMessage(role="user", content=project_summary)
            ]
            
            response = await self.ollama_client.generate_text(
                model="llama3:8b",
                messages=messages,
                temperature=0.3
            )
            
            # Parse AI response
            try:
                analysis = json.loads(response.content)
            except json.JSONDecodeError:
                # Fallback if JSON parsing fails
                analysis = {
                    "health_score": 75,
                    "risk_assessment": "Medium",
                    "key_issues": ["Unable to parse AI response"],
                    "recommendations": ["Review project data manually"],
                    "priority_actions": ["Contact project manager"]
                }
            
            return {
                "analysis": analysis,
                "model_used": response.model,
                "tokens_used": response.tokens_used,
                "response_time": response.response_time,
                "timestamp": response.timestamp
            }
            
        except Exception as e:
            self.logger.error(f"Error analyzing project health: {e}")
            return {
                "error": str(e),
                "analysis": {
                    "health_score": 50,
                    "risk_assessment": "Unknown",
                    "key_issues": ["Analysis failed"],
                    "recommendations": ["Manual review required"],
                    "priority_actions": ["Contact support"]
                }
            }
    
    async def generate_project_insights(self, projects_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate insights from multiple projects."""
        try:
            # Prepare projects summary
            projects_summary = f"""
            Portfolio Analysis Request:
            Total Projects: {len(projects_data)}
            
            Project Summary:
            """
            
            for i, project in enumerate(projects_data[:10]):  # Limit to first 10 projects
                projects_summary += f"""
            Project {i+1}:
            - Name: {project.get('name', 'Unknown')}
            - Status: {project.get('status', 'Unknown')}
            - Progress: {project.get('percent_complete', 0)}%
            - Budget: ${project.get('budget_amount', 0):,.2f}
            """
            
            messages = [
                AIMessage(
                    role="system",
                    content="""You are a portfolio management expert. Analyze the project portfolio and provide:
                    1. Overall Portfolio Health (0-100)
                    2. Top 3 Risks
                    3. Resource Allocation Insights
                    4. Timeline Analysis
                    5. Budget Analysis
                    6. Strategic Recommendations
                    
                    Respond in JSON format with these fields."""
                ),
                AIMessage(role="user", content=projects_summary)
            ]
            
            response = await self.ollama_client.generate_text(
                model="llama3:8b",
                messages=messages,
                temperature=0.4
            )
            
            # Parse AI response
            try:
                insights = json.loads(response.content)
            except json.JSONDecodeError:
                insights = {
                    "portfolio_health": 70,
                    "top_risks": ["Data parsing error"],
                    "resource_insights": ["Manual review required"],
                    "timeline_analysis": ["Unable to analyze"],
                    "budget_analysis": ["Data unavailable"],
                    "strategic_recommendations": ["Contact portfolio manager"]
                }
            
            return {
                "insights": insights,
                "model_used": response.model,
                "tokens_used": response.tokens_used,
                "response_time": response.response_time,
                "timestamp": response.timestamp
            }
            
        except Exception as e:
            self.logger.error(f"Error generating project insights: {e}")
            return {
                "error": str(e),
                "insights": {
                    "portfolio_health": 50,
                    "top_risks": ["Analysis failed"],
                    "resource_insights": ["Manual review required"],
                    "timeline_analysis": ["Unable to analyze"],
                    "budget_analysis": ["Data unavailable"],
                    "strategic_recommendations": ["Contact support"]
                }
            }
    
    async def generate_code_suggestions(self, code_context: str, task_description: str) -> Dict[str, Any]:
        """Generate code suggestions using CodeLlama."""
        try:
            messages = [
                AIMessage(
                    role="system",
                    content="""You are an expert software developer. Provide code suggestions and improvements.
                    Focus on:
                    1. Code quality
                    2. Performance optimization
                    3. Best practices
                    4. Security considerations
                    5. Error handling
                    
                    Provide practical, actionable suggestions."""
                ),
                AIMessage(
                    role="user",
                    content=f"""Task: {task_description}
                    
                    Code Context:
                    {code_context}
                    
                    Please provide suggestions for improvement."""
                )
            ]
            
            response = await self.ollama_client.generate_text(
                model="codellama:7b-instruct-q4_K_M",
                messages=messages,
                temperature=0.3
            )
            
            return {
                "suggestions": response.content,
                "model_used": response.model,
                "tokens_used": response.tokens_used,
                "response_time": response.response_time,
                "timestamp": response.timestamp
            }
            
        except Exception as e:
            self.logger.error(f"Error generating code suggestions: {e}")
            return {
                "error": str(e),
                "suggestions": "Unable to generate suggestions. Please try again."
            }
    
    async def generate_documentation(self, code_content: str, doc_type: str = "API") -> Dict[str, Any]:
        """Generate documentation for code."""
        try:
            messages = [
                AIMessage(
                    role="system",
                    content=f"""You are a technical documentation expert. Generate comprehensive {doc_type} documentation.
                    Include:
                    1. Overview and purpose
                    2. Parameters and return values
                    3. Usage examples
                    4. Error handling
                    5. Best practices
                    
                    Use clear, professional language."""
                ),
                AIMessage(
                    role="user",
                    content=f"""Please generate {doc_type} documentation for this code:
                    
                    {code_content}"""
                )
            ]
            
            response = await self.ollama_client.generate_text(
                model="mistral:7b-instruct-v0.2-q4_K_M",
                messages=messages,
                temperature=0.4
            )
            
            return {
                "documentation": response.content,
                "doc_type": doc_type,
                "model_used": response.model,
                "tokens_used": response.tokens_used,
                "response_time": response.response_time,
                "timestamp": response.timestamp
            }
            
        except Exception as e:
            self.logger.error(f"Error generating documentation: {e}")
            return {
                "error": str(e),
                "documentation": "Unable to generate documentation. Please try again."
            }
    
    async def semantic_search(self, query: str, documents: List[str], top_k: int = 5) -> List[Dict[str, Any]]:
        """Perform semantic search using embeddings."""
        try:
            # Generate query embedding
            query_embedding = await self.ollama_client.generate_embeddings(query)
            
            # Generate document embeddings
            doc_embeddings = []
            for doc in documents:
                embedding = await self.ollama_client.generate_embeddings(doc)
                doc_embeddings.append(embedding)
            
            # Calculate similarities (cosine similarity)
            similarities = []
            for i, doc_embedding in enumerate(doc_embeddings):
                similarity = self._cosine_similarity(query_embedding, doc_embedding)
                similarities.append({
                    "document": documents[i],
                    "similarity": similarity,
                    "index": i
                })
            
            # Sort by similarity and return top_k
            similarities.sort(key=lambda x: x["similarity"], reverse=True)
            return similarities[:top_k]
            
        except Exception as e:
            self.logger.error(f"Error in semantic search: {e}")
            return []
    
    def _cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """Calculate cosine similarity between two vectors."""
        import math
        
        dot_product = sum(a * b for a, b in zip(vec1, vec2))
        magnitude1 = math.sqrt(sum(a * a for a in vec1))
        magnitude2 = math.sqrt(sum(a * a for a in vec2))
        
        if magnitude1 == 0 or magnitude2 == 0:
            return 0.0
        
        return dot_product / (magnitude1 * magnitude2)


# Global AI service instance
ai_service: Optional[AIService] = None


async def get_ai_service() -> AIService:
    """Get global AI service instance."""
    global ai_service
    if ai_service is None:
        ollama_client = OllamaClient()
        ai_service = AIService(ollama_client)
    return ai_service


async def initialize_ai_service() -> AIService:
    """Initialize AI service."""
    global ai_service
    ollama_client = OllamaClient()
    ai_service = AIService(ollama_client)
    return ai_service

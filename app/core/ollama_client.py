"""
Ollama AI Client for GPT-OSS-20B Integration
Provides AI-powered analysis for project management dashboard
"""
import httpx
import json
from typing import Dict, List, Any, Optional
from app.core.logging import get_logger

logger = get_logger("core.ollama_client")

class OllamaClient:
    """Client for interacting with Ollama GPT-OSS-20B model"""
    
    def __init__(self, base_url: str = "http://localhost:11434"):
        self.base_url = base_url
        self.model_name = "gpt-oss-20b"
        self.timeout = 30.0
        
    async def generate_analysis(self, prompt: str, context: Dict[str, Any] = None) -> str:
        """Generate AI analysis using GPT-OSS-20B model"""
        try:
            # Prepare the full prompt with context
            full_prompt = self._prepare_prompt(prompt, context)
            
            # Make request to Ollama API
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.base_url}/api/generate",
                    json={
                        "model": self.model_name,
                        "prompt": full_prompt,
                        "stream": False,
                        "options": {
                            "temperature": 0.7,
                            "top_p": 0.9,
                            "max_tokens": 2000
                        }
                    }
                )
                
                if response.status_code == 200:
                    result = response.json()
                    return result.get("response", "No response generated")
                else:
                    logger.error(f"Ollama API error: {response.status_code} - {response.text}")
                    return "AI analysis temporarily unavailable"
                    
        except httpx.TimeoutException:
            logger.error("Ollama API timeout")
            return "AI analysis request timed out"
        except Exception as e:
            logger.error(f"Ollama API error: {str(e)}")
            return "AI analysis service unavailable"
    
    def _prepare_prompt(self, prompt: str, context: Dict[str, Any] = None) -> str:
        """Prepare the full prompt with context"""
        if not context:
            return prompt
            
        context_str = json.dumps(context, indent=2)
        return f"""Context Data:
{context_str}

Analysis Request:
{prompt}

Please provide a comprehensive analysis based on the context data above. Focus on actionable insights, trends, and recommendations."""
    
    async def analyze_project_health(self, project_data: Dict[str, Any]) -> str:
        """Analyze project health and provide insights"""
        prompt = """Analyze the project health data and provide:
1. Overall health assessment
2. Key risk factors identified
3. Recommendations for improvement
4. Priority actions needed
5. Success indicators to monitor

Be specific and actionable in your recommendations."""
        
        return await self.generate_analysis(prompt, project_data)
    
    async def analyze_financial_performance(self, financial_data: Dict[str, Any]) -> str:
        """Analyze financial performance and provide insights"""
        prompt = """Analyze the financial performance data and provide:
1. Budget utilization assessment
2. Cost vs benefit analysis
3. Financial risk indicators
4. ROI optimization recommendations
5. Budget allocation suggestions

Focus on financial efficiency and value delivery."""
        
        return await self.generate_analysis(prompt, financial_data)
    
    async def analyze_resource_utilization(self, resource_data: Dict[str, Any]) -> str:
        """Analyze resource utilization and provide insights"""
        prompt = """Analyze the resource utilization data and provide:
1. Resource efficiency assessment
2. Capacity planning insights
3. Skill gap analysis
4. Resource optimization recommendations
5. Team productivity suggestions

Consider workload distribution and skill matching."""
        
        return await self.generate_analysis(prompt, resource_data)
    
    async def generate_strategic_recommendations(self, dashboard_data: Dict[str, Any]) -> str:
        """Generate strategic recommendations based on overall dashboard data"""
        prompt = """Based on the comprehensive project management dashboard data, provide:
1. Strategic insights and trends
2. Portfolio-level recommendations
3. Risk mitigation strategies
4. Growth opportunities
5. Process improvement suggestions
6. Technology adoption recommendations

Provide executive-level insights that drive business value."""
        
        return await self.generate_analysis(prompt, dashboard_data)
    
    async def predict_project_outcomes(self, project_data: Dict[str, Any]) -> str:
        """Predict project outcomes and provide forecasts"""
        prompt = """Based on the project data, provide predictions for:
1. Project completion likelihood
2. Budget variance forecasts
3. Timeline risk assessment
4. Quality outcome predictions
5. Success probability analysis

Include confidence levels and supporting rationale."""
        
        return await self.generate_analysis(prompt, project_data)

# Global instance
ollama_client = OllamaClient()

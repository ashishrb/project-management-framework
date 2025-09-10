"""
AI Configuration Settings
Configuration for AI services and Ollama models
"""

import os
from typing import Dict, List, Any
from pydantic import BaseSettings


class AIConfig(BaseSettings):
    """AI configuration settings."""
    
    # Ollama Configuration
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    OLLAMA_TIMEOUT: int = 30
    OLLAMA_MAX_RETRIES: int = 3
    
    # Model Configuration
    DEFAULT_MODEL: str = "llama3:8b"
    EMBEDDING_MODEL: str = "nomic-embed-text:latest"
    CODE_MODEL: str = "codellama:7b-instruct-q4_K_M"
    INSTRUCTION_MODEL: str = "llama3.2:3b-instruct-q4_K_M"
    
    # AI Service Configuration
    AI_CACHE_TTL: int = 300  # 5 minutes
    AI_MAX_TOKENS: int = 4096
    AI_TEMPERATURE: float = 0.7
    AI_STREAM: bool = False
    
    # Copilot Configuration
    COPILOT_MAX_CONCURRENT_TASKS: int = 10
    COPILOT_TASK_TIMEOUT: int = 300  # 5 minutes
    COPILOT_RETRY_ATTEMPTS: int = 3
    
    # Performance Configuration
    AI_RESPONSE_TIMEOUT: int = 30
    AI_BATCH_SIZE: int = 10
    AI_RATE_LIMIT: int = 100  # requests per minute
    
    # Model-specific configurations
    MODEL_CONFIGS: Dict[str, Dict[str, Any]] = {
        "llama3:8b": {
            "name": "Llama 3 8B",
            "description": "General purpose language model for complex tasks",
            "max_tokens": 4096,
            "temperature": 0.7,
            "use_cases": ["code_generation", "analysis", "reasoning"],
            "performance": "high",
            "memory_usage": "medium"
        },
        "llama3.2:3b-instruct-q4_K_M": {
            "name": "Llama 3.2 3B Instruct",
            "description": "Instruction-tuned model for specific tasks",
            "max_tokens": 2048,
            "temperature": 0.5,
            "use_cases": ["instructions", "task_completion", "qa"],
            "performance": "medium",
            "memory_usage": "low"
        },
        "mistral:7b-instruct-v0.2-q4_K_M": {
            "name": "Mistral 7B Instruct",
            "description": "High-performance instruction model",
            "max_tokens": 4096,
            "temperature": 0.6,
            "use_cases": ["code_generation", "analysis", "reasoning"],
            "performance": "high",
            "memory_usage": "medium"
        },
        "codellama:7b-instruct-q4_K_M": {
            "name": "CodeLlama 7B Instruct",
            "description": "Specialized code generation model",
            "max_tokens": 4096,
            "temperature": 0.3,
            "use_cases": ["code_generation", "code_review", "debugging"],
            "performance": "high",
            "memory_usage": "medium"
        },
        "qwen2.5-coder:1.5b": {
            "name": "Qwen2.5 Coder 1.5B",
            "description": "Lightweight code generation model",
            "max_tokens": 2048,
            "temperature": 0.4,
            "use_cases": ["code_generation", "quick_tasks"],
            "performance": "medium",
            "memory_usage": "low"
        },
        "nomic-embed-text:latest": {
            "name": "Nomic Embed Text",
            "description": "Text embedding model for semantic search",
            "max_tokens": 512,
            "temperature": 0.0,
            "use_cases": ["embeddings", "similarity", "search"],
            "performance": "high",
            "memory_usage": "low"
        }
    }
    
    # Task-specific model assignments
    TASK_MODELS: Dict[str, str] = {
        "project_analysis": "llama3:8b",
        "portfolio_insights": "llama3:8b",
        "code_review": "codellama:7b-instruct-q4_K_M",
        "documentation": "mistral:7b-instruct-v0.2-q4_K_M",
        "risk_assessment": "llama3:8b",
        "resource_optimization": "llama3:8b",
        "timeline_analysis": "llama3:8b",
        "budget_analysis": "llama3:8b",
        "semantic_search": "nomic-embed-text:latest",
        "quick_tasks": "qwen2.5-coder:1.5b"
    }
    
    # AI Feature Flags
    AI_FEATURES_ENABLED: bool = True
    AI_COPILOT_ENABLED: bool = True
    AI_DASHBOARD_ENABLED: bool = True
    AI_PREDICTIONS_ENABLED: bool = True
    AI_RECOMMENDATIONS_ENABLED: bool = True
    
    # Security Configuration
    AI_API_KEY: str = ""
    AI_RATE_LIMITING_ENABLED: bool = True
    AI_CONTENT_FILTERING_ENABLED: bool = True
    
    # Monitoring Configuration
    AI_MONITORING_ENABLED: bool = True
    AI_METRICS_COLLECTION: bool = True
    AI_ERROR_TRACKING: bool = True
    
    class Config:
        env_file = ".env"
        case_sensitive = True


# Global AI configuration instance
ai_config = AIConfig()


def get_ai_config() -> AIConfig:
    """Get AI configuration instance."""
    return ai_config


def get_model_config(model_name: str) -> Dict[str, Any]:
    """Get configuration for a specific model."""
    return ai_config.MODEL_CONFIGS.get(model_name, {})


def get_task_model(task_type: str) -> str:
    """Get recommended model for a specific task type."""
    return ai_config.TASK_MODELS.get(task_type, ai_config.DEFAULT_MODEL)


def is_ai_feature_enabled(feature: str) -> bool:
    """Check if an AI feature is enabled."""
    feature_flags = {
        "ai_features": ai_config.AI_FEATURES_ENABLED,
        "ai_copilot": ai_config.AI_COPILOT_ENABLED,
        "ai_dashboard": ai_config.AI_DASHBOARD_ENABLED,
        "ai_predictions": ai_config.AI_PREDICTIONS_ENABLED,
        "ai_recommendations": ai_config.AI_RECOMMENDATIONS_ENABLED
    }
    return feature_flags.get(feature, False)


def get_available_models() -> List[str]:
    """Get list of available models."""
    return list(ai_config.MODEL_CONFIGS.keys())


def get_model_use_cases(model_name: str) -> List[str]:
    """Get use cases for a specific model."""
    config = get_model_config(model_name)
    return config.get("use_cases", [])


def get_model_performance_info(model_name: str) -> Dict[str, str]:
    """Get performance information for a specific model."""
    config = get_model_config(model_name)
    return {
        "performance": config.get("performance", "unknown"),
        "memory_usage": config.get("memory_usage", "unknown")
    }

from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import logging
from datetime import datetime

router = APIRouter()

# Configure logging
logger = logging.getLogger(__name__)

class FrontendLogEntry(BaseModel):
    level: str
    message: str
    module: str
    timestamp: Optional[str] = None
    url: Optional[str] = None
    user_agent: Optional[str] = None
    function: Optional[str] = None
    data: Optional[Dict[str, Any]] = None
    stack_trace: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

class FrontendLogRequest(BaseModel):
    logs: List[FrontendLogEntry]

@router.post("/frontend")
async def receive_frontend_logs(request: Request):
    """
    Receive and process frontend logs
    """
    try:
        # Get validated body from middleware
        request_data = getattr(request.state, 'validated_body', {})
        logs = request_data.get("logs", [])
        
        logger.info(f"🔍 [DEBUG] Received {len(logs)} frontend log entries")
        
        for log_entry in logs:
            # Extract log data with defaults
            level = log_entry.get("level", "INFO")
            message = log_entry.get("message", "No message")
            module = log_entry.get("module", "unknown")
            function_name = log_entry.get("function", "unknown")
            data = log_entry.get("data")
            url = log_entry.get("url", "unknown")
            user_agent = log_entry.get("user_agent", "unknown")
            
            # Convert frontend log level to Python logging level
            log_level = getattr(logging, level.upper(), logging.INFO)
            
            # Format the log message
            log_message = f"[{module}] {message}"
            if function_name and function_name != "unknown":
                log_message += f" ({function_name})"
            
            # Add data if available
            if data:
                log_message += f" | Data: {data}"
            
            # Add URL if available
            if url and url != "unknown":
                log_message += f" | URL: {url}"
            
            # Log the entry
            logger.log(log_level, log_message)
        
        return {"status": "success", "message": f"Processed {len(logs)} log entries"}
        
    except Exception as e:
        logger.error(f"Error processing frontend logs: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to process frontend logs")

@router.get("/frontend/health")
async def frontend_logs_health():
    """
    Health check for frontend logging endpoint
    """
    return {"status": "healthy", "message": "Frontend logging endpoint is operational"}

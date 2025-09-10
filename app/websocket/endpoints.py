"""
WebSocket endpoints for real-time communication
"""
import json
import asyncio
from typing import Dict, Any
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import logging

from app.websocket.connection_manager import connection_manager
from app.api.deps import get_current_user

logger = logging.getLogger(__name__)
security = HTTPBearer(auto_error=False)

router = APIRouter()

async def get_websocket_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Get user info for WebSocket connection (simplified for now)"""
    # TODO: Implement proper JWT validation for WebSocket
    return {
        "user_id": 1,
        "username": "admin",
        "role": "admin",
        "email": "admin@example.com"
    }

@router.websocket("/dashboard")
async def websocket_dashboard(websocket: WebSocket):
    """WebSocket endpoint for dashboard real-time updates"""
    await connection_manager.connect(websocket, "dashboard")
    
    try:
        while True:
            # Keep connection alive and handle incoming messages
            data = await websocket.receive_text()
            message = json.loads(data)
            
            # Handle different message types
            if message.get("type") == "ping":
                await connection_manager.send_personal_message({
                    "type": "pong",
                    "timestamp": asyncio.get_event_loop().time()
                }, websocket)
            elif message.get("type") == "subscribe":
                # Handle subscription to specific data types
                await connection_manager.send_personal_message({
                    "type": "subscribed",
                    "data_type": message.get("data_type"),
                    "timestamp": asyncio.get_event_loop().time()
                }, websocket)
            
    except WebSocketDisconnect:
        await connection_manager.disconnect(websocket)
    except Exception as e:
        logger.error(f"Dashboard WebSocket error: {e}")
        await connection_manager.disconnect(websocket)

@router.websocket("/projects")
async def websocket_projects(websocket: WebSocket):
    """WebSocket endpoint for project real-time updates"""
    await connection_manager.connect(websocket, "projects")
    
    try:
        while True:
            data = await websocket.receive_text()
            message = json.loads(data)
            
            # Handle project-specific messages
            if message.get("type") == "project_update":
                # Broadcast project updates to all project room subscribers
                await connection_manager.broadcast_to_room({
                    "type": "project_updated",
                    "project_id": message.get("project_id"),
                    "changes": message.get("changes"),
                    "timestamp": asyncio.get_event_loop().time()
                }, "projects", exclude=websocket)
            
    except WebSocketDisconnect:
        await connection_manager.disconnect(websocket)
    except Exception as e:
        logger.error(f"Projects WebSocket error: {e}")
        await connection_manager.disconnect(websocket)

@router.websocket("/resources")
async def websocket_resources(websocket: WebSocket):
    """WebSocket endpoint for resource real-time updates"""
    await connection_manager.connect(websocket, "resources")
    
    try:
        while True:
            data = await websocket.receive_text()
            message = json.loads(data)
            
            # Handle resource-specific messages
            if message.get("type") == "resource_update":
                await connection_manager.broadcast_to_room({
                    "type": "resource_updated",
                    "resource_id": message.get("resource_id"),
                    "changes": message.get("changes"),
                    "timestamp": asyncio.get_event_loop().time()
                }, "resources", exclude=websocket)
            
    except WebSocketDisconnect:
        await connection_manager.disconnect(websocket)
    except Exception as e:
        logger.error(f"Resources WebSocket error: {e}")
        await connection_manager.disconnect(websocket)

@router.websocket("/risks")
async def websocket_risks(websocket: WebSocket):
    """WebSocket endpoint for risk real-time updates"""
    await connection_manager.connect(websocket, "risks")
    
    try:
        while True:
            data = await websocket.receive_text()
            message = json.loads(data)
            
            # Handle risk-specific messages
            if message.get("type") == "risk_alert":
                await connection_manager.broadcast_to_room({
                    "type": "risk_alerted",
                    "risk_id": message.get("risk_id"),
                    "severity": message.get("severity"),
                    "message": message.get("message"),
                    "timestamp": asyncio.get_event_loop().time()
                }, "risks", exclude=websocket)
            
    except WebSocketDisconnect:
        await connection_manager.disconnect(websocket)
    except Exception as e:
        logger.error(f"Risks WebSocket error: {e}")
        await connection_manager.disconnect(websocket)

@router.websocket("/general")
async def websocket_general(websocket: WebSocket):
    """WebSocket endpoint for general real-time updates"""
    await connection_manager.connect(websocket, "general")
    
    try:
        while True:
            data = await websocket.receive_text()
            message = json.loads(data)
            
            # Handle general messages
            if message.get("type") == "broadcast":
                await connection_manager.broadcast_to_all({
                    "type": "broadcast_message",
                    "content": message.get("content"),
                    "sender": message.get("sender"),
                    "timestamp": asyncio.get_event_loop().time()
                }, exclude=websocket)
            
    except WebSocketDisconnect:
        await connection_manager.disconnect(websocket)
    except Exception as e:
        logger.error(f"General WebSocket error: {e}")
        await connection_manager.disconnect(websocket)

# HTTP endpoints for WebSocket management
@router.get("/stats")
async def get_websocket_stats():
    """Get WebSocket connection statistics"""
    return {
        "total_connections": connection_manager.get_connection_count(),
        "room_stats": connection_manager.get_room_stats(),
        "status": "active"
    }

@router.post("/broadcast")
async def broadcast_message(
    message: Dict[str, Any],
    room: str = "general",
    current_user: dict = Depends(get_current_user)
):
    """Broadcast a message to a specific room"""
    try:
        await connection_manager.broadcast_to_room(message, room)
        return {"status": "success", "message": "Broadcast sent"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Broadcast failed: {str(e)}")

@router.post("/queue")
async def queue_message(
    message: Dict[str, Any],
    room: str = "general",
    current_user: dict = Depends(get_current_user)
):
    """Queue a message for offline users"""
    try:
        connection_manager.queue_message(message, room)
        return {"status": "success", "message": "Message queued"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Queue failed: {str(e)}")

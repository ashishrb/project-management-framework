"""
WebSocket Connection Manager for real-time updates
"""
import json
import asyncio
from typing import Dict, List, Set
from fastapi import WebSocket, WebSocketDisconnect
import logging

logger = logging.getLogger(__name__)

class ConnectionManager:
    """Manages WebSocket connections and broadcasting"""
    
    def __init__(self):
        # Store active connections by room/type
        self.active_connections: Dict[str, Set[WebSocket]] = {
            "dashboard": set(),
            "projects": set(),
            "resources": set(),
            "risks": set(),
            "general": set()
        }
        
        # Store user sessions
        self.user_sessions: Dict[WebSocket, Dict] = {}
        
        # Message queue for offline users
        self.message_queue: Dict[str, List[Dict]] = {
            "dashboard": [],
            "projects": [],
            "resources": [],
            "risks": [],
            "general": []
        }
    
    async def connect(self, websocket: WebSocket, room: str = "general", user_info: Dict = None):
        """Accept a new WebSocket connection"""
        await websocket.accept()
        
        # Add to active connections
        self.active_connections[room].add(websocket)
        
        # Store user session info
        self.user_sessions[websocket] = {
            "room": room,
            "user_info": user_info or {},
            "connected_at": asyncio.get_event_loop().time()
        }
        
        logger.info(f"WebSocket connected to room '{room}': {websocket.client}")
        
        # Send any queued messages for this room
        await self._send_queued_messages(websocket, room)
    
    async def disconnect(self, websocket: WebSocket):
        """Handle WebSocket disconnection"""
        if websocket in self.user_sessions:
            room = self.user_sessions[websocket]["room"]
            self.active_connections[room].discard(websocket)
            del self.user_sessions[websocket]
            logger.info(f"WebSocket disconnected from room '{room}': {websocket.client}")
    
    async def send_personal_message(self, message: Dict, websocket: WebSocket):
        """Send a message to a specific WebSocket connection"""
        try:
            await websocket.send_text(json.dumps(message))
        except Exception as e:
            logger.error(f"Error sending personal message: {e}")
            await self.disconnect(websocket)
    
    async def broadcast_to_room(self, message: Dict, room: str, exclude: WebSocket = None):
        """Broadcast a message to all connections in a room"""
        if room not in self.active_connections:
            logger.warning(f"Room '{room}' not found")
            return
        
        # Send to all active connections in the room
        disconnected = set()
        for websocket in self.active_connections[room]:
            if websocket == exclude:
                continue
                
            try:
                await websocket.send_text(json.dumps(message))
            except Exception as e:
                logger.error(f"Error broadcasting to {websocket.client}: {e}")
                disconnected.add(websocket)
        
        # Clean up disconnected connections
        for websocket in disconnected:
            await self.disconnect(websocket)
    
    async def broadcast_to_all(self, message: Dict, exclude: WebSocket = None):
        """Broadcast a message to all active connections"""
        for room in self.active_connections:
            await self.broadcast_to_room(message, room, exclude)
    
    async def _send_queued_messages(self, websocket: WebSocket, room: str):
        """Send queued messages to a newly connected client"""
        if room in self.message_queue and self.message_queue[room]:
            for message in self.message_queue[room][-10:]:  # Send last 10 messages
                try:
                    await websocket.send_text(json.dumps(message))
                except Exception as e:
                    logger.error(f"Error sending queued message: {e}")
                    break
    
    def queue_message(self, message: Dict, room: str):
        """Queue a message for offline users"""
        if room in self.message_queue:
            self.message_queue[room].append(message)
            # Keep only last 50 messages per room
            if len(self.message_queue[room]) > 50:
                self.message_queue[room] = self.message_queue[room][-50:]
    
    def get_connection_count(self, room: str = None) -> int:
        """Get the number of active connections"""
        if room:
            return len(self.active_connections.get(room, set()))
        return sum(len(connections) for connections in self.active_connections.values())
    
    def get_room_stats(self) -> Dict[str, int]:
        """Get connection statistics for all rooms"""
        return {
            room: len(connections) 
            for room, connections in self.active_connections.items()
        }

# Global connection manager instance
connection_manager = ConnectionManager()

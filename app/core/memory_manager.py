"""
Memory Management & WebSocket Optimization
Provides memory leak prevention and connection management
"""

import asyncio
import gc
import psutil
import time
from typing import Dict, List, Set, Optional, Any
from datetime import datetime, timedelta
import logging
from collections import defaultdict
import weakref

logger = logging.getLogger(__name__)


class MemoryMonitor:
    """Memory usage monitoring and management"""
    
    def __init__(self):
        self.process = psutil.Process()
        self.memory_history = []
        self.peak_memory = 0
        self.memory_threshold = 500 * 1024 * 1024  # 500MB threshold
        self.cleanup_threshold = 400 * 1024 * 1024  # 400MB cleanup threshold
    
    def get_memory_usage(self) -> Dict[str, Any]:
        """Get current memory usage statistics"""
        memory_info = self.process.memory_info()
        memory_percent = self.process.memory_percent()
        
        return {
            "rss": memory_info.rss,  # Resident Set Size
            "vms": memory_info.vms,  # Virtual Memory Size
            "percent": memory_percent,
            "available": psutil.virtual_memory().available,
            "total": psutil.virtual_memory().total,
            "timestamp": datetime.now().isoformat()
        }
    
    def log_memory_usage(self, context: str = ""):
        """Log current memory usage"""
        memory_stats = self.get_memory_usage()
        
        # Update peak memory
        if memory_stats["rss"] > self.peak_memory:
            self.peak_memory = memory_stats["rss"]
        
        # Add to history
        self.memory_history.append({
            "context": context,
            "timestamp": datetime.now(),
            **memory_stats
        })
        
        # Keep only last 100 entries
        if len(self.memory_history) > 100:
            self.memory_history = self.memory_history[-100:]
        
        # Check thresholds
        if memory_stats["rss"] > self.memory_threshold:
            logger.warning(f"🚨 High memory usage: {memory_stats['rss'] / 1024 / 1024:.1f}MB")
            return True
        
        return False
    
    def force_garbage_collection(self):
        """Force garbage collection"""
        before_gc = self.get_memory_usage()
        
        # Run garbage collection
        collected = gc.collect()
        
        after_gc = self.get_memory_usage()
        freed_memory = before_gc["rss"] - after_gc["rss"]
        
        logger.info(f"🧹 Garbage collection: freed {freed_memory / 1024 / 1024:.1f}MB, collected {collected} objects")
        
        return freed_memory, collected
    
    def get_memory_summary(self) -> Dict[str, Any]:
        """Get memory usage summary"""
        current = self.get_memory_usage()
        
        return {
            "current": current,
            "peak": self.peak_memory,
            "history_count": len(self.memory_history),
            "threshold_exceeded": current["rss"] > self.memory_threshold,
            "cleanup_needed": current["rss"] > self.cleanup_threshold
        }


class WebSocketConnectionManager:
    """Optimized WebSocket connection management"""
    
    def __init__(self):
        self.connections: Dict[str, Dict[str, Any]] = {}
        self.rooms: Dict[str, Set[str]] = defaultdict(set)
        self.connection_limits = {
            "per_user": 5,
            "total": 1000,
            "per_room": 100
        }
        self.cleanup_interval = 300  # 5 minutes
        self.last_cleanup = time.time()
        self.connection_stats = {
            "total_connections": 0,
            "active_connections": 0,
            "cleaned_connections": 0,
            "peak_connections": 0
        }
    
    async def add_connection(self, connection_id: str, websocket, user_id: str = None, room: str = None):
        """Add a new WebSocket connection"""
        
        # Check connection limits
        if not self._check_connection_limits(user_id, room):
            logger.warning(f"🚫 Connection limit exceeded for user {user_id}")
            return False
        
        # Store connection info
        self.connections[connection_id] = {
            "websocket": websocket,
            "user_id": user_id,
            "room": room,
            "connected_at": datetime.now(),
            "last_activity": time.time(),
            "message_count": 0,
            "is_active": True
        }
        
        # Add to room if specified
        if room:
            self.rooms[room].add(connection_id)
        
        # Update stats
        self.connection_stats["total_connections"] += 1
        self.connection_stats["active_connections"] += 1
        
        if self.connection_stats["active_connections"] > self.connection_stats["peak_connections"]:
            self.connection_stats["peak_connections"] = self.connection_stats["active_connections"]
        
        logger.info(f"🔌 New connection: {connection_id} (user: {user_id}, room: {room})")
        return True
    
    async def remove_connection(self, connection_id: str):
        """Remove a WebSocket connection"""
        if connection_id not in self.connections:
            return
        
        connection = self.connections[connection_id]
        
        # Remove from room
        if connection["room"]:
            self.rooms[connection["room"]].discard(connection_id)
        
        # Close WebSocket
        try:
            await connection["websocket"].close()
        except Exception as e:
            logger.error(f"Error closing WebSocket {connection_id}: {e}")
        
        # Remove from connections
        del self.connections[connection_id]
        
        # Update stats
        self.connection_stats["active_connections"] -= 1
        
        logger.info(f"🔌 Connection removed: {connection_id}")
    
    async def update_activity(self, connection_id: str):
        """Update connection activity timestamp"""
        if connection_id in self.connections:
            self.connections[connection_id]["last_activity"] = time.time()
            self.connections[connection_id]["message_count"] += 1
    
    async def cleanup_inactive_connections(self):
        """Clean up inactive connections"""
        current_time = time.time()
        
        # Skip if cleanup was done recently
        if current_time - self.last_cleanup < self.cleanup_interval:
            return
        
        inactive_connections = []
        
        for connection_id, connection in self.connections.items():
            time_since_activity = current_time - connection["last_activity"]
            
            # Mark as inactive if no activity for 10 minutes
            if time_since_activity > 600:  # 10 minutes
                inactive_connections.append(connection_id)
        
        # Remove inactive connections
        for connection_id in inactive_connections:
            await self.remove_connection(connection_id)
            self.connection_stats["cleaned_connections"] += 1
        
        self.last_cleanup = current_time
        
        if inactive_connections:
            logger.info(f"🧹 Cleaned up {len(inactive_connections)} inactive connections")
    
    def _check_connection_limits(self, user_id: str = None, room: str = None) -> bool:
        """Check if connection limits are exceeded"""
        
        # Check total connection limit
        if self.connection_stats["active_connections"] >= self.connection_limits["total"]:
            return False
        
        # Check per-user limit
        if user_id:
            user_connections = sum(1 for conn in self.connections.values() 
                                 if conn["user_id"] == user_id)
            if user_connections >= self.connection_limits["per_user"]:
                return False
        
        # Check per-room limit
        if room:
            room_connections = len(self.rooms[room])
            if room_connections >= self.connection_limits["per_room"]:
                return False
        
        return True
    
    async def broadcast_to_room(self, room: str, message: Dict[str, Any]):
        """Broadcast message to all connections in a room"""
        if room not in self.rooms:
            return
        
        connections_to_remove = []
        
        for connection_id in self.rooms[room]:
            if connection_id in self.connections:
                connection = self.connections[connection_id]
                try:
                    await connection["websocket"].send_json(message)
                    await self.update_activity(connection_id)
                except Exception as e:
                    logger.error(f"Error broadcasting to {connection_id}: {e}")
                    connections_to_remove.append(connection_id)
            else:
                connections_to_remove.append(connection_id)
        
        # Remove failed connections
        for connection_id in connections_to_remove:
            self.rooms[room].discard(connection_id)
    
    def get_connection_stats(self) -> Dict[str, Any]:
        """Get connection statistics"""
        return {
            "stats": self.connection_stats.copy(),
            "limits": self.connection_limits.copy(),
            "rooms": {room: len(connections) for room, connections in self.rooms.items()},
            "connections_by_user": self._get_connections_by_user(),
            "connections_by_room": {room: len(connections) for room, connections in self.rooms.items()}
        }
    
    def _get_connections_by_user(self) -> Dict[str, int]:
        """Get connection count by user"""
        user_counts = defaultdict(int)
        for connection in self.connections.values():
            if connection["user_id"]:
                user_counts[connection["user_id"]] += 1
        return dict(user_counts)


class ResourceManager:
    """Resource management and cleanup"""
    
    def __init__(self):
        self.resources: Dict[str, Any] = {}
        self.cleanup_callbacks: List[callable] = []
        self.cleanup_interval = 60  # 1 minute
        self.last_cleanup = time.time()
    
    def register_resource(self, resource_id: str, resource: Any, cleanup_callback: callable = None):
        """Register a resource for management"""
        self.resources[resource_id] = {
            "resource": resource,
            "created_at": datetime.now(),
            "last_accessed": time.time(),
            "cleanup_callback": cleanup_callback
        }
        
        logger.debug(f"📦 Registered resource: {resource_id}")
    
    def unregister_resource(self, resource_id: str):
        """Unregister a resource"""
        if resource_id in self.resources:
            resource_info = self.resources[resource_id]
            
            # Call cleanup callback if available
            if resource_info["cleanup_callback"]:
                try:
                    resource_info["cleanup_callback"](resource_info["resource"])
                except Exception as e:
                    logger.error(f"Error in cleanup callback for {resource_id}: {e}")
            
            del self.resources[resource_id]
            logger.debug(f"🗑️ Unregistered resource: {resource_id}")
    
    def access_resource(self, resource_id: str):
        """Mark resource as accessed"""
        if resource_id in self.resources:
            self.resources[resource_id]["last_accessed"] = time.time()
    
    async def cleanup_unused_resources(self, max_age: int = 3600):
        """Clean up unused resources older than max_age seconds"""
        current_time = time.time()
        
        # Skip if cleanup was done recently
        if current_time - self.last_cleanup < self.cleanup_interval:
            return
        
        resources_to_remove = []
        
        for resource_id, resource_info in self.resources.items():
            age = current_time - resource_info["last_accessed"]
            
            if age > max_age:
                resources_to_remove.append(resource_id)
        
        # Remove unused resources
        for resource_id in resources_to_remove:
            self.unregister_resource(resource_id)
        
        self.last_cleanup = current_time
        
        if resources_to_remove:
            logger.info(f"🧹 Cleaned up {len(resources_to_remove)} unused resources")
    
    def get_resource_stats(self) -> Dict[str, Any]:
        """Get resource statistics"""
        current_time = time.time()
        
        stats = {
            "total_resources": len(self.resources),
            "resources_by_age": {
                "recent": 0,      # < 1 hour
                "old": 0,          # 1-24 hours
                "very_old": 0      # > 24 hours
            }
        }
        
        for resource_info in self.resources.values():
            age_hours = (current_time - resource_info["last_accessed"]) / 3600
            
            if age_hours < 1:
                stats["resources_by_age"]["recent"] += 1
            elif age_hours < 24:
                stats["resources_by_age"]["old"] += 1
            else:
                stats["resources_by_age"]["very_old"] += 1
        
        return stats


# Global instances
memory_monitor = MemoryMonitor()
websocket_manager = WebSocketConnectionManager()
resource_manager = ResourceManager()


class MemoryOptimizationService:
    """Centralized memory optimization service"""
    
    def __init__(self):
        self.optimization_enabled = True
        self.cleanup_schedule = []
    
    async def start_optimization(self):
        """Start memory optimization service"""
        logger.info("🚀 Starting memory optimization service")
        
        # Schedule periodic cleanup
        self.cleanup_schedule = [
            self._periodic_memory_check,
            self._periodic_websocket_cleanup,
            self._periodic_resource_cleanup,
            self._periodic_garbage_collection
        ]
        
        # Start cleanup tasks
        for cleanup_task in self.cleanup_schedule:
            asyncio.create_task(self._run_periodic_task(cleanup_task))
    
    async def _run_periodic_task(self, task_func):
        """Run a periodic task"""
        while self.optimization_enabled:
            try:
                await task_func()
                await asyncio.sleep(60)  # Run every minute
            except Exception as e:
                logger.error(f"Error in periodic task {task_func.__name__}: {e}")
                await asyncio.sleep(60)
    
    async def _periodic_memory_check(self):
        """Periodic memory usage check"""
        high_memory = memory_monitor.log_memory_usage("periodic_check")
        
        if high_memory:
            # Force garbage collection
            memory_monitor.force_garbage_collection()
    
    async def _periodic_websocket_cleanup(self):
        """Periodic WebSocket connection cleanup"""
        await websocket_manager.cleanup_inactive_connections()
    
    async def _periodic_resource_cleanup(self):
        """Periodic resource cleanup"""
        await resource_manager.cleanup_unused_resources()
    
    async def _periodic_garbage_collection(self):
        """Periodic garbage collection"""
        memory_monitor.force_garbage_collection()
    
    async def stop_optimization(self):
        """Stop memory optimization service"""
        self.optimization_enabled = False
        logger.info("🛑 Memory optimization service stopped")
    
    def get_optimization_status(self) -> Dict[str, Any]:
        """Get optimization service status"""
        return {
            "enabled": self.optimization_enabled,
            "memory_stats": memory_monitor.get_memory_summary(),
            "websocket_stats": websocket_manager.get_connection_stats(),
            "resource_stats": resource_manager.get_resource_stats()
        }


# Global optimization service
optimization_service = MemoryOptimizationService()

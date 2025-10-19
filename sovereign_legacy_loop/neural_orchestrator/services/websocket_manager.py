"""
🌐 WebSocket Manager
====================

Manages WebSocket connections for real-time updates to the website.
Provides live data streaming for the neural consciousness dashboard.
"""

import asyncio
import json
import logging
from typing import List, Dict, Any
from datetime import datetime

from fastapi import WebSocket
from models import (
    ConsciousnessValue, SystemHealth, WebSocketMessage,
    ConsciousnessUpdateMessage, HealthUpdateMessage, EmergencyMessage
)

logger = logging.getLogger(__name__)


class WebSocketManager:
    """Manages WebSocket connections for real-time updates."""
    
    def __init__(self):
        """Initialize the WebSocket manager."""
        self.active_connections: List[WebSocket] = []
        self.connection_info: Dict[WebSocket, Dict[str, Any]] = {}
        
        logger.info("🌐 WebSocket Manager initialized")
    
    async def connect(self, websocket: WebSocket):
        """Accept a new WebSocket connection."""
        await websocket.accept()
        self.active_connections.append(websocket)
        
        # Store connection info
        self.connection_info[websocket] = {
            "connected_at": datetime.utcnow(),
            "last_ping": datetime.utcnow(),
            "message_count": 0
        }
        
        logger.info(f"New WebSocket connection established. Total: {len(self.active_connections)}")
        
        # Send welcome message
        await self._send_to_connection(websocket, {
            "type": "welcome",
            "data": {
                "message": "Connected to Neural Orchestrator",
                "timestamp": datetime.utcnow().isoformat(),
                "service": "Neural Consciousness Dashboard"
            }
        })
    
    def disconnect(self, websocket: WebSocket):
        """Remove a WebSocket connection."""
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
            
        if websocket in self.connection_info:
            del self.connection_info[websocket]
        
        logger.info(f"WebSocket connection closed. Total: {len(self.active_connections)}")
    
    async def disconnect_all(self):
        """Disconnect all WebSocket connections."""
        logger.info("Disconnecting all WebSocket connections...")
        
        for websocket in self.active_connections.copy():
            try:
                await websocket.close()
            except Exception as e:
                logger.error(f"Error closing WebSocket: {e}")
        
        self.active_connections.clear()
        self.connection_info.clear()
        
        logger.info("All WebSocket connections closed")
    
    async def broadcast_consciousness_update(self):
        """Broadcast consciousness value update to all connected clients."""
        if not self.active_connections:
            return
        
        logger.debug("Broadcasting consciousness update...")
        
        try:
            # This would be called with actual data from the neural aggregator
            # For now, we'll send a placeholder message
            message = {
                "type": "consciousness_update",
                "data": {
                    "total": 8184.0,
                    "change_24h": 2.3,
                    "change_7d": 8.7,
                    "timestamp": datetime.utcnow().isoformat()
                }
            }
            
            await self._broadcast_message(message)
            
        except Exception as e:
            logger.error(f"Error broadcasting consciousness update: {e}")
    
    async def broadcast_health_update(self, health_data: SystemHealth):
        """Broadcast system health update to all connected clients."""
        if not self.active_connections:
            return
        
        logger.debug("Broadcasting health update...")
        
        try:
            message = {
                "type": "health_update",
                "data": {
                    "overall_status": health_data.overall_status,
                    "total_systems": health_data.total_systems,
                    "healthy_systems": health_data.healthy_systems,
                    "systems": [
                        {
                            "name": sys.name,
                            "status": sys.status,
                            "last_heartbeat": sys.last_heartbeat.isoformat() if sys.last_heartbeat else None,
                            "error_count": sys.error_count
                        }
                        for sys in health_data.systems
                    ],
                    "timestamp": datetime.utcnow().isoformat()
                }
            }
            
            await self._broadcast_message(message)
            
        except Exception as e:
            logger.error(f"Error broadcasting health update: {e}")
    
    async def broadcast_emergency_status(self):
        """Broadcast emergency status to all connected clients."""
        if not self.active_connections:
            return
        
        logger.warning("🚨 Broadcasting emergency status to all clients")
        
        try:
            message = {
                "type": "emergency",
                "data": {
                    "status": "EMERGENCY_STOP_EXECUTED",
                    "message": "All trading systems have been halted",
                    "timestamp": datetime.utcnow().isoformat(),
                    "severity": "CRITICAL"
                }
            }
            
            await self._broadcast_message(message)
            
        except Exception as e:
            logger.error(f"Error broadcasting emergency status: {e}")
    
    async def broadcast_tier_update(self, tier_type: str, tier_data: Dict[str, Any]):
        """Broadcast tier-specific update (Tier A or Tier B)."""
        if not self.active_connections:
            return
        
        logger.debug(f"Broadcasting {tier_type} update...")
        
        try:
            message = {
                "type": f"{tier_type.lower()}_update",
                "data": {
                    **tier_data,
                    "timestamp": datetime.utcnow().isoformat()
                }
            }
            
            await self._broadcast_message(message)
            
        except Exception as e:
            logger.error(f"Error broadcasting {tier_type} update: {e}")
    
    async def broadcast_shadow_ai_update(self, shadow_status: Dict[str, Any]):
        """Broadcast SHADOW.AI status update."""
        if not self.active_connections:
            return
        
        logger.debug("Broadcasting SHADOW.AI status update...")
        
        try:
            message = {
                "type": "shadow_ai_update",
                "data": {
                    **shadow_status,
                    "timestamp": datetime.utcnow().isoformat()
                }
            }
            
            await self._broadcast_message(message)
            
        except Exception as e:
            logger.error(f"Error broadcasting SHADOW.AI update: {e}")
    
    async def broadcast_migration_update(self, migration_data: Dict[str, Any]):
        """Broadcast migration status update."""
        if not self.active_connections:
            return
        
        logger.debug("Broadcasting migration status update...")
        
        try:
            message = {
                "type": "migration_update",
                "data": {
                    **migration_data,
                    "timestamp": datetime.utcnow().isoformat()
                }
            }
            
            await self._broadcast_message(message)
            
        except Exception as e:
            logger.error(f"Error broadcasting migration update: {e}")
    
    async def broadcast_custom_message(self, message_type: str, data: Dict[str, Any]):
        """Broadcast a custom message to all connected clients."""
        if not self.active_connections:
            return
        
        try:
            message = {
                "type": message_type,
                "data": {
                    **data,
                    "timestamp": datetime.utcnow().isoformat()
                }
            }
            
            await self._broadcast_message(message)
            
        except Exception as e:
            logger.error(f"Error broadcasting custom message: {e}")
    
    async def _broadcast_message(self, message: Dict[str, Any]):
        """Broadcast a message to all active connections."""
        if not self.active_connections:
            return
        
        message_json = json.dumps(message)
        disconnected_connections = []
        
        for websocket in self.active_connections:
            try:
                await websocket.send_text(message_json)
                
                # Update connection info
                if websocket in self.connection_info:
                    self.connection_info[websocket]["message_count"] += 1
                    self.connection_info[websocket]["last_ping"] = datetime.utcnow()
                
            except Exception as e:
                logger.warning(f"Failed to send message to WebSocket: {e}")
                disconnected_connections.append(websocket)
        
        # Remove disconnected connections
        for websocket in disconnected_connections:
            self.disconnect(websocket)
        
        if disconnected_connections:
            logger.info(f"Removed {len(disconnected_connections)} disconnected WebSockets")
    
    async def _send_to_connection(self, websocket: WebSocket, message: Dict[str, Any]):
        """Send a message to a specific WebSocket connection."""
        try:
            message_json = json.dumps(message)
            await websocket.send_text(message_json)
            
            # Update connection info
            if websocket in self.connection_info:
                self.connection_info[websocket]["message_count"] += 1
                self.connection_info[websocket]["last_ping"] = datetime.utcnow()
                
        except Exception as e:
            logger.error(f"Failed to send message to WebSocket: {e}")
            self.disconnect(websocket)
    
    def get_connection_stats(self) -> Dict[str, Any]:
        """Get statistics about WebSocket connections."""
        now = datetime.utcnow()
        
        total_connections = len(self.active_connections)
        total_messages = sum(info["message_count"] for info in self.connection_info.values())
        
        # Calculate average connection age
        connection_ages = []
        for info in self.connection_info.values():
            age = (now - info["connected_at"]).total_seconds()
            connection_ages.append(age)
        
        avg_connection_age = sum(connection_ages) / len(connection_ages) if connection_ages else 0
        
        return {
            "total_connections": total_connections,
            "total_messages_sent": total_messages,
            "average_connection_age_seconds": avg_connection_age,
            "connection_details": [
                {
                    "connected_at": info["connected_at"].isoformat(),
                    "message_count": info["message_count"],
                    "last_ping": info["last_ping"].isoformat()
                }
                for info in self.connection_info.values()
            ]
        }
    
    async def ping_all_connections(self):
        """Send ping to all connections to check if they're still alive."""
        if not self.active_connections:
            return
        
        logger.debug("Pinging all WebSocket connections...")
        
        ping_message = {
            "type": "ping",
            "data": {
                "timestamp": datetime.utcnow().isoformat()
            }
        }
        
        await self._broadcast_message(ping_message)
    
    async def cleanup_stale_connections(self, max_age_minutes: int = 60):
        """Clean up stale connections that haven't been active."""
        if not self.active_connections:
            return
        
        now = datetime.utcnow()
        stale_connections = []
        
        for websocket, info in self.connection_info.items():
            last_ping = info["last_ping"]
            age_minutes = (now - last_ping).total_seconds() / 60
            
            if age_minutes > max_age_minutes:
                stale_connections.append(websocket)
        
        for websocket in stale_connections:
            logger.info(f"Cleaning up stale WebSocket connection (age: {max_age_minutes}+ minutes)")
            try:
                await websocket.close()
            except Exception:
                pass  # Connection might already be closed
            self.disconnect(websocket)
        
        if stale_connections:
            logger.info(f"Cleaned up {len(stale_connections)} stale connections")

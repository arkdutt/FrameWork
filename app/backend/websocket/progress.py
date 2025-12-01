"""
WebSocket manager for real-time progress updates.
"""
from typing import Dict, Set, Any
from fastapi import WebSocket
from ..models.project_status import StageStatus
import json


class ConnectionManager:
    """Manages WebSocket connections."""
    
    def __init__(self):
        """Initialize connection manager."""
        # project_id -> set of WebSocket connections
        self.active_connections: Dict[str, Set[WebSocket]] = {}
    
    async def connect(self, websocket: WebSocket, project_id: str):
        """
        Accept and register a WebSocket connection.
        
        Args:
            websocket: WebSocket connection
            project_id: Project ID
        """
        await websocket.accept()
        
        if project_id not in self.active_connections:
            self.active_connections[project_id] = set()
        
        self.active_connections[project_id].add(websocket)
        print(f" WebSocket connected for project {project_id}")
    
    def disconnect(self, websocket: WebSocket, project_id: str):
        """
        Remove a WebSocket connection.
        
        Args:
            websocket: WebSocket connection
            project_id: Project ID
        """
        if project_id in self.active_connections:
            self.active_connections[project_id].discard(websocket)
            
            # Clean up empty sets
            if len(self.active_connections[project_id]) == 0:
                del self.active_connections[project_id]
        
        print(f" WebSocket disconnected for project {project_id}")
    
    async def send_to_project(self, project_id: str, message: dict):
        """
        Send message to all connections for a project.
        
        Args:
            project_id: Project ID
            message: Message dictionary
        """
        if project_id not in self.active_connections:
            return
        
        # Convert message to JSON
        message_json = json.dumps(message)
        
        # Send to all connections
        disconnected = set()
        for connection in self.active_connections[project_id]:
            try:
                await connection.send_text(message_json)
            except Exception as e:
                print(f" Error sending to WebSocket: {str(e)}")
                disconnected.add(connection)
        
        # Remove disconnected connections
        for connection in disconnected:
            self.disconnect(connection, project_id)
    
    async def broadcast(self, message: dict):
        """
        Broadcast message to all connections.
        
        Args:
            message: Message dictionary
        """
        message_json = json.dumps(message)
        
        for project_id, connections in self.active_connections.items():
            disconnected = set()
            for connection in connections:
                try:
                    await connection.send_text(message_json)
                except Exception as e:
                    print(f" Error broadcasting to WebSocket: {str(e)}")
                    disconnected.add(connection)
            
            # Remove disconnected connections
            for connection in disconnected:
                self.disconnect(connection, project_id)


class WebSocketManager:
    """Static manager for WebSocket operations."""
    
    manager = ConnectionManager()
    
    @classmethod
    async def broadcast_progress(
        cls,
        project_id: str,
        stage: str,
        status: StageStatus,
        message: str = "",
        data: Dict[str, Any] = None
    ):
        """
        Broadcast progress update to all connections for a project.
        
        Args:
            project_id: Project ID
            stage: Stage name ("script", "storyboard", "shot_list")
            status: Stage status
            message: Optional message
            data: Optional additional data
        """
        message_dict = {
            "type": "progress",
            "project_id": project_id,
            "stage": stage,
            "status": status.value,
            "message": message,
            "data": data or {}
        }
        
        await cls.manager.send_to_project(project_id, message_dict)
    
    @classmethod
    async def send_error(
        cls,
        project_id: str,
        error: str
    ):
        """
        Send error message to all connections for a project.
        
        Args:
            project_id: Project ID
            error: Error message
        """
        message_dict = {
            "type": "error",
            "project_id": project_id,
            "error": error
        }
        
        await cls.manager.send_to_project(project_id, message_dict)
    
    @classmethod
    async def send_completion(
        cls,
        project_id: str
    ):
        """
        Send completion message to all connections for a project.
        
        Args:
            project_id: Project ID
        """
        message_dict = {
            "type": "completed",
            "project_id": project_id,
            "message": "Project completed successfully"
        }
        
        await cls.manager.send_to_project(project_id, message_dict)



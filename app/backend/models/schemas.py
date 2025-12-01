"""
Pydantic models for API requests and database documents.
"""
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime
from bson import ObjectId
from .project_status import StageStatus, ProjectStatus


class PyObjectId(ObjectId):
    """Custom type for MongoDB ObjectId."""
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid ObjectId")
        return ObjectId(v)

    @classmethod
    def __get_pydantic_json_schema__(cls, field_schema):
        field_schema.update(type="string")


class StageInfo(BaseModel):
    """Information about a single stage."""
    status: StageStatus = StageStatus.PENDING
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    error: Optional[str] = None


class Classification(BaseModel):
    """Result of input classification."""
    script: bool = False
    storyboard: bool = False
    shot_list: bool = False


class CreateProjectRequest(BaseModel):
    """Request to create a new project."""
    user_prompt: str = Field(..., description="User's input prompt")
    title: Optional[str] = Field(None, description="Optional project title")


class ProjectResponse(BaseModel):
    """Response containing project information."""
    id: str = Field(alias="_id")
    title: Optional[str]
    user_prompt: str
    status: ProjectStatus
    classification: Optional[Classification]
    
    # Stage tracking
    script_stage: StageInfo
    storyboard_stage: StageInfo
    shot_list_stage: StageInfo
    
    # Generated content
    script: Optional[str] = None
    storyboard: Optional[List[Dict[str, Any]]] = None
    shot_list: Optional[List[Dict[str, Any]]] = None
    
    created_at: datetime
    updated_at: datetime
    
    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}


class RunProjectRequest(BaseModel):
    """Request to run the project pipeline."""
    force_rerun: bool = Field(default=False, description="Force rerun even if completed")


class UpdateScriptRequest(BaseModel):
    """Request to update a project's script."""
    script: str = Field(..., description="Updated script content")


class WebSocketMessage(BaseModel):
    """WebSocket message format."""
    project_id: str
    stage: str  # "script" | "storyboard" | "shot_list"
    status: StageStatus
    message: Optional[str] = None
    data: Optional[Dict[str, Any]] = None



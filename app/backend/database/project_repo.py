"""
CRUD operations for projects.
"""
from typing import Optional, Dict, Any, List
from datetime import datetime
from bson import ObjectId
from .mongodb import MongoDB
from ..models.schemas import Classification, StageInfo
from ..models.project_status import ProjectStatus, StageStatus


class ProjectRepository:
    """Repository for project operations."""
    
    COLLECTION_NAME = "projects"
    
    @classmethod
    def get_collection(cls):
        """Get projects collection."""
        return MongoDB.get_collection(cls.COLLECTION_NAME)
    
    @classmethod
    async def create_project(
        cls,
        user_prompt: str,
        title: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Create a new project.
        
        Args:
            user_prompt: User's input prompt
            title: Optional project title
            
        Returns:
            Created project document
        """
        now = datetime.utcnow()
        
        project = {
            "title": title or f"Project {now.strftime('%Y-%m-%d %H:%M')}",
            "user_prompt": user_prompt,
            "status": ProjectStatus.CREATED,
            "classification": None,
            
            # Stage tracking
            "script_stage": {
                "status": StageStatus.PENDING,
                "started_at": None,
                "completed_at": None,
                "error": None
            },
            "storyboard_stage": {
                "status": StageStatus.PENDING,
                "started_at": None,
                "completed_at": None,
                "error": None
            },
            "shot_list_stage": {
                "status": StageStatus.PENDING,
                "started_at": None,
                "completed_at": None,
                "error": None
            },
            
            # Generated content
            "script": None,
            "storyboard": None,
            "shot_list": None,
            
            "created_at": now,
            "updated_at": now
        }
        
        collection = cls.get_collection()
        result = await collection.insert_one(project)
        project["_id"] = str(result.inserted_id)
        
        return project
    
    @classmethod
    async def get_project(cls, project_id: str) -> Optional[Dict[str, Any]]:
        """
        Get project by ID.
        
        Args:
            project_id: Project ID
            
        Returns:
            Project document or None
        """
        if not ObjectId.is_valid(project_id):
            return None
        
        collection = cls.get_collection()
        project = await collection.find_one({"_id": ObjectId(project_id)})
        
        if project:
            project["_id"] = str(project["_id"])
        
        return project
    
    @classmethod
    async def update_status(
        cls,
        project_id: str,
        status: ProjectStatus
    ) -> bool:
        """
        Update project status.
        
        Args:
            project_id: Project ID
            status: New status
            
        Returns:
            True if updated, False otherwise
        """
        if not ObjectId.is_valid(project_id):
            return False
        
        collection = cls.get_collection()
        result = await collection.update_one(
            {"_id": ObjectId(project_id)},
            {
                "$set": {
                    "status": status,
                    "updated_at": datetime.utcnow()
                }
            }
        )
        
        return result.modified_count > 0
    
    @classmethod
    async def save_classification(
        cls,
        project_id: str,
        classification: Classification
    ) -> bool:
        """
        Save classification result.
        
        Args:
            project_id: Project ID
            classification: Classification result
            
        Returns:
            True if saved, False otherwise
        """
        if not ObjectId.is_valid(project_id):
            return False
        
        collection = cls.get_collection()
        result = await collection.update_one(
            {"_id": ObjectId(project_id)},
            {
                "$set": {
                    "classification": classification.dict(),
                    "updated_at": datetime.utcnow()
                }
            }
        )
        
        return result.modified_count > 0
    
    @classmethod
    async def update_stage(
        cls,
        project_id: str,
        stage: str,
        status: StageStatus,
        error: Optional[str] = None
    ) -> bool:
        """
        Update stage status.
        
        Args:
            project_id: Project ID
            stage: Stage name ("script", "storyboard", "shot_list")
            status: New status
            error: Optional error message
            
        Returns:
            True if updated, False otherwise
        """
        if not ObjectId.is_valid(project_id):
            return False
        
        now = datetime.utcnow()
        stage_field = f"{stage}_stage"
        
        update_data = {
            f"{stage_field}.status": status,
            "updated_at": now
        }
        
        if status == StageStatus.RUNNING:
            update_data[f"{stage_field}.started_at"] = now
        elif status in [StageStatus.DONE, StageStatus.FAILED]:
            update_data[f"{stage_field}.completed_at"] = now
        
        if error:
            update_data[f"{stage_field}.error"] = error
        
        collection = cls.get_collection()
        result = await collection.update_one(
            {"_id": ObjectId(project_id)},
            {"$set": update_data}
        )
        
        return result.modified_count > 0
    
    @classmethod
    async def save_script(
        cls,
        project_id: str,
        script: str
    ) -> bool:
        """
        Save generated script.
        
        Args:
            project_id: Project ID
            script: Generated script content
            
        Returns:
            True if saved, False otherwise
        """
        if not ObjectId.is_valid(project_id):
            return False
        
        collection = cls.get_collection()
        result = await collection.update_one(
            {"_id": ObjectId(project_id)},
            {
                "$set": {
                    "script": script,
                    "updated_at": datetime.utcnow()
                }
            }
        )
        
        return result.modified_count > 0
    
    @classmethod
    async def update_script(cls, project_id: str, script: str) -> bool:
        """Alias for save_script - saves user-provided or generated script."""
        return await cls.save_script(project_id, script)
    
    @classmethod
    async def save_storyboard(
        cls,
        project_id: str,
        storyboard: List[Dict[str, Any]]
    ) -> bool:
        """
        Save generated storyboard.
        
        Args:
            project_id: Project ID
            storyboard: List of storyboard frames
            
        Returns:
            True if saved, False otherwise
        """
        if not ObjectId.is_valid(project_id):
            return False
        
        collection = cls.get_collection()
        result = await collection.update_one(
            {"_id": ObjectId(project_id)},
            {
                "$set": {
                    "storyboard": storyboard,
                    "updated_at": datetime.utcnow()
                }
            }
        )
        
        return result.modified_count > 0
    
    @classmethod
    async def save_shot_list(
        cls,
        project_id: str,
        shot_list: List[Dict[str, Any]]
    ) -> bool:
        """
        Save generated shot list.
        
        Args:
            project_id: Project ID
            shot_list: List of shots
            
        Returns:
            True if saved, False otherwise
        """
        if not ObjectId.is_valid(project_id):
            return False
        
        collection = cls.get_collection()
        result = await collection.update_one(
            {"_id": ObjectId(project_id)},
            {
                "$set": {
                    "shot_list": shot_list,
                    "updated_at": datetime.utcnow()
                }
            }
        )
        
        return result.modified_count > 0



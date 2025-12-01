"""
Status enums and constants for project workflow.
"""
from enum import Enum


class StageStatus(str, Enum):
    """Status of individual stages."""
    PENDING = "pending"
    RUNNING = "running"
    DONE = "done"
    FAILED = "failed"


class ProjectStage(str, Enum):
    """Available project stages."""
    SCRIPT = "script"
    STORYBOARD = "storyboard"
    SHOT_LIST = "shot_list"


class ProjectStatus(str, Enum):
    """Overall project status."""
    CREATED = "created"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"



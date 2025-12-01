"""
Pipeline - Sequential execution controller for agents.
"""
from typing import Dict, Any
from ..orchestrator.router import Router
from ..agents.script_agent import ScriptAgent
from ..agents.storyboard_agent import StoryboardAgent
from ..agents.shot_list_agent import ShotListAgent
from ..database.project_repo import ProjectRepository
from ..models.project_status import ProjectStatus, StageStatus
from ..websocket.progress import WebSocketManager


class Pipeline:
    """
    Controls the sequential execution of agents.
    """
    
    def __init__(self):
        """Initialize the pipeline."""
        self.router = Router()
        self.script_agent = ScriptAgent()
        self.storyboard_agent = StoryboardAgent()
        self.shot_list_agent = ShotListAgent()
    
    async def run(self, project_id: str, skip_script: bool = False):
        """
        Run the complete pipeline for a project.
        
        Args:
            project_id: Project ID
            skip_script: If True, skip script generation (used when script was manually edited)
        """
        try:
            # Get project
            project = await ProjectRepository.get_project(project_id)
            if not project:
                raise ValueError(f"Project {project_id} not found")
            
            # Update status to processing
            await ProjectRepository.update_status(project_id, ProjectStatus.PROCESSING)
            
            # Classify and determine routing
            classification = await self.router.classify_and_route(project)
            agent_sequence = self.router.determine_agent_sequence(classification)
            
            # If skip_script is True, remove script from sequence
            if skip_script and "script" in agent_sequence:
                agent_sequence.remove("script")
                print(f"⏭  Skipping script agent (script was manually edited)")
            
            print(f" Starting pipeline for project {project_id}")
            print(f" Agent sequence: {agent_sequence}")
            
            # Execute agents in sequence
            for agent_name in agent_sequence:
                # Refresh project data before each agent
                project = await ProjectRepository.get_project(project_id)
                
                if agent_name == "script":
                    await self._run_script_agent(project)
                elif agent_name == "storyboard":
                    await self._run_storyboard_agent(project)
                elif agent_name == "shot_list":
                    await self._run_shot_list_agent(project)
            
            # Mark project as completed
            await ProjectRepository.update_status(project_id, ProjectStatus.COMPLETED)
            print(f" Pipeline completed for project {project_id}")
            
        except Exception as e:
            print(f" Pipeline failed for project {project_id}: {str(e)}")
            await ProjectRepository.update_status(project_id, ProjectStatus.FAILED)
            raise
    
    async def _run_script_agent(self, project: Dict[str, Any]):
        """Run the script agent."""
        project_id = project["_id"]
        stage = "script"
        
        try:
            print(f" Running script agent for project {project_id}")
            
            # Update stage status
            await ProjectRepository.update_stage(project_id, stage, StageStatus.RUNNING)
            await WebSocketManager.broadcast_progress(
                project_id, stage, StageStatus.RUNNING, "Generating script..."
            )
            
            # Run agent
            script = await self.script_agent.run(project)
            
            # Save result
            await ProjectRepository.save_script(project_id, script)
            
            # Update stage status
            await ProjectRepository.update_stage(project_id, stage, StageStatus.DONE)
            await WebSocketManager.broadcast_progress(
                project_id, stage, StageStatus.DONE, "Script generated"
            )
            
            print(f" Script agent completed for project {project_id}")
            
        except Exception as e:
            print(f" Script agent failed: {str(e)}")
            await ProjectRepository.update_stage(
                project_id, stage, StageStatus.FAILED, str(e)
            )
            await WebSocketManager.broadcast_progress(
                project_id, stage, StageStatus.FAILED, f"Error: {str(e)}"
            )
            raise
    
    async def _run_storyboard_agent(self, project: Dict[str, Any]):
        """Run the storyboard agent."""
        project_id = project["_id"]
        stage = "storyboard"
        
        try:
            print(f" Running storyboard agent for project {project_id}")
            
            # Update stage status
            await ProjectRepository.update_stage(project_id, stage, StageStatus.RUNNING)
            await WebSocketManager.broadcast_progress(
                project_id, stage, StageStatus.RUNNING, "Generating storyboard..."
            )
            
            # Run agent
            storyboard = await self.storyboard_agent.run(project)
            
            # Save result
            await ProjectRepository.save_storyboard(project_id, storyboard)
            
            # Update stage status
            await ProjectRepository.update_stage(project_id, stage, StageStatus.DONE)
            await WebSocketManager.broadcast_progress(
                project_id, stage, StageStatus.DONE, "Storyboard generated"
            )
            
            print(f" Storyboard agent completed for project {project_id}")
            
        except Exception as e:
            print(f" Storyboard agent failed: {str(e)}")
            await ProjectRepository.update_stage(
                project_id, stage, StageStatus.FAILED, str(e)
            )
            await WebSocketManager.broadcast_progress(
                project_id, stage, StageStatus.FAILED, f"Error: {str(e)}"
            )
            raise
    
    async def _run_shot_list_agent(self, project: Dict[str, Any]):
        """Run the shot list agent."""
        project_id = project["_id"]
        stage = "shot_list"
        
        try:
            print(f" Running shot list agent for project {project_id}")
            
            # Update stage status
            await ProjectRepository.update_stage(project_id, stage, StageStatus.RUNNING)
            await WebSocketManager.broadcast_progress(
                project_id, stage, StageStatus.RUNNING, "Generating shot list..."
            )
            
            # Run agent
            shot_list = await self.shot_list_agent.run(project)
            
            # Save result
            await ProjectRepository.save_shot_list(project_id, shot_list)
            
            # Update stage status
            await ProjectRepository.update_stage(project_id, stage, StageStatus.DONE)
            await WebSocketManager.broadcast_progress(
                project_id, stage, StageStatus.DONE, "Shot list generated"
            )
            
            print(f" Shot list agent completed for project {project_id}")
            
        except Exception as e:
            print(f" Shot list agent failed: {str(e)}")
            await ProjectRepository.update_stage(
                project_id, stage, StageStatus.FAILED, str(e)
            )
            await WebSocketManager.broadcast_progress(
                project_id, stage, StageStatus.FAILED, f"Error: {str(e)}"
            )
            raise



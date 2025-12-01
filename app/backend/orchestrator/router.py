"""
Router - Handles classification and agent routing.
"""
from typing import Dict, Any
from ..classifiers.input_classifier import InputClassifier
from ..models.schemas import Classification
from ..database.project_repo import ProjectRepository
from ..models.project_status import StageStatus


class Router:
    """
    Routes user input to appropriate agents based on classification.
    """
    
    def __init__(self):
        """Initialize the router."""
        self.classifier = InputClassifier()
    
    async def classify_and_route(self, project: Dict[str, Any]) -> Classification:
        """
        Classify user input and determine routing.
        
        Also extracts and saves user-provided content and updates stage status.
        
        Args:
            project: Project document
            
        Returns:
            Classification result
        """
        user_prompt = project.get("user_prompt", "")
        project_id = project.get("_id")
        
        # Classify the input
        classification = await self.classifier.classify_user_input(user_prompt)
        
        # If user provided a script, extract and save it + mark stage as done
        if classification.script:
            user_script = self.classifier.extract_user_script(user_prompt)
            if user_script and project_id:
                print(f" Saving user-provided script to database")
                await ProjectRepository.update_script(project_id, user_script)
                # Mark script stage as done (user provided it)
                await ProjectRepository.update_stage(project_id, "script", StageStatus.DONE)
                print(f" Marked script stage as DONE (user-provided)")
        
        # If user provided storyboard, mark as done
        if classification.storyboard and project_id:
            await ProjectRepository.update_stage(project_id, "storyboard", StageStatus.DONE)
            print(f" Marked storyboard stage as DONE (user-provided)")
        
        # If user provided shot list, mark as done
        if classification.shot_list and project_id:
            await ProjectRepository.update_stage(project_id, "shot_list", StageStatus.DONE)
            print(f" Marked shot list stage as DONE (user-provided)")
        
        # Save classification to database
        if project_id:
            await ProjectRepository.save_classification(project_id, classification)
        
        return classification
    
    def determine_agent_sequence(self, classification: Classification) -> list:
        """
        Determine the sequence of agents to run.
        
        Uses INVERSE LOGIC: Classification indicates what user ALREADY HAS.
        - False = User doesn't have it → Generate it
        - True = User has it → Skip generation (user provided it)
        
        Args:
            classification: Classification result (what user already has)
            
        Returns:
            List of agent names in execution order
        """
        sequence = []
        
        # INVERSE LOGIC: Only generate what's missing (False values)
        
        # 1. Script
        if not classification.script:
            # User doesn't have script → generate it
            sequence.append("script")
        else:
            # User HAS script → don't regenerate, it's already saved
            print(" User provided script - skipping script generation")
        
        # 2. Storyboard
        if not classification.storyboard:
            # User wants storyboard generated
            # Storyboard requires script - but user may have provided it
            sequence.append("storyboard")
        
        # 3. Shot List
        if not classification.shot_list:
            # User wants shot list generated
            # Shot list requires storyboard
            if "storyboard" not in sequence and not classification.storyboard:
                # Need to generate storyboard first
                sequence.append("storyboard")
            sequence.append("shot_list")
        
        return sequence



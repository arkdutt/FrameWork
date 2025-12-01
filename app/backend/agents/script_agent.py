"""
Script Agent - Generates scripts from user prompts.

Uses Google Gemini to generate professional screenplays.
"""
from typing import Dict, Any
import google.generativeai as genai
from ..config.settings import settings


class ScriptAgent:
    """
    Agent responsible for generating film scripts.
    
    Uses Gemini AI to create properly formatted screenplays
    following industry-standard formatting conventions.
    """
    
    def __init__(self):
        """Initialize the script agent with Gemini API."""
        genai.configure(api_key=settings.gemini_api_key)
        
        # Configure safety settings to allow creative content
        safety_settings = [
            {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"},
        ]
        
        self.model = genai.GenerativeModel(
            'gemini-pro-latest',
            safety_settings=safety_settings
        )
    
    async def run(self, project: Dict[str, Any]) -> str:
        """
        Generate a script based on the project prompt.
        
        Args:
            project: Project document containing user_prompt and other data
            
        Returns:
            Generated script as a string in proper screenplay format
        """
        user_prompt = project.get("user_prompt", "")
        
        # Check if user already provided a script
        if project.get("script"):
            print(" Script already exists, skipping generation")
            return project.get("script")
        
        system_prompt = """You are a professional screenwriter. Generate a properly formatted screenplay based on the user's prompt.

SCREENPLAY FORMAT RULES:
1. Use standard screenplay formatting:
   - FADE IN: at the beginning
   - FADE OUT. at the end
   - Scene headings in ALL CAPS: INT./EXT. LOCATION - TIME
   - Character names in ALL CAPS before dialogue
   - Action lines in regular case
   - Dialogue indented appropriately

2. Include:
   - Clear scene descriptions
   - Character development
   - Natural dialogue
   - Visual storytelling elements
   - Proper scene transitions

3. Length guidelines:
   - Short film (2-5 min): 2-5 pages
   - Medium (5-15 min): 5-15 pages
   - Commercial (30-60 sec): 1 page
   - Adapt based on user's requirements

4. Be creative and professional

User's project prompt:
"""

        try:
            print(f" Generating script for prompt: {user_prompt[:100]}...")
            
            response = self.model.generate_content(
                system_prompt + user_prompt,
                generation_config={
                    "temperature": 0.8,
                    "top_p": 0.95,
                    "top_k": 40,
                    "max_output_tokens": 8000,
                }
            )
            
            # Check if response was blocked
            if not response.candidates or not response.candidates[0].content.parts:
                finish_reason = response.candidates[0].finish_reason if response.candidates else "UNKNOWN"
                raise ValueError(f"Content generation blocked. Finish reason: {finish_reason}. This may be due to safety filters.")
            
            script = response.text.strip()
            
            # Ensure proper formatting
            if not script.startswith("FADE IN"):
                script = "FADE IN:\n\n" + script
            if not script.endswith("FADE OUT."):
                script = script + "\n\nFADE OUT."
            
            print(f" Script generated successfully ({len(script)} characters)")
            return script
            
        except Exception as e:
            print(f" Script generation failed: {str(e)}")
            # Return a basic script structure as fallback
            fallback_script = f"""FADE IN:

INT. SCENE - DAY

A story unfolds based on the prompt: {user_prompt[:200]}...

[Script generation encountered an error: {str(e)}]

FADE OUT."""
            return fallback_script
    
    async def validate_output(self, script: str) -> bool:
        """
        Validate the generated script.
        
        Args:
            script: Generated script
            
        Returns:
            True if valid, False otherwise
        """
        if not script or len(script) < 50:
            return False
        
        # Check for basic screenplay elements
        script_upper = script.upper()
        has_fade_in = "FADE IN" in script_upper
        has_fade_out = "FADE OUT" in script_upper
        has_scene_heading = any(x in script_upper for x in ["INT.", "EXT."])
        
        return has_fade_in and has_fade_out and has_scene_heading



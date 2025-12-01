"""
Shot List Agent - Generates detailed shot lists from storyboards.

Uses Google Gemini to create comprehensive technical shot breakdowns.
"""
from typing import Dict, Any, List
import google.generativeai as genai
import json
from ..config.settings import settings


class ShotListAgent:
    """
    Agent responsible for generating shot lists.
    
    Uses Gemini AI to analyze storyboards and create detailed technical
    shot lists with camera angles, movements, equipment, and timing.
    """
    
    def __init__(self):
        """Initialize the shot list agent with Gemini API."""
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
    
    async def run(self, project: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Generate a shot list based on the project storyboard.
        
        Args:
            project: Project document containing storyboard and other data
            
        Returns:
            List of shots, each containing:
            - shot_number: int
            - scene: str
            - shot_type: str (e.g., "Wide Shot", "Medium Shot", "Close-up")
            - camera_movement: str (e.g., "Static", "Pan", "Dolly", "Tracking")
            - description: str
            - duration: str (e.g., "5 seconds", "3-4 seconds")
            - equipment: List[str] (e.g., ["Camera", "Tripod", "Slider"])
            - lens: str (e.g., "50mm", "24-70mm zoom")
            - notes: str (additional technical notes)
        """
        storyboard = project.get("storyboard", [])
        script = project.get("script", "")
        
        if not storyboard:
            raise ValueError("Storyboard is required to generate shot list")
        
        # Check if shot list already exists
        if project.get("shot_list"):
            print(" Shot list already exists, skipping generation")
            return project.get("shot_list")
        
        system_prompt = """You are an expert cinematographer and director of photography. Create a detailed, professional shot list based on the provided storyboard for a film production.

CRITICAL REQUIREMENT: Create AT LEAST ONE shot for EVERY storyboard frame provided. If the storyboard has 12 frames, generate AT LEAST 12 shots.

TASK: Transform each storyboard frame into one or more technical shots with camera specifications.

For EACH shot, provide a JSON object with:
1. shot_number: Sequential number
2. scene: Scene identifier from the storyboard
3. shot_type: Choose from Wide Shot, Medium Shot, Close-Up, Over-the-Shoulder, POV, etc.
4. camera_movement: Choose from Static, Pan, Tilt, Dolly, Tracking, Handheld, Steadicam, etc.
5. description: Technical description of the shot
6. duration: Estimated duration (e.g., "3-5 seconds")
7. equipment: Array of equipment (e.g., ["Camera", "Tripod", "Slider"])
8. lens: Recommended lens (e.g., "50mm f/1.8", "24-70mm zoom")
9. notes: Technical notes for the crew

Return ONLY a valid JSON array. No markdown, no explanations. Ensure you create at least one shot per storyboard frame.

Example:
[
  {
    "shot_number": 1,
    "scene": "Scene 1",
    "shot_type": "Wide Shot",
    "camera_movement": "Static",
    "description": "Establishing shot of location",
    "duration": "5 seconds",
    "equipment": ["Camera", "Tripod"],
    "lens": "24mm",
    "notes": "Natural lighting"
  }
]

STORYBOARD:
"""

        try:
            print(f" Generating shot list from storyboard ({len(storyboard)} frames)...")
            
            # Sanitize storyboard data - only send essential info to avoid safety filters
            # Remove image URLs and keep only scene descriptions
            sanitized_storyboard = []
            for frame in storyboard:
                sanitized_storyboard.append({
                    "frame_number": frame.get("frame_number", 0),
                    "scene": frame.get("scene", ""),
                    "description": frame.get("description", ""),
                    "camera_angle": frame.get("camera_angle", "Medium Shot"),
                    "dialogue": frame.get("dialogue", ""),
                })
            
            storyboard_text = json.dumps(sanitized_storyboard, indent=2)
            
            response = self.model.generate_content(
                system_prompt + storyboard_text,
                generation_config={
                    "temperature": 0.6,
                    "top_p": 0.9,
                    "top_k": 40,
                    "max_output_tokens": 4000,
                    "response_mime_type": "application/json",
                }
            )
            
            # Check if response was blocked
            if not response.candidates or not response.candidates[0].content.parts:
                finish_reason = response.candidates[0].finish_reason if response.candidates else "UNKNOWN"
                raise ValueError(f"Content generation blocked. Finish reason: {finish_reason}. This may be due to safety filters.")
            
            result_text = response.text.strip()
            
            # Clean up response (remove markdown code blocks if present)
            if "```json" in result_text:
                result_text = result_text.split("```json")[1].split("```")[0].strip()
            elif "```" in result_text:
                result_text = result_text.split("```")[1].split("```")[0].strip()
            
            # Additional cleanup for malformed JSON
            # Sometimes Gemini adds trailing commas or comments
            result_text = result_text.replace(",]", "]").replace(",}", "}")
            
            # Remove any text before the first [ or {
            if "[" in result_text:
                result_text = result_text[result_text.index("["):]
            elif "{" in result_text:
                result_text = result_text[result_text.index("{"):]
            
            # Remove any text after the last ] or }
            if "]" in result_text:
                result_text = result_text[:result_text.rindex("]")+1]
            elif "}" in result_text:
                result_text = result_text[:result_text.rindex("}")+1]
            
            # Parse JSON
            try:
                shot_list = json.loads(result_text)
            except json.JSONDecodeError as json_err:
                print(f"  JSON parse error: {json_err}")
                print(f" Problematic JSON (first 500 chars): {result_text[:500]}")
                # Try to fix common JSON issues
                result_text = result_text.replace("'", '"')  # Single to double quotes
                result_text = result_text.replace("\n", " ")  # Remove newlines in strings
                shot_list = json.loads(result_text)  # Retry
            
            # Validate structure
            if not isinstance(shot_list, list):
                raise ValueError("Shot list must be a list")
            
            # Ensure all shots have required fields
            for i, shot in enumerate(shot_list):
                if "shot_number" not in shot:
                    shot["shot_number"] = i + 1
                if "shot_type" not in shot:
                    shot["shot_type"] = "Medium Shot"
                if "camera_movement" not in shot:
                    shot["camera_movement"] = "Static"
                if "description" not in shot:
                    shot["description"] = "Shot description"
                if "scene" not in shot:
                    shot["scene"] = f"Scene {i + 1}"
                if "duration" not in shot:
                    shot["duration"] = "3-5 seconds"
                if "equipment" not in shot:
                    shot["equipment"] = ["Camera", "Tripod"]
                if "lens" not in shot:
                    shot["lens"] = "50mm"
                if "notes" not in shot:
                    shot["notes"] = ""
            
            # Validation: Ensure we have at least as many shots as storyboard frames
            if len(shot_list) < len(storyboard):
                print(f"  Warning: Generated {len(shot_list)} shots but have {len(storyboard)} storyboard frames")
                print(f" Creating additional shots to match storyboard frames...")
                
                # Create additional shots for missing frames
                for i in range(len(shot_list), len(storyboard)):
                    frame = storyboard[i]
                    additional_shot = {
                        "shot_number": i + 1,
                        "scene": frame.get("scene", f"Scene {i + 1}"),
                        "shot_type": frame.get("camera_angle", "Medium Shot"),
                        "camera_movement": "Static",
                        "description": frame.get("description", "Shot description"),
                        "duration": "3-5 seconds",
                        "equipment": ["Camera", "Tripod"],
                        "lens": "50mm",
                        "notes": "Auto-generated to match storyboard"
                    }
                    shot_list.append(additional_shot)
            
            print(f" Shot list generated successfully ({len(shot_list)} shots for {len(storyboard)} frames)")
            return shot_list
            
        except Exception as e:
            print(f" Shot list generation failed: {str(e)}")
            
            # Fallback: Create basic shot list from storyboard frames (ALL frames, not limited)
            fallback_shot_list = []
            for i, frame in enumerate(storyboard):  # Process ALL frames
                shot = {
                    "shot_number": i + 1,
                    "scene": frame.get("scene", f"Scene {i + 1}"),
                    "shot_type": frame.get("camera_angle", "Medium Shot"),
                    "camera_movement": "Static",
                    "description": frame.get("description", "Shot description"),
                    "duration": "3-5 seconds",
                    "equipment": ["Camera", "Tripod"],
                    "lens": "50mm",
                    "notes": f"Auto-generated due to error"
                }
                fallback_shot_list.append(shot)
            
            print(f" Fallback shot list created ({len(fallback_shot_list)} shots for {len(storyboard)} frames)")
            
            return fallback_shot_list if fallback_shot_list else [
                {
                    "shot_number": 1,
                    "scene": "Scene 1",
                    "shot_type": "Medium Shot",
                    "camera_movement": "Static",
                    "description": "Fallback shot",
                    "duration": "5 seconds",
                    "equipment": ["Camera", "Tripod"],
                    "lens": "50mm",
                    "notes": "Fallback shot list generated due to error"
                }
            ]
    
    async def validate_output(self, shot_list: List[Dict[str, Any]]) -> bool:
        """
        Validate the generated shot list.
        
        Args:
            shot_list: Generated shot list
            
        Returns:
            True if valid, False otherwise
        """
        if not shot_list or len(shot_list) == 0:
            return False
        
        # Check that each shot has required fields
        required_fields = ["shot_number", "shot_type", "description"]
        for shot in shot_list:
            if not all(field in shot for field in required_fields):
                return False
        
        return True



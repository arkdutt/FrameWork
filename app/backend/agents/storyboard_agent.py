"""
Storyboard Agent - Generates storyboards from scripts.

Uses Google Gemini to create detailed visual scene breakdowns.
Uses Pollinations.AI for FREE image generation (no API key needed).
"""
from typing import Dict, Any, List
import google.generativeai as genai
import json
from ..config.settings import settings
from ..utils.image_generation import PollinationsAI


class StoryboardAgent:
    """
    Agent responsible for generating storyboards.
    
    Uses Gemini AI to parse scripts and create detailed visual
    descriptions for each key frame/scene in the film.
    Uses Pollinations.AI for free image generation.
    """
    
    def __init__(self):
        """Initialize the storyboard agent with Gemini API."""
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
        self.image_generator = PollinationsAI()
    
    async def run(self, project: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Generate a storyboard based on the project script.
        
        Args:
            project: Project document containing script and other data
            
        Returns:
            List of storyboard frames, each containing:
            - frame_number: int
            - scene: str
            - description: str
            - camera_angle: str
            - dialogue: str (optional)
            - notes: str (optional)
        """
        script = project.get("script", "")
        
        if not script:
            raise ValueError("Script is required to generate storyboard")
        
        # Check if storyboard already exists
        if project.get("storyboard"):
            print(" Storyboard already exists, skipping generation")
            return project.get("storyboard")
        
        system_prompt = """You are an expert storyboard artist and cinematographer. Analyze the provided screenplay and create a detailed storyboard.

TASK: Break down the script into key visual frames/shots and provide detailed descriptions for each.

For EACH key frame, provide:
1. frame_number: Sequential number (1, 2, 3, etc.)
2. scene: Scene identifier (e.g., "Scene 1", "Opening", "INT. HOUSE")
3. description: Detailed visual description of what's happening in the frame (composition, lighting, mood, character positions, key visual elements)
4. camera_angle: Camera angle/shot type (e.g., "Wide Shot", "Medium Close-Up", "Over-the-Shoulder", "Bird's Eye View", "Low Angle")
5. dialogue: Any dialogue spoken during this frame (optional)
6. notes: Additional notes for the cinematographer or artist (optional)

GUIDELINES:
- Identify 8-15 key frames that tell the story visually
- Focus on important story beats and transitions
- Include establishing shots, key character moments, and dramatic beats
- Be specific about visual composition
- Consider lighting, mood, and atmosphere
- Think cinematically

Return your response as a JSON array of frames. ONLY return valid JSON, no additional text.

Example format:
[
  {
    "frame_number": 1,
    "scene": "Opening",
    "description": "Wide shot of a bustling city street at sunset. Golden hour lighting bathes the buildings. People walking, cars passing. Camera is positioned at street level.",
    "camera_angle": "Wide Shot",
    "dialogue": "",
    "notes": "Establish the urban setting and time of day"
  },
  {
    "frame_number": 2,
    "scene": "INT. COFFEE SHOP",
    "description": "Medium shot of the protagonist sitting alone at a corner table, staring out the window. Soft diffused light from window. Coffee cup in foreground, slightly out of focus.",
    "camera_angle": "Medium Shot",
    "dialogue": "Is anyone sitting here?",
    "notes": "Shallow depth of field, focus on protagonist's contemplative expression"
  }
]

Now analyze this screenplay and generate the storyboard:

SCREENPLAY:
"""

        try:
            print(f" Generating storyboard from script ({len(script)} characters)...")
            
            response = self.model.generate_content(
                system_prompt + script,
                generation_config={
                    "temperature": 0.7,
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
            
            # Parse JSON
            storyboard = json.loads(result_text)
            
            # Validate structure
            if not isinstance(storyboard, list):
                raise ValueError("Storyboard must be a list")
            
            # Ensure all frames have required fields AND generate images
            for i, frame in enumerate(storyboard):
                if "frame_number" not in frame:
                    frame["frame_number"] = i + 1
                if "description" not in frame:
                    frame["description"] = "Visual frame description"
                if "camera_angle" not in frame:
                    frame["camera_angle"] = "Medium Shot"
                if "scene" not in frame:
                    frame["scene"] = f"Scene {i + 1}"
                if "dialogue" not in frame:
                    frame["dialogue"] = ""
                if "notes" not in frame:
                    frame["notes"] = ""
                
                # Generate image URL for this frame using PollinationsAI
                print(f"  Generating image for frame {i + 1}...")
                frame["image_url"] = self.image_generator.generate_cinematic_frame(
                    description=frame["description"],
                    camera_angle=frame.get("camera_angle"),
                    lighting=frame.get("lighting"),
                    mood=frame.get("mood")
                )
            
            print(f" Storyboard generated successfully ({len(storyboard)} frames with images)")
            return storyboard
            
        except Exception as e:
            print(f" Storyboard generation failed: {str(e)}")
            
            # Fallback: Create basic storyboard structure with images
            fallback_storyboard = [
                {
                    "frame_number": 1,
                    "scene": "Opening",
                    "description": "Opening shot establishing the setting based on the script.",
                    "camera_angle": "Wide Shot",
                    "dialogue": "",
                    "image_url": self.image_generator.generate_cinematic_frame(
                        "Opening shot establishing the setting", camera_angle="Wide Shot"
                    ),
                    "notes": f"Error during generation: {str(e)}"
                },
                {
                    "frame_number": 2,
                    "scene": "Main Action",
                    "description": "Key character moment or main action from the script.",
                    "camera_angle": "Medium Shot",
                    "dialogue": "",
                    "image_url": self.image_generator.generate_cinematic_frame(
                        "Key character moment", camera_angle="Medium Shot"
                    ),
                    "notes": "Fallback storyboard generated"
                },
                {
                    "frame_number": 3,
                    "scene": "Closing",
                    "description": "Final shot concluding the sequence.",
                    "camera_angle": "Close-Up",
                    "dialogue": "",
                    "image_url": self.image_generator.generate_cinematic_frame(
                        "Final shot concluding the sequence", camera_angle="Close-Up"
                    ),
                    "notes": "Fallback storyboard generated"
                }
            ]
            return fallback_storyboard
    
    async def validate_output(self, storyboard: List[Dict[str, Any]]) -> bool:
        """
        Validate the generated storyboard.
        
        Args:
            storyboard: Generated storyboard
            
        Returns:
            True if valid, False otherwise
        """
        if not storyboard or len(storyboard) == 0:
            return False
        
        # Check that each frame has required fields
        required_fields = ["frame_number", "description"]
        for frame in storyboard:
            if not all(field in frame for field in required_fields):
                return False
        
        return True



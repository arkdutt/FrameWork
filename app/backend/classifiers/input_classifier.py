"""
Input Classifier - Determines what needs to be generated.

Uses Google Gemini to analyze user prompts and classify content needs.
"""
import google.generativeai as genai
import json
from ..config.settings import settings
from ..models.schemas import Classification


class InputClassifier:
    """
    Classifier that analyzes user input to determine required outputs.
    
    Uses Gemini AI to intelligently parse user prompts and understand
    what content the user already has vs. what needs to be generated.
    """
    
    def __init__(self):
        """Initialize the classifier with Gemini API."""
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
    
    async def classify_user_input(self, prompt: str) -> Classification:
        """
        Classify user input to determine what user ALREADY HAS.
        
        INVERSE LOGIC DESIGN:
        - True = User already has this content
        - False = User doesn't have this (system will generate it)
        
        Args:
            prompt: User's input prompt
            
        Returns:
            Classification object indicating what user ALREADY HAS
        
        Examples:
        - "Write a script about robots" 
          → {script: False, storyboard: False, shot_list: False}
          (User has nothing, system generates everything)
          
        - "Here's my script: [text]. Create storyboard" 
          → {script: True, storyboard: False, shot_list: False}
          (User has script, system generates storyboard)
          
        - "I have a script and storyboard. Generate shot list"
          → {script: True, storyboard: True, shot_list: False}
          (User has script+storyboard, system generates shot list only)
        """
        
        system_prompt = """You are an expert content classifier for a filmmaker pre-production system.

Your task is to analyze the user's prompt and determine what content they ALREADY HAVE vs what they want GENERATED.

CRITICAL - INVERSE LOGIC:
- Return TRUE if the user ALREADY PROVIDED that content (it exists in their prompt)
- Return FALSE if the user NEEDS the system to generate it

Content types to detect:
1. **script**: A complete screenplay/script in proper format (FADE IN, scene headings, dialogue, etc.)
   - TRUE if: User has included an actual script with screenplay formatting
   - FALSE if: User is requesting script generation or just describing a story idea

2. **storyboard**: Visual scene breakdowns with frame descriptions
   - TRUE if: User has provided storyboard frames or visual descriptions
   - FALSE if: User wants storyboard generated

3. **shot_list**: Technical breakdown with camera specs and shot details
   - TRUE if: User has provided a shot list
   - FALSE if: User wants shot list generated

DETECTION RULES:
- Look for explicit phrases: "here's my script", "I have a script", "my script:", "script:"
- Look for screenplay formatting: "FADE IN:", "INT.", "EXT.", "FADE OUT", scene headings
- If prompt contains >200 characters with screenplay formatting → script = TRUE
- If prompt is just a story idea/description → script = FALSE
- Default to FALSE if uncertain

Examples:
 "Write a script about robots" → {"script": false, "storyboard": false, "shot_list": false}
 "Create a rom-com about two people" → {"script": false, "storyboard": false, "shot_list": false}
 "Here's my script: FADE IN: INT. HOUSE..." → {"script": true, "storyboard": false, "shot_list": false}
 "FADE IN: EXT. CITY - DAY... Generate storyboard" → {"script": true, "storyboard": false, "shot_list": false}

Respond ONLY with valid JSON:
{
  "script": true/false,
  "storyboard": true/false,
  "shot_list": true/false
}

User prompt to classify:
"""

        try:
            # Call Gemini API
            response = self.model.generate_content(
                system_prompt + prompt,
                generation_config={
                    "temperature": 0.1,
                    "top_p": 0.95,
                    "top_k": 20,
                    "max_output_tokens": 200,
                }
            )
            
            # Check if response was blocked
            if not response.candidates or not response.candidates[0].content.parts:
                finish_reason = response.candidates[0].finish_reason if response.candidates else "UNKNOWN"
                print(f"  Classification blocked by safety filters (finish_reason: {finish_reason}), using fallback")
                raise ValueError(f"Content blocked: {finish_reason}")
            
            # Parse JSON response
            result_text = response.text.strip()
            
            # Clean up response (remove markdown code blocks if present)
            if "```json" in result_text:
                result_text = result_text.split("```json")[1].split("```")[0].strip()
            elif "```" in result_text:
                result_text = result_text.split("```")[1].split("```")[0].strip()
            
            # Parse JSON
            result_json = json.loads(result_text)
            
            # Create classification object
            classification = Classification(
                script=result_json.get("script", False),
                storyboard=result_json.get("storyboard", False),
                shot_list=result_json.get("shot_list", False)
            )
            
            print(f" Classification result: {classification}")
            return classification
            
        except Exception as e:
            print(f"  Classification failed, using fallback: {str(e)}")
            
            # Fallback: Simple keyword matching with better detection
            prompt_lower = prompt.lower()
            
            # Check if user has provided a script (look for screenplay markers)
            has_script_indicators = [
                "here's my script", "here is my script", "i have a script", "my script:", 
                "existing script", "attached script", "script i wrote", "script:",
                "fade in:", "int.", "ext.", "fade out"  # Screenplay formatting markers
            ]
            
            # Also check if prompt contains actual script content (more than 200 chars with screenplay markers)
            has_script = any(phrase in prompt_lower for phrase in has_script_indicators)
            if not has_script and len(prompt) > 200:
                # Check for screenplay formatting indicators
                screenplay_markers = ["fade in", "int.", "ext.", "fade out", "cut to:", "dissolve to:"]
                marker_count = sum(1 for marker in screenplay_markers if marker in prompt_lower)
                if marker_count >= 2:
                    has_script = True
                    print(" Detected screenplay format in prompt - user has script")
            
            has_storyboard = any(phrase in prompt_lower for phrase in [
                "i have a storyboard", "i have storyboard", "existing storyboard", 
                "my storyboard", "attached storyboard", "here's my storyboard"
            ])
            
            has_shot_list = any(phrase in prompt_lower for phrase in [
                "i have a shot list", "i have shot list", "existing shot list", 
                "my shot list", "attached shot list", "here's my shot list"
            ])
            
            classification = Classification(
                script=has_script,
                storyboard=has_storyboard,
                shot_list=has_shot_list
            )
            
            print(f" Fallback classification: {classification}")
            return classification
    
    def extract_user_script(self, prompt: str) -> str | None:
        """
        Extract user-provided script from the prompt.
        
        Args:
            prompt: User's input prompt
            
        Returns:
            Extracted script text or None if no script found
        """
        prompt_lower = prompt.lower()
        
        # Look for script separators
        script_indicators = [
            "here's my script:",
            "here is my script:",
            "my script:",
            "script:",
            "here's the script:",
        ]
        
        # Try to find script content after indicators
        for indicator in script_indicators:
            if indicator in prompt_lower:
                # Find the position and extract everything after
                idx = prompt_lower.index(indicator)
                script_start = idx + len(indicator)
                script = prompt[script_start:].strip()
                
                # Remove any trailing instructions
                # (e.g., "...FADE OUT. Now create a storyboard")
                trailing_phrases = [
                    "\n\nnow create",
                    "\n\ngenerate a",
                    "\n\ncreate a",
                    "\n\ngenerate the",
                    "\n\nmake a",
                ]
                for phrase in trailing_phrases:
                    if phrase in script.lower():
                        cut_idx = script.lower().index(phrase)
                        script = script[:cut_idx].strip()
                        break
                
                if len(script) > 50:  # Must be substantial
                    print(f" Extracted user-provided script ({len(script)} characters)")
                    return script
        
        # Check if entire prompt looks like a screenplay
        screenplay_markers = ["fade in", "int.", "ext.", "fade out"]
        marker_count = sum(1 for marker in screenplay_markers if marker in prompt_lower)
        
        if marker_count >= 2 and len(prompt) > 200:
            # The whole prompt appears to be a script
            print(f" Entire prompt appears to be a script ({len(prompt)} characters)")
            return prompt.strip()
        
        return None
    
    async def extract_metadata(self, prompt: str) -> dict:
        """
        Extract additional metadata from the prompt.
        
        Args:
            prompt: User's input prompt
            
        Returns:
            Dictionary of extracted metadata (genre, tone, duration, etc.)
        """
        system_prompt = """Extract metadata from this film project prompt. Return ONLY a JSON object with:
{
  "genre": "string or null",
  "tone": "string or null", 
  "duration": "string or null"
}

User prompt:
"""
        
        try:
            response = self.model.generate_content(
                system_prompt + prompt,
                generation_config={"temperature": 0.2, "max_output_tokens": 150}
            )
            
            result_text = response.text.strip()
            if "```json" in result_text:
                result_text = result_text.split("```json")[1].split("```")[0].strip()
            elif "```" in result_text:
                result_text = result_text.split("```")[1].split("```")[0].strip()
            
            return json.loads(result_text)
            
        except Exception as e:
            print(f"  Metadata extraction failed: {str(e)}")
            return {"genre": None, "tone": None, "duration": None}



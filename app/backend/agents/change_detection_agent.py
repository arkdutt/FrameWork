"""
Change Detection Agent - Analyzes script changes and determines impact.

Uses Google Gemini to evaluate whether script edits are significant enough
to warrant regeneration of storyboard and shot list.
"""
from typing import Dict, Any, Optional
import google.generativeai as genai
from ..config.settings import settings
import difflib
import json


class ChangeDetectionAgent:
    """
    Agent responsible for analyzing script changes.
    
    Determines whether edits are significant enough to trigger
    regeneration of downstream artifacts (storyboard, shot list).
    """
    
    def __init__(self):
        """Initialize the change detection agent with Gemini API."""
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
    
    def calculate_diff(self, old_script: str, new_script: str) -> Dict[str, Any]:
        """
        Calculate the difference between two scripts.
        
        Args:
            old_script: Original script
            new_script: Edited script
            
        Returns:
            Dictionary with diff statistics
        """
        old_lines = old_script.splitlines()
        new_lines = new_script.splitlines()
        
        differ = difflib.Differ()
        diff = list(differ.compare(old_lines, new_lines))
        
        added_lines = [line[2:] for line in diff if line.startswith('+ ')]
        removed_lines = [line[2:] for line in diff if line.startswith('- ')]
        
        # Calculate percentage change
        total_lines = max(len(old_lines), len(new_lines))
        changed_lines = len(added_lines) + len(removed_lines)
        change_percentage = (changed_lines / total_lines * 100) if total_lines > 0 else 0
        
        return {
            "added_lines": added_lines,
            "removed_lines": removed_lines,
            "total_changes": changed_lines,
            "change_percentage": round(change_percentage, 2),
            "old_length": len(old_lines),
            "new_length": len(new_lines)
        }
    
    async def analyze_changes(
        self, 
        old_script: str, 
        new_script: str
    ) -> Dict[str, Any]:
        """
        Analyze script changes and determine if regeneration is needed.
        
        Args:
            old_script: Original script
            new_script: Edited script
            
        Returns:
            Dictionary with analysis results:
            {
                "should_regenerate": bool,
                "regenerate_storyboard": bool,
                "regenerate_shot_list": bool,
                "reason": str,
                "change_summary": str,
                "change_percentage": float
            }
        """
        # Calculate diff
        diff_info = self.calculate_diff(old_script, new_script)
        
        print(f" Script change analysis:")
        print(f"   - Lines added: {len(diff_info['added_lines'])}")
        print(f"   - Lines removed: {len(diff_info['removed_lines'])}")
        print(f"   - Change percentage: {diff_info['change_percentage']}%")
        
        # Quick check: if change is very small (<3%), skip regeneration
        if diff_info['change_percentage'] < 3:
            print(" Changes are minimal (<3%), skipping regeneration")
            return {
                "should_regenerate": False,
                "regenerate_storyboard": False,
                "regenerate_shot_list": False,
                "reason": "Changes are too minor (< 3% of script modified)",
                "change_summary": "Minimal edits detected",
                "change_percentage": diff_info['change_percentage']
            }
        
        # Use LLM to analyze semantic significance of changes
        system_prompt = """You are an expert film production assistant analyzing script changes.

Your task is to evaluate whether changes to a screenplay are SIGNIFICANT enough to warrant regenerating the storyboard and shot list.

SIGNIFICANT CHANGES (should regenerate):
- New scenes added
- Existing scenes removed
- Major dialogue changes that affect visual storytelling
- New characters introduced
- Location changes
- Time of day changes
- Action sequence modifications
- Plot-critical edits

INSIGNIFICANT CHANGES (no regeneration needed):
- Minor typo fixes
- Small dialogue tweaks that don't change meaning
- Formatting adjustments
- Punctuation changes
- Minor word substitutions
- Small additions/deletions that don't affect visuals

Analyze the changes and respond ONLY with a JSON object:
{
  "should_regenerate": true/false,
  "regenerate_storyboard": true/false,
  "regenerate_shot_list": true/false,
  "reason": "Brief explanation of why regeneration is/isn't needed",
  "change_summary": "Summary of what changed"
}

ORIGINAL SCRIPT:
---
{old_script}
---

EDITED SCRIPT:
---
{new_script}
---

CHANGES DETECTED:
{diff_summary}

Analyze these changes and respond with JSON only:"""

        # Create diff summary for context
        diff_summary = f"""
Added content ({len(diff_info['added_lines'])} lines):
{chr(10).join(diff_info['added_lines'][:10])}  # Show first 10 lines
{'...' if len(diff_info['added_lines']) > 10 else ''}

Removed content ({len(diff_info['removed_lines'])} lines):
{chr(10).join(diff_info['removed_lines'][:10])}  # Show first 10 lines
{'...' if len(diff_info['removed_lines']) > 10 else ''}

Overall: {diff_info['change_percentage']}% of script modified
"""

        try:
            # Truncate scripts if too long (keep Gemini context manageable)
            old_script_truncated = old_script[:4000] if len(old_script) > 4000 else old_script
            new_script_truncated = new_script[:4000] if len(new_script) > 4000 else new_script
            
            prompt = system_prompt.format(
                old_script=old_script_truncated,
                new_script=new_script_truncated,
                diff_summary=diff_summary
            )
            
            print(f" Asking Gemini to analyze script changes...")
            
            response = self.model.generate_content(
                prompt,
                generation_config={
                    "temperature": 0.3,  # Lower temperature for more consistent analysis
                    "top_p": 0.8,
                    "max_output_tokens": 1000,
                },
                response_mime_type="application/json"
            )
            
            # Check if response was blocked
            if not response.candidates or not response.candidates[0].content.parts:
                print("  Gemini response blocked, using fallback logic")
                return self._fallback_analysis(diff_info)
            
            result_text = response.text.strip()
            
            # Parse JSON response
            analysis = json.loads(result_text)
            
            # Add change percentage to result
            analysis['change_percentage'] = diff_info['change_percentage']
            
            print(f" Analysis complete: {analysis['reason']}")
            print(f"   - Regenerate: {analysis['should_regenerate']}")
            
            return analysis
            
        except Exception as e:
            print(f" Change analysis failed: {str(e)}")
            return self._fallback_analysis(diff_info)
    
    def _fallback_analysis(self, diff_info: Dict[str, Any]) -> Dict[str, Any]:
        """
        Fallback analysis based on heuristics if LLM fails.
        
        Args:
            diff_info: Diff information
            
        Returns:
            Analysis result
        """
        # Heuristic: if change is >15%, likely significant
        should_regenerate = diff_info['change_percentage'] > 15
        
        # Check for scene-level changes
        added_text = ' '.join(diff_info['added_lines']).upper()
        removed_text = ' '.join(diff_info['removed_lines']).upper()
        
        has_scene_changes = any(keyword in added_text or keyword in removed_text 
                               for keyword in ['INT.', 'EXT.', 'FADE IN', 'FADE OUT', 'CUT TO'])
        
        if has_scene_changes:
            should_regenerate = True
            reason = "Scene-level changes detected (INT/EXT headers, scene transitions)"
        elif diff_info['change_percentage'] > 15:
            reason = f"Substantial changes ({diff_info['change_percentage']}% of script modified)"
        else:
            reason = f"Minor changes ({diff_info['change_percentage']}% of script modified)"
        
        return {
            "should_regenerate": should_regenerate,
            "regenerate_storyboard": should_regenerate,
            "regenerate_shot_list": should_regenerate,
            "reason": reason,
            "change_summary": f"Fallback analysis: {diff_info['total_changes']} lines changed",
            "change_percentage": diff_info['change_percentage']
        }


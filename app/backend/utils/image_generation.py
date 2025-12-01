"""
Image Generation using Pollinations.AI

FREE text-to-image generation with no API key required.
Uses Pollinations.AI's Stable Diffusion API.
"""
import urllib.parse
from typing import Optional


class PollinationsAI:
    """
    Free text-to-image generation using Pollinations.AI.
    
    Features:
    - No API key required
    - Unlimited usage
    - Stable Diffusion powered
    - Multiple styles supported
    """
    
    BASE_URL = "https://image.pollinations.ai/prompt"
    
    @staticmethod
    def generate_image_url(
        prompt: str,
        width: int = 1024,
        height: int = 576,
        style: str = "cinematic",
        enhance: bool = True,
        nologo: bool = True
    ) -> str:
        """
        Generate an image URL from a text prompt.
        
        Args:
            prompt: Text description of the image
            width: Image width in pixels (default: 1024)
            height: Image height in pixels (default: 576, cinematic aspect ratio)
            style: Art style to apply (default: "cinematic")
            enhance: Enhance prompt with style keywords (default: True)
            nologo: Remove Pollinations.AI logo (default: True)
            
        Returns:
            Image URL that can be used directly in <img> tags
            
        Example:
            >>> url = PollinationsAI.generate_image_url("A robot painting")
            >>> print(url)
            https://image.pollinations.ai/prompt/A%20robot%20painting...
        """
        # Enhance prompt if requested
        if enhance:
            enhanced_prompt = f"{prompt}, {style} style, high quality, professional"
        else:
            enhanced_prompt = prompt
        
        # URL encode the prompt
        encoded_prompt = urllib.parse.quote(enhanced_prompt)
        
        # Build URL with parameters
        params = []
        params.append(f"width={width}")
        params.append(f"height={height}")
        if nologo:
            params.append("nologo=true")
        
        params_string = "&".join(params)
        
        image_url = f"{PollinationsAI.BASE_URL}/{encoded_prompt}?{params_string}"
        
        return image_url
    
    @staticmethod
    def generate_cinematic_frame(
        description: str,
        camera_angle: Optional[str] = None,
        lighting: Optional[str] = None,
        mood: Optional[str] = None
    ) -> str:
        """
        Generate a cinematic storyboard frame.
        
        Optimized for film/video production with cinematic styling.
        
        Args:
            description: Scene description
            camera_angle: Camera angle (e.g., "wide shot", "close-up")
            lighting: Lighting description (e.g., "golden hour", "dramatic")
            mood: Mood/atmosphere (e.g., "tense", "peaceful")
            
        Returns:
            Image URL for the cinematic frame
            
        Example:
            >>> url = PollinationsAI.generate_cinematic_frame(
            ...     "Robot in art studio",
            ...     camera_angle="wide shot",
            ...     lighting="soft natural light",
            ...     mood="melancholic"
            ... )
        """
        # Build enhanced prompt
        prompt_parts = [description]
        
        if camera_angle:
            prompt_parts.append(f"{camera_angle}")
        
        if lighting:
            prompt_parts.append(f"{lighting}")
        
        if mood:
            prompt_parts.append(f"{mood} atmosphere")
        
        # Add cinematic keywords
        prompt_parts.extend([
            "cinematic",
            "film still",
            "professional cinematography",
            "detailed",
            "high quality"
        ])
        
        full_prompt = ", ".join(prompt_parts)
        
        # Generate with 16:9 cinematic aspect ratio
        return PollinationsAI.generate_image_url(
            full_prompt,
            width=1024,
            height=576,
            enhance=False  # Already enhanced
        )
    
    @staticmethod
    def generate_storyboard_frames(frames: list) -> list:
        """
        Generate images for multiple storyboard frames.
        
        Args:
            frames: List of frame dictionaries with 'description' and optional 'camera_angle'
            
        Returns:
            List of frames with 'image_url' added
            
        Example:
            >>> frames = [
            ...     {"description": "Opening shot", "camera_angle": "wide shot"},
            ...     {"description": "Character close-up", "camera_angle": "close-up"}
            ... ]
            >>> frames_with_images = PollinationsAI.generate_storyboard_frames(frames)
        """
        for frame in frames:
            description = frame.get("description", "")
            camera_angle = frame.get("camera_angle")
            lighting = frame.get("lighting")
            mood = frame.get("mood")
            
            frame["image_url"] = PollinationsAI.generate_cinematic_frame(
                description=description,
                camera_angle=camera_angle,
                lighting=lighting,
                mood=mood
            )
        
        return frames


# Convenience functions for common use cases

def text_to_image(prompt: str, **kwargs) -> str:
    """
    Simple text-to-image generation.
    
    Args:
        prompt: Text description
        **kwargs: Additional parameters for generate_image_url()
        
    Returns:
        Image URL
    """
    return PollinationsAI.generate_image_url(prompt, **kwargs)


def cinematic_image(description: str, camera_angle: str = None) -> str:
    """
    Generate a cinematic image.
    
    Args:
        description: Scene description
        camera_angle: Optional camera angle
        
    Returns:
        Image URL
    """
    return PollinationsAI.generate_cinematic_frame(description, camera_angle)


# Example usage
if __name__ == "__main__":
    # Simple usage
    url1 = text_to_image("A robot learning to paint")
    print(f"Simple image: {url1}")
    
    # Cinematic usage
    url2 = cinematic_image(
        "Abandoned art studio with dusty light streaming through windows",
        camera_angle="wide shot"
    )
    print(f"Cinematic image: {url2}")
    
    # Storyboard frames
    frames = [
        {
            "description": "Robot enters abandoned studio",
            "camera_angle": "Wide Shot",
            "lighting": "dramatic shadows",
            "mood": "mysterious"
        },
        {
            "description": "Close-up of robot's optical sensors scanning old paintings",
            "camera_angle": "Extreme Close-Up",
            "lighting": "soft ambient",
            "mood": "curious"
        }
    ]
    
    frames_with_images = PollinationsAI.generate_storyboard_frames(frames)
    for frame in frames_with_images:
        print(f"Frame {frame.get('description', '')[:30]}...")
        print(f"  URL: {frame['image_url']}")



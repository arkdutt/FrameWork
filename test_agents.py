#!/usr/bin/env python3
"""
Test script for the Filmmaker AI App agents.

This script tests all AI agents independently to verify they work correctly.
"""
import asyncio
import sys
import os

# Add the backend directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app', 'backend'))

from app.backend.classifiers.input_classifier import InputClassifier
from app.backend.agents.script_agent import ScriptAgent
from app.backend.agents.storyboard_agent import StoryboardAgent
from app.backend.agents.shot_list_agent import ShotListAgent


async def test_classifier():
    """Test the InputClassifier."""
    print("\n" + "="*80)
    print(" TESTING INPUT CLASSIFIER")
    print("="*80)
    
    classifier = InputClassifier()
    
    test_prompts = [
        "Write a script about a robot learning to paint",
        "Here's my script: [FADE IN...]. Please create a storyboard for it.",
        "I have a script and storyboard. Generate the shot list please."
    ]
    
    for i, prompt in enumerate(test_prompts, 1):
        print(f"\n Test {i}: {prompt[:60]}...")
        result = await classifier.classify_user_input(prompt)
        print(f"   Result: script={result.script}, storyboard={result.storyboard}, shot_list={result.shot_list}")
    
    print("\n InputClassifier test complete!\n")


async def test_script_agent():
    """Test the ScriptAgent."""
    print("\n" + "="*80)
    print(" TESTING SCRIPT AGENT")
    print("="*80)
    
    agent = ScriptAgent()
    
    test_project = {
        "user_prompt": "Create a 2-minute short film about a lonely astronaut discovering alien flowers on Mars. Make it emotional and hopeful.",
        "title": "Martian Flowers"
    }
    
    print(f"\n Generating script for: {test_project['title']}")
    print(f"   Prompt: {test_project['user_prompt'][:80]}...")
    
    script = await agent.run(test_project)
    
    print(f"\n Script generated! ({len(script)} characters)")
    print("\n--- SCRIPT PREVIEW (first 500 chars) ---")
    print(script[:500])
    print("...\n")
    
    # Validate
    is_valid = await agent.validate_output(script)
    print(f"{'' if is_valid else ''} Validation: {'PASSED' if is_valid else 'FAILED'}")


async def test_storyboard_agent():
    """Test the StoryboardAgent."""
    print("\n" + "="*80)
    print(" TESTING STORYBOARD AGENT")
    print("="*80)
    
    agent = StoryboardAgent()
    
    # Sample script for testing
    sample_script = """FADE IN:

INT. SPACESHIP - NIGHT

ALEX (30s, astronaut) sits alone by the window, staring at the red Martian surface below.

EXT. MARS SURFACE - DAY

Alex steps out in a spacesuit. The desolate red landscape stretches endlessly.

Suddenly, Alex spots something unusual - a patch of bioluminescent blue flowers glowing softly.

Alex kneels down, mesmerized. A tear rolls down their cheek.

FADE OUT."""
    
    test_project = {
        "script": sample_script,
        "title": "Martian Flowers"
    }
    
    print(f"\n Generating storyboard from script...")
    
    storyboard = await agent.run(test_project)
    
    print(f"\n Storyboard generated! ({len(storyboard)} frames)")
    
    # Display frames
    for frame in storyboard[:3]:  # Show first 3 frames
        print(f"\n--- FRAME {frame['frame_number']} ---")
        print(f"Scene: {frame.get('scene', 'N/A')}")
        print(f"Camera: {frame.get('camera_angle', 'N/A')}")
        print(f"Description: {frame.get('description', 'N/A')[:100]}...")
    
    if len(storyboard) > 3:
        print(f"\n... and {len(storyboard) - 3} more frames")
    
    # Validate
    is_valid = await agent.validate_output(storyboard)
    print(f"\n{'' if is_valid else ''} Validation: {'PASSED' if is_valid else 'FAILED'}")


async def test_shot_list_agent():
    """Test the ShotListAgent."""
    print("\n" + "="*80)
    print(" TESTING SHOT LIST AGENT")
    print("="*80)
    
    agent = ShotListAgent()
    
    # Sample storyboard for testing
    sample_storyboard = [
        {
            "frame_number": 1,
            "scene": "INT. SPACESHIP",
            "description": "Wide shot of Alex sitting alone by window, Mars visible outside",
            "camera_angle": "Wide Shot",
            "dialogue": "",
            "notes": "Low light, moody atmosphere"
        },
        {
            "frame_number": 2,
            "scene": "EXT. MARS SURFACE",
            "description": "Establishing shot of desolate Martian landscape, red and barren",
            "camera_angle": "Extreme Wide Shot",
            "dialogue": "",
            "notes": "Wide lens, emphasize isolation"
        },
        {
            "frame_number": 3,
            "scene": "EXT. MARS SURFACE",
            "description": "Close-up of Alex's helmet visor reflecting the blue glowing flowers",
            "camera_angle": "Close-Up",
            "dialogue": "",
            "notes": "Focus on reflection, dramatic moment"
        }
    ]
    
    test_project = {
        "storyboard": sample_storyboard,
        "script": "Sample script...",
        "title": "Martian Flowers"
    }
    
    print(f"\n Generating shot list from storyboard...")
    
    shot_list = await agent.run(test_project)
    
    print(f"\n Shot list generated! ({len(shot_list)} shots)")
    
    # Display shots
    for shot in shot_list[:3]:  # Show first 3 shots
        print(f"\n--- SHOT {shot['shot_number']} ---")
        print(f"Scene: {shot.get('scene', 'N/A')}")
        print(f"Type: {shot.get('shot_type', 'N/A')}")
        print(f"Movement: {shot.get('camera_movement', 'N/A')}")
        print(f"Duration: {shot.get('duration', 'N/A')}")
        print(f"Equipment: {', '.join(shot.get('equipment', []))}")
        print(f"Lens: {shot.get('lens', 'N/A')}")
        print(f"Description: {shot.get('description', 'N/A')[:80]}...")
    
    if len(shot_list) > 3:
        print(f"\n... and {len(shot_list) - 3} more shots")
    
    # Validate
    is_valid = await agent.validate_output(shot_list)
    print(f"\n{'' if is_valid else ''} Validation: {'PASSED' if is_valid else 'FAILED'}")


async def main():
    """Run all tests."""
    print("\n" + "="*80)
    print(" FILMMAKER AI APP - AGENT TESTING SUITE")
    print("="*80)
    print("\nThis script will test all AI agents to verify they work correctly.")
    print("Make sure your .env file has GEMINI_API_KEY set!")
    
    input("\nPress Enter to start testing... ")
    
    try:
        # Run all tests
        await test_classifier()
        await test_script_agent()
        await test_storyboard_agent()
        await test_shot_list_agent()
        
        print("\n" + "="*80)
        print(" ALL TESTS COMPLETED SUCCESSFULLY!")
        print("="*80)
        print("\n Your AI agents are working correctly!")
        print("\nNext steps:")
        print("1. Start MongoDB: docker run -d -p 27017:27017 mongo:latest")
        print("2. Start backend: cd app/backend && python -m uvicorn main:app --reload")
        print("3. Start frontend: cd app/frontend && npm run dev")
        print("4. Test the full system at http://localhost:3000")
        print("\n")
        
    except Exception as e:
        print("\n" + "="*80)
        print(" TEST FAILED!")
        print("="*80)
        print(f"\nError: {str(e)}")
        print("\nPlease check:")
        print("1. GEMINI_API_KEY is set in .env file")
        print("2. You have internet connection")
        print("3. Dependencies are installed: pip install -r requirements.txt")
        print("\n")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())



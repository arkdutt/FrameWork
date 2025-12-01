#!/usr/bin/env python3
"""
Check if Gemini API key is configured correctly.
"""
import os
import sys
from pathlib import Path

# Add backend to path
backend_path = Path(__file__).parent / 'app' / 'backend'
sys.path.insert(0, str(backend_path))

def check_env_file():
    """Check if .env file exists and has the API key."""
    env_path = Path(__file__).parent / '.env'
    
    print(" Checking configuration...")
    print(f"Looking for .env file at: {env_path}")
    
    if not env_path.exists():
        print(" .env file not found!")
        print("\nPlease create a .env file in the project root with:")
        print("GEMINI_API_KEY=your_actual_api_key_here")
        return False
    
    print(" .env file exists")
    
    # Check if it has the key
    with open(env_path, 'r') as f:
        content = f.read()
        
    if 'GEMINI_API_KEY' not in content:
        print(" GEMINI_API_KEY not found in .env file!")
        print("\nPlease add this line to your .env file:")
        print("GEMINI_API_KEY=your_actual_api_key_here")
        return False
    
    # Check if it's set to a placeholder
    for line in content.split('\n'):
        if line.startswith('GEMINI_API_KEY'):
            key_value = line.split('=', 1)[1].strip() if '=' in line else ''
            if not key_value or 'your_' in key_value.lower() or 'here' in key_value.lower():
                print("  GEMINI_API_KEY is set to a placeholder value!")
                print(f"Current value: {key_value}")
                print("\nPlease set it to your actual Gemini API key from:")
                print("https://makersuite.google.com/app/apikey")
                return False
            
            if len(key_value) < 20:
                print("  GEMINI_API_KEY seems too short!")
                print(f"Current length: {len(key_value)} characters")
                print("Gemini API keys are typically 39 characters long")
                return False
            
            print(f" GEMINI_API_KEY is set ({len(key_value)} characters)")
            break
    
    return True


def check_settings():
    """Check if settings can load the API key."""
    try:
        from config.settings import settings
        
        print("\n Checking settings...")
        
        if settings.gemini_api_key is None:
            print(" Settings loaded but gemini_api_key is None!")
            print("\nThis means the .env file is not being read correctly.")
            print("Make sure .env is in the project root directory:")
            print(f"  {Path(__file__).parent / '.env'}")
            return False
        
        if 'your_' in settings.gemini_api_key.lower():
            print(" API key is still a placeholder!")
            print(f"Current value: {settings.gemini_api_key}")
            return False
        
        print(f" Settings loaded successfully")
        print(f" API key loaded: {settings.gemini_api_key[:10]}...{settings.gemini_api_key[-4:]}")
        return True
        
    except Exception as e:
        print(f" Error loading settings: {e}")
        return False


def test_api_key():
    """Test if the API key works with Gemini."""
    try:
        import google.generativeai as genai
        from config.settings import settings
        
        print("\n Testing API key with Gemini...")
        
        genai.configure(api_key=settings.gemini_api_key)
        model = genai.GenerativeModel('gemini-1.5-pro')
        
        response = model.generate_content("Say 'Hello, I am working!'")
        
        print(" API key is valid and working!")
        print(f"Response: {response.text}")
        return True
        
    except Exception as e:
        print(f" API key test failed: {e}")
        print("\nPlease check:")
        print("1. Your API key is correct")
        print("2. Get a new key at: https://makersuite.google.com/app/apikey")
        print("3. Make sure the Gemini API is enabled")
        return False


def main():
    print("="*60)
    print(" GEMINI API KEY CONFIGURATION CHECKER")
    print("="*60)
    
    # Check .env file
    if not check_env_file():
        print("\n" + "="*60)
        print(" CONFIGURATION FAILED")
        print("="*60)
        print("\nTo fix:")
        print("1. Create/edit .env file in project root")
        print("2. Add: GEMINI_API_KEY=your_actual_key")
        print("3. Get key from: https://makersuite.google.com/app/apikey")
        sys.exit(1)
    
    # Check settings
    if not check_settings():
        print("\n" + "="*60)
        print(" SETTINGS FAILED")
        print("="*60)
        sys.exit(1)
    
    # Test API key
    if not test_api_key():
        print("\n" + "="*60)
        print(" API KEY TEST FAILED")
        print("="*60)
        sys.exit(1)
    
    print("\n" + "="*60)
    print(" ALL CHECKS PASSED!")
    print("="*60)
    print("\nYour Gemini API key is configured correctly!")
    print("You can now run the backend successfully.")


if __name__ == "__main__":
    main()



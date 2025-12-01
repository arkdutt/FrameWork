#!/usr/bin/env python3
"""
List available Gemini models to find the correct model name.
"""
import google.generativeai as genai
import sys
import os
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent / 'app' / 'backend'))

try:
    from config.settings import settings
    
    print("="*60)
    print(" LISTING AVAILABLE GEMINI MODELS")
    print("="*60)
    
    if not settings.gemini_api_key:
        print("\n No API key found!")
        print("Please set GEMINI_API_KEY in your .env file")
        sys.exit(1)
    
    print(f"\n Using API key: {settings.gemini_api_key[:10]}...{settings.gemini_api_key[-4:]}")
    
    # Configure Gemini
    genai.configure(api_key=settings.gemini_api_key)
    
    print("\n Available Models:")
    print("-" * 60)
    
    for model in genai.list_models():
        if 'generateContent' in model.supported_generation_methods:
            print(f"\n {model.name}")
            print(f"   Display Name: {model.display_name}")
            print(f"   Description: {model.description}")
            print(f"   Methods: {', '.join(model.supported_generation_methods)}")
    
    print("\n" + "="*60)
    print(" Use one of the model names above (without 'models/' prefix)")
    print("="*60)
    
    print("\n Recommended for your app:")
    print("   - gemini-1.5-flash → Fast and efficient")
    print("   - gemini-1.5-pro → Higher quality")
    print("   - gemini-pro → Older, stable version")
    
except Exception as e:
    print(f"\n Error: {e}")
    print("\nPlease ensure:")
    print("1. GEMINI_API_KEY is set in .env file")
    print("2. API key is valid")
    print("3. You have internet connection")
    sys.exit(1)



"""
Configuration settings for the filmmaker app.
"""
from pydantic_settings import BaseSettings
from typing import Optional, Union
from pydantic import field_validator
import os
from pathlib import Path


# Find the project root (where .env should be)
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
ENV_FILE = PROJECT_ROOT / ".env"


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # MongoDB
    mongodb_url: str = "mongodb://localhost:27017"
    mongodb_database: str = "filmmaker_db"
    
    # API
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    
    # CORS
    cors_origins: Union[list, str] = ["http://localhost:3000"]
    
    # WebSocket
    websocket_heartbeat_interval: int = 30
    
    # Agent settings (placeholders for your implementation)
    openai_api_key: Optional[str] = None
    gemini_api_key: Optional[str] = None
    max_retries: int = 3
    
    @field_validator('cors_origins', mode='before')
    @classmethod
    def parse_cors_origins(cls, v):
        """Parse CORS origins from comma-separated string or list."""
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(',')]
        return v
    
    class Config:
        env_file = str(ENV_FILE)
        env_file_encoding = 'utf-8'
        case_sensitive = False


# Print where we're looking for .env file (for debugging)
print(f" Looking for .env file at: {ENV_FILE}")
if ENV_FILE.exists():
    print(f" Found .env file")
else:
    print(f" .env file NOT found at {ENV_FILE}")

settings = Settings()

# Debug: Print if API key is loaded
if settings.gemini_api_key:
    print(f" Gemini API key loaded: {settings.gemini_api_key[:10]}...{settings.gemini_api_key[-4:]}")
else:
    print(f" Gemini API key NOT loaded!")
    print(f"   Please add GEMINI_API_KEY=your_key to {ENV_FILE}")



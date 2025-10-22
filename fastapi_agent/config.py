"""
Configuration settings for FastAPI AI Agent Service
"""
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    
    # App settings
    APP_NAME: str = "AI Sales Agent Service"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    
    # Django Backend API
    DJANGO_API_URL: str = "http://web:8000"
    DJANGO_API_KEY: str = "change-this-in-production"
    
    # OpenAI API (for ai_agent compatibility)
    OPENAI_API_KEY: str = ""
    DIGITALOCEAN_AGENT_URL: str = ""
    
    # Ollama LLM
    OLLAMA_URL: str = "http://ollama:11434"
    OLLAMA_MODEL: str = "phi3:mini"
    
    # Database
    DATABASE_URL: str = "postgresql://agent:agent@fastapi_db:5432/agent_db"
    
    # ChromaDB
    CHROMA_PERSIST_DIR: str = "./chroma_db"
    
    # Audio settings
    WHISPER_MODEL: str = "base"  # tiny, base, small, medium, large
    TTS_LANGUAGE: str = "ar"
    AUDIO_STORAGE_PATH: str = "./recordings"
    
    # WebRTC
    STUN_SERVER: Optional[str] = "stun:stun.l.google.com:19302"
    
    # CORS
    CORS_ORIGINS: list = [
        "http://localhost:3000",
        "http://localhost:8000",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:8000",
    ]
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()


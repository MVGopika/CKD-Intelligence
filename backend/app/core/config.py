"""
Configuration module for backend settings
"""
from pydantic_settings import BaseSettings
from functools import lru_cache
import os
from pathlib import Path

class Settings(BaseSettings):
    """Application settings from environment variables"""
    
    # Database
    DATABASE_URL: str = os.getenv(
        "postgresql://neondb_owner:npg_uhf7Ux9cQSel@ep-divine-dew-ai8msfjp-pooler.c-4.us-east-1.aws.neon.tech/CKD%20Intelligence?sslmode=require&channel_binding=require",
        "sqlite:///./ckd_intelligence.db"
    )
    
    # JWT
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 480  # 8 hours
    
    # API
    API_TITLE: str = "CKD Intelligence API"
    API_VERSION: str = "1.0.0"
    API_DESCRIPTION: str = "AI-powered chronic kidney disease prediction and decision support"
    
    # CORS
    ALLOWED_ORIGINS: list = [
        "http://localhost:3000",
        "http://localhost:8000",
        "https://localhost:3000",
    ]
    
    # ML Models path (point to ckd_project saved models folder)
    # Default is computed relative to this file so it works regardless
    # of the working directory used to start the server.
    _default_models_path = str(Path(__file__).resolve().parents[3] / "ckd_project" / "models" / "saved_models")
    MODELS_PATH: str = os.getenv("MODELS_PATH", _default_models_path)
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True

@lru_cache()
def get_settings():
    """Get cached settings"""
    return Settings()

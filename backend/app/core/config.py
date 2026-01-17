
from pydantic_settings import BaseSettings
from typing import List, Optional

class Settings(BaseSettings):
    PROJECT_NAME: str = "Nexus AI"
    API_V1_STR: str = "/api"
    SECRET_KEY: str = "CHANGE_THIS_IN_PRODUCTION_SECRET_KEY"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    
    # Database
    DATABASE_URL: str = "sqlite:///./sql_app.db"
    
    # AI (OpenRouter)
    OPENROUTER_API_KEY: str = ""
    
    # HH.ru Integration
    HH_CLIENT_ID: Optional[str] = None
    HH_CLIENT_SECRET: Optional[str] = None
    HH_REDIRECT_URI: Optional[str] = "http://localhost:8000/api/auth/hh/callback"

    # CORS
    BACKEND_CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://127.0.0.1:3000", "http://127.0.0.1:5500", "http://localhost:5500"]

    class Config:
        env_file = ".env"

settings = Settings()

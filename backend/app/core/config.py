
from pydantic_settings import BaseSettings
from typing import List, Optional

class Settings(BaseSettings):
    PROJECT_NAME: str = "Nexus AI"
    API_V1_STR: str = "/api"
    SECRET_KEY: str = "NexusAI2025besteverandnoonecanbeatme"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    
    # Database
    DATABASE_URL: str = "sqlite:///./sql_app.db"
    
    # AI (OpenRouter & GigaChat)
    OPENROUTER_API_KEY: str = ""
    AI_MODEL_NAME: str = "nex-agi/deepseek-v3.1-nex-n1:free"
    
    # GigaChat API
    GIGACHAT_API_KEY: Optional[str] = None
    GIGACHAT_SCOPE: str = "GIGACHAT_API_PERS"
    USE_GIGACHAT: bool = False  # Переключатель между OpenRouter и GigaChat
    giga_chat_client_id: Optional[str] = None
    giga_chat_cient_secret: Optional[str] = None
    
    # HH.ru Integration
    HH_CLIENT_ID: Optional[str] = None
    HH_CLIENT_SECRET: Optional[str] = None
    HH_REDIRECT_URI: Optional[str] = "http://localhost:8000/api/auth/hh/callback"
    
    # Automated HH.ru Auth
    EMAIL: Optional[str] = None
    PASSWORD: Optional[str] = None

    # Subscription Tiers
    SUBSCRIPTION_TIERS: dict = {
        "FREE": {
            "name": "Free Trial",
            "price": 0,
            "resume_limit": 30,
            "trial_days": 14,
            "is_trial": True
        },
        "START": {
            "name": "Start",
            "price": 15000,
            "resume_limit": 100,
            "is_trial": False
        },
        "BASIC": {
            "name": "Basic",
            "price": 75000,
            "resume_limit": 500,
            "is_trial": False
        },
        "PRO": {
            "name": "Pro",
            "price": 250000,
            "resume_limit": 10000000,  # 10 Million (Unlimited)
            "is_trial": False
        }
    }

    # CORS
    BACKEND_CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://127.0.0.1:3000", "http://127.0.0.1:5500", "http://localhost:5500", "null"]

    class Config:
        env_file = ".env"

settings = Settings()

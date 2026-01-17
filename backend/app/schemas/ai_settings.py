
from pydantic import BaseModel
from typing import Optional

class AISettingsBase(BaseModel):
    ai_role: str = "Эксперт по подбору персонала"
    system_prompt: str = """Вы - опытный HR-специалист с глубокими знаниями в области подбора персонала. 
Ваша задача - объективно оценивать кандидатов на соответствие требованиям вакансии и предоставлять практические рекомендации."""
    model_name: str = "x-ai/grok-4.1-fast"
    temperature: float = 0.7

class AISettingsCreate(AISettingsBase):
    pass

class AISettingsUpdate(BaseModel):
    ai_role: Optional[str] = None
    system_prompt: Optional[str] = None
    model_name: Optional[str] = None
    temperature: Optional[float] = None

class AISettings(AISettingsBase):
    id: int
    user_id: int
    
    class Config:
        from_attributes = True

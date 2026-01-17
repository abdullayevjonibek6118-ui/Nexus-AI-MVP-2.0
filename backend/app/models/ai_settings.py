
from sqlalchemy import Column, Integer, String, Text, Float, ForeignKey
from sqlalchemy.orm import relationship
from app.db.base_class import Base

class AISettings(Base):
    __tablename__ = "ai_settings"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True)
    
    # AI Configuration
    ai_role = Column(String, default="Эксперт по подбору персонала")
    system_prompt = Column(Text, default="""Вы - опытный HR-специалист с глубокими знаниями в области подбора персонала. 
Ваша задача - объективно оценивать кандидатов на соответствие требованиям вакансии и предоставлять практические рекомендации.""")
    model_name = Column(String, default="x-ai/grok-4.1-fast")
    temperature = Column(Float, default=0.7)
    
    # Relationship
    user = relationship("User", back_populates="ai_settings")


from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from app.db.base_class import Base
from datetime import datetime

class Vacancy(Base):
    __tablename__ = "vacancy"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True, nullable=False)
    description = Column(Text, nullable=False)
    required_skills = Column(String)  # Comma separated or JSON
    experience_level = Column(String)
    salary_range = Column(String)
    skill_weights = Column(Text, nullable=True) # JSON string of skill weights
    owner_id = Column(Integer, ForeignKey("users.id"))
    
    # HH.ru Integration
    hh_id = Column(String, index=True, nullable=True)
    hh_status = Column(String, nullable=True) # e.g., "active", "closed"
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    published_at = Column(DateTime, nullable=True)

    owner = relationship("app.models.user.User", backref="vacancies")

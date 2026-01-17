
from sqlalchemy import Column, Integer, String, Text, ForeignKey
from sqlalchemy.orm import relationship
from app.db.base_class import Base

class Vacancy(Base):
    __tablename__ = "vacancy"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True, nullable=False)
    description = Column(Text, nullable=False)
    required_skills = Column(String)  # Comma separated or JSON
    experience_level = Column(String)
    salary_range = Column(String)
    owner_id = Column(Integer, ForeignKey("users.id"))

    owner = relationship("app.models.user.User", backref="vacancies")

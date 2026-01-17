
from sqlalchemy import Column, Integer, String, Float, Text, ForeignKey, JSON
from sqlalchemy.orm import relationship
from app.db.base_class import Base

class Candidate(Base):
    __tablename__ = "candidates"

    id = Column(Integer, primary_key=True, index=True)
    vacancy_id = Column(Integer, ForeignKey("vacancy.id"))
    filename = Column(String)
    content = Column(Text) # Extracted text
    
    # AI Analysis Results
    score = Column(Float, default=0.0)
    skills_match = Column(JSON)
    missing_skills = Column(JSON)
    summary = Column(Text)
    recommendation = Column(String)
    status = Column(String, default="NEW") # NEW, SHORTLIST, REJECTED, APPROVED

    vacancy = relationship("app.models.vacancy.Vacancy", backref="candidates")

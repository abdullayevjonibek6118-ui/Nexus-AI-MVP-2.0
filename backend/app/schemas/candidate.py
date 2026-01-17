
from typing import Optional, List
from pydantic import BaseModel

class CandidateBase(BaseModel):
    filename: str
    content: Optional[str] = None
    summary: Optional[str] = None
    recommendation: Optional[str] = None
    score: Optional[float] = 0.0
    status: Optional[str] = "NEW"

class CandidateCreate(BaseModel):
    vacancy_id: int
    # content and filename usually come from file upload, but for manually adding maybe needed
    pass

class Candidate(CandidateBase):
    id: int
    vacancy_id: int
    skills_match: Optional[List[str]] = []
    missing_skills: Optional[List[str]] = []

    class Config:
        orm_mode = True

class CandidateAnalysisResult(BaseModel):
    score: float
    skills_match: List[str]
    missing_skills: List[str]
    summary: str
    recommendation: str

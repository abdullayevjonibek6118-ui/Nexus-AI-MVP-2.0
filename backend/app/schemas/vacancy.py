
from typing import Optional, List
from pydantic import BaseModel

class VacancyBase(BaseModel):
    title: str
    description: str
    required_skills: Optional[str] = None
    experience_level: Optional[str] = None
    salary_range: Optional[str] = None
    skill_weights: Optional[str] = None

class VacancyCreate(VacancyBase):
    pass

class VacancyUpdate(VacancyBase):
    pass

class Vacancy(VacancyBase):
    id: int
    owner_id: int
    hh_id: Optional[str] = None
    hh_status: Optional[str] = None

    class Config:
        from_attributes = True

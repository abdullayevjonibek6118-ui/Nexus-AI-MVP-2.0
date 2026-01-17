
from typing import Optional, List
from pydantic import BaseModel

class VacancyBase(BaseModel):
    title: str
    description: str
    required_skills: Optional[str] = None
    experience_level: Optional[str] = None
    salary_range: Optional[str] = None

class VacancyCreate(VacancyBase):
    pass

class VacancyUpdate(VacancyBase):
    pass

class Vacancy(VacancyBase):
    id: int
    owner_id: int

    class Config:
        orm_mode = True


from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.api import deps
from app.models.vacancy import Vacancy
from app.models.user import User
from app.schemas.vacancy import VacancyCreate, Vacancy as VacancySchema

router = APIRouter()

@router.post("/", response_model=VacancySchema)
def create_vacancy(
    *,
    db: Session = Depends(deps.get_db),
    vacancy_in: VacancyCreate,
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """
    Create new vacancy.
    """
    vacancy = Vacancy(
        title=vacancy_in.title,
        description=vacancy_in.description,
        required_skills=vacancy_in.required_skills,
        experience_level=vacancy_in.experience_level,
        salary_range=vacancy_in.salary_range,
        owner_id=current_user.id,
    )
    db.add(vacancy)
    db.commit()
    db.refresh(vacancy)
    return vacancy

@router.get("/", response_model=List[VacancySchema])
def read_vacancies(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """
    Retrieve vacancies.
    """
    vacancies = db.query(Vacancy).filter(Vacancy.owner_id == current_user.id).offset(skip).limit(limit).all()
    return vacancies

@router.get("/{id}", response_model=VacancySchema)
def read_vacancy(
    *,
    db: Session = Depends(deps.get_db),
    id: int,
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """
    Get vacancy by ID.
    """
    vacancy = db.query(Vacancy).filter(Vacancy.id == id, Vacancy.owner_id == current_user.id).first()
    if not vacancy:
        raise HTTPException(status_code=404, detail="Vacancy not found")
    return vacancy

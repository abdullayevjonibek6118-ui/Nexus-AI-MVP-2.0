
from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.api import deps
from app.models.vacancy import Vacancy
from app.models.user import User
from app.models.candidate import Candidate
from app.schemas.vacancy import VacancyCreate, Vacancy as VacancySchema
from app.services.mock_data import generate_mock_resume, get_random_name
import random

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
        skill_weights=vacancy_in.skill_weights,
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
@router.post("/{id}/publish-hh", response_model=VacancySchema)
def publish_vacancy_hh(
    *,
    db: Session = Depends(deps.get_db),
    id: int,
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """
    Publish vacancy to HH.ru.
    """
    vacancy = db.query(Vacancy).filter(Vacancy.id == id, Vacancy.owner_id == current_user.id).first()
    if not vacancy:
        raise HTTPException(status_code=404, detail="Vacancy not found")
    
    from app.services.hh import hh_service
    
    # Priority: 1. User's manually linked account, 2. Automated service account
    token = current_user.hh_access_token
    if not token:
        token = hh_service.get_automated_token()
    
    if not token and not hh_service.mock_mode:
        raise HTTPException(status_code=401, detail="HH.ru account not connected. Please authorize.")
    
    result = hh_service.publish_vacancy({
        "id": vacancy.id,
        "title": vacancy.title,
        "description": vacancy.description
    }, token=token)
    
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
        
    vacancy.hh_id = result.get("id")
    vacancy.hh_status = result.get("status")
    db.add(vacancy)
    db.commit()
    db.refresh(vacancy)
    return vacancy

@router.post("/{id}/publish-demo", response_model=VacancySchema)
def publish_vacancy_demo(
    *,
    db: Session = Depends(deps.get_db),
    id: int,
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """
    Publish vacancy in demo mode and generate mock candidates.
    """
    vacancy = db.query(Vacancy).filter(Vacancy.id == id, Vacancy.owner_id == current_user.id).first()
    if not vacancy:
        raise HTTPException(status_code=404, detail="Vacancy not found")
    
    # Generate 10-20 candidates
    num_candidates = random.randint(10, 20)
    for _ in range(num_candidates):
        name = get_random_name()
        content = generate_mock_resume(vacancy.title, vacancy.required_skills)
        
        # Determine a mock score (for immediate visual feedback)
        score = random.uniform(0.4, 0.95)
        
        candidate = Candidate(
            vacancy_id=vacancy.id,
            filename=f"{name}.txt",
            content=content,
            score=score,
            status="NEW",
            # We don't fill full AI analysis here, 
            # as the user might want to trigger it themselves
            # or we can fill some basic fields
            summary="Автоматически сгенерированный демо-кандидат.",
            recommendation="Рекомендуется к рассмотрению" if score > 0.7 else "Требует уточнения"
        )
        db.add(candidate)
    
    vacancy.hh_status = "PUBLISHED" # Mock status
    db.add(vacancy)
    db.commit()
    db.refresh(vacancy)
    return vacancy

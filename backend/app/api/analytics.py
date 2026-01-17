
from typing import Any, List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.api import deps
from app.models.candidate import Candidate
from app.models.vacancy import Vacancy
from app.models.user import User

router = APIRouter()

@router.get("/")
def get_analytics(
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """
    Get dashboard analytics.
    """
    total_vacancies = db.query(Vacancy).filter(Vacancy.owner_id == current_user.id).count()
    
    # Get all vacancies for user
    vacancies = db.query(Vacancy.id).filter(Vacancy.owner_id == current_user.id).all()
    vacancy_ids = [v.id for v in vacancies]
    
    total_candidates = 0
    avg_score = 0.0
    
    if vacancy_ids:
        total_candidates = db.query(Candidate).filter(Candidate.vacancy_id.in_(vacancy_ids)).count()
        avg_score_query = db.query(func.avg(Candidate.score)).filter(Candidate.vacancy_id.in_(vacancy_ids)).scalar()
        if avg_score_query:
            avg_score = round(avg_score_query, 2)

    return {
        "active_vacancies": total_vacancies,
        "total_candidates": total_candidates,
        "avg_ai_score": avg_score,
        # Mocking other metrics for MVP as per PRD "Simple Analytics"
        "time_to_hire": "12 days", 
        "top_skills": ["Python", "FastAPI", "SQL"] 
    }

@router.get("/export")
def export_analytics(
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """
    Mock export function.
    """
    return {"message": "CSV Export feature - check console or download mock"}

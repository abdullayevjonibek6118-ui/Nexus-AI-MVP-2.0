
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
    # try:
    
    # Initialize defaults
    total_vacancies = db.query(Vacancy).filter(Vacancy.owner_id == current_user.id).count()
    
    # Get all vacancies for user
    vacancies = db.query(Vacancy.id).filter(Vacancy.owner_id == current_user.id).all()
    vacancy_ids = [v.id for v in vacancies]
    
    total_candidates = 0
    avg_score = 0.0
    status_breakdown = {}
    hh_candidates = 0
    manual_candidates = 0
    
    if vacancy_ids:
        total_candidates = db.query(Candidate).filter(Candidate.vacancy_id.in_(vacancy_ids)).count()
        avg_score_query = db.query(func.avg(Candidate.score)).filter(Candidate.vacancy_id.in_(vacancy_ids)).scalar()
        if avg_score_query:
            avg_score = round(avg_score_query, 2)
            
        candidate_stats = db.query(
            Candidate.status, 
            func.count(Candidate.id)
        ).filter(Candidate.vacancy_id.in_(vacancy_ids)).group_by(Candidate.status).all()
        
        status_breakdown = {str(status) if status else "Unknown": count for status, count in candidate_stats}
        
        # Calculate sources
        hh_candidates = db.query(Candidate).filter(
            Candidate.vacancy_id.in_(vacancy_ids),
            Candidate.hh_resume_id.isnot(None)
        ).count()
        
        manual_candidates = total_candidates - hh_candidates

    return {
        "active_vacancies": total_vacancies,
        "total_candidates": total_candidates,
        "avg_ai_score": avg_score,
        "status_breakdown": status_breakdown,
        "sources": {
            "hh_ru": hh_candidates,
            "manual": manual_candidates
        },
        "top_skills": ["Python", "FastAPI", "React", "AI Integration"],
        "metrics": {
            "time_to_hire": 14, # Placeholder: Avg days to close vacancy (mocked)
            "funnel_conversion": {
                "new_to_screened": 85,
                "screened_to_interview": 40,
                "interview_to_offer": 15
            },
            "response_rate": 65, # Mock: % of candidates who replied
            "cost_per_hire": 50000 # Mock: Estimated cost
        }
    }
    # except Exception as e:
    #     import traceback
    #     traceback.print_exc()
    #     raise e

@router.get("/export")
def export_analytics(
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """
    Mock export function.
    """
    return {"message": "CSV Export feature - check console or download mock"}

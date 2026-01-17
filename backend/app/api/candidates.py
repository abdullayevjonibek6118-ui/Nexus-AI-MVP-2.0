
from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException, File, UploadFile
from sqlalchemy.orm import Session
from app.api import deps
from app.models.candidate import Candidate
from app.models.vacancy import Vacancy
from app.models.user import User
from app.schemas.candidate import Candidate as CandidateSchema
# from app.services.gemini import analyze_resume
from app.services.openrouter import analyze_resume

router = APIRouter()

@router.post("/upload", response_model=CandidateSchema)
async def upload_candidate(
    vacancy_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """
    Upload a resume file and create a candidate entry.
    """
    vacancy = db.query(Vacancy).filter(Vacancy.id == vacancy_id, Vacancy.owner_id == current_user.id).first()
    if not vacancy:
        raise HTTPException(status_code=404, detail="Vacancy not found")

    content_bytes = await file.read()
    # Simple text extraction for MVP (assuming .txt or simple read)
    # For PDF/DOCX in real prod, use pypdf or similar. 
    # Here we assume the user uploads a text file or we treat it as text.
    # To support the "Upload PDF/DOCX" requirement of PRD in MVP without heavy libs, 
    # we might just store the file content if it's binary, but Gemini needs text.
    # For this MVP step, let's assume text files or try to decode utf-8.
    try:
        content_text = content_bytes.decode("utf-8")
    except:
        content_text = "Binary file content placeholder. Real extraction needed for PDF."

    candidate = Candidate(
        vacancy_id=vacancy_id,
        filename=file.filename,
        content=content_text
    )
    db.add(candidate)
    db.commit()
    db.refresh(candidate)
    return candidate

@router.post("/{candidate_id}/analyze", response_model=CandidateSchema)
def analyze_candidate(
    candidate_id: int,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """
    Trigger AI analysis for a candidate.
    """
    candidate = db.query(Candidate).filter(Candidate.id == candidate_id).first()
    if not candidate:
         raise HTTPException(status_code=404, detail="Candidate not found")
    
    # Verify ownership through vacancy
    vacancy = db.query(Vacancy).filter(Vacancy.id == candidate.vacancy_id, Vacancy.owner_id == current_user.id).first()
    if not vacancy:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    # Fetch AI Settings
    from app.models.ai_settings import AISettings
    ai_settings = db.query(AISettings).filter(AISettings.user_id == current_user.id).first()
    
    # Use settings if available, otherwise defaults
    system_prompt = ai_settings.system_prompt if ai_settings else None
    model = ai_settings.model_name if ai_settings else "x-ai/grok-4.1-fast"
    temperature = ai_settings.temperature if ai_settings else 0.7

    # Call AI Service
    result = analyze_resume(
        vacancy_description=vacancy.description, 
        resume_text=candidate.content,
        system_prompt=system_prompt,
        model=model,
        temperature=temperature
    )
    
    candidate.score = result.score
    candidate.skills_match = result.skills_match
    candidate.missing_skills = result.missing_skills
    candidate.summary = result.summary
    candidate.recommendation = result.recommendation
    
    db.commit()
    db.refresh(candidate)
    return candidate

@router.get("/", response_model=List[CandidateSchema])
def read_candidates(
    vacancy_id: int,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """
    List candidates for a vacancy.
    """
    vacancy = db.query(Vacancy).filter(Vacancy.id == vacancy_id, Vacancy.owner_id == current_user.id).first()
    if not vacancy:
        raise HTTPException(status_code=404, detail="Vacancy not found")
    
    return db.query(Candidate).filter(Candidate.vacancy_id == vacancy_id).all()

@router.get("/{candidate_id}", response_model=CandidateSchema)
def read_candidate_detail(
    candidate_id: int,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    vacancy = db.query(Vacancy).join(Candidate).filter(Candidate.id == candidate_id, Vacancy.owner_id == current_user.id).first()
    if not vacancy:
         raise HTTPException(status_code=404, detail="Candidate not found")
    
    candidate = db.query(Candidate).filter(Candidate.id == candidate_id).first()
    return candidate

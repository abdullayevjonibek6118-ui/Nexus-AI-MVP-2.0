
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
from app.services.subscription import subscription_service

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
    Supports PDF, DOCX, and TXT formats.
    """
    vacancy = db.query(Vacancy).filter(Vacancy.id == vacancy_id, Vacancy.owner_id == current_user.id).first()
    if not vacancy:
        raise HTTPException(status_code=404, detail="Vacancy not found")

    # Check subscription limits
    if not subscription_service.can_upload_resume(current_user):
        status = subscription_service.get_subscription_status(current_user)
        raise HTTPException(
            status_code=402,
            detail={
                "error": "SUBSCRIPTION_LIMIT_REACHED",
                "current_tier": status["tier"],
                "limit": status["limit"]
            }
        )

    content_bytes = await file.read()
    
    # Use resume parser for proper text extraction
    from app.services.resume_parser import parse_resume
    content_text = parse_resume(file.filename, content_bytes)

    candidate = Candidate(
        vacancy_id=vacancy_id,
        filename=file.filename,
        content=content_text
    )
    db.add(candidate)
    
    # Record resume usage
    subscription_service.record_resume_usage(current_user)
    
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
    from app.core.config import settings as app_settings
    ai_settings = db.query(AISettings).filter(AISettings.user_id == current_user.id).first()
    
    # Use settings if available, otherwise defaults
    system_prompt = ai_settings.system_prompt if ai_settings else None
    model = ai_settings.model_name if ai_settings else app_settings.AI_MODEL_NAME
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
    candidate.screening_questions = result.screening_questions
    
    # Automatically post the first screening question to candidate's chat
    if result.screening_questions and len(result.screening_questions) > 0:
        from app.models.chat import ChatMessage
        # Check if we already have messages to avoid duplicate greetings
        existing_msg = db.query(ChatMessage).filter(ChatMessage.candidate_id == candidate.id).first()
        if not existing_msg:
            # HR Agent Intro + First Question
            intro = f"Здравствуйте! Я ваш ИИ-рекрутер. Я ознакомился с вашим резюме на позицию '{vacancy.title}'. У меня есть несколько уточняющих вопросов:\n\n"
            full_msg = intro + result.screening_questions[0]
            db.add(ChatMessage(candidate_id=candidate.id, role="assistant", content=full_msg))

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
    List candidates for a vacancy, sorted by AI score descending.
    """
    vacancy = db.query(Vacancy).filter(Vacancy.id == vacancy_id, Vacancy.owner_id == current_user.id).first()
    if not vacancy:
        raise HTTPException(status_code=404, detail="Vacancy not found")
    
    return db.query(Candidate).filter(Candidate.vacancy_id == vacancy_id).order_by(Candidate.score.desc()).all()

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

@router.post("/sync-hh", response_model=List[CandidateSchema])
def sync_candidates_hh(
    vacancy_id: int,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """
    Sync candidates from HH.ru for a specific vacancy.
    """
    vacancy = db.query(Vacancy).filter(Vacancy.id == vacancy_id, Vacancy.owner_id == current_user.id).first()
    if not vacancy or not vacancy.hh_id:
        raise HTTPException(status_code=400, detail="Vacancy not published to HH.ru or not found")

    if not current_user.hh_access_token:
        raise HTTPException(status_code=401, detail="HH.ru account not connected. Please authorize.")

    from app.services.hh import hh_service
    
    # Check subscription limits for HH sync
    # We briefly check if they can upload AT LEAST ONE. 
    # In a full impl, we'd check how many they are syncing vs how many left.
    if not subscription_service.can_upload_resume(current_user):
        status = subscription_service.get_subscription_status(current_user)
        raise HTTPException(
            status_code=402,
            detail={
                "error": "SUBSCRIPTION_LIMIT_REACHED",
                "current_tier": status["tier"],
                "limit": status["limit"]
            }
        )

    responses = hh_service.get_responses(vacancy.hh_id, token=current_user.hh_access_token)
    
    new_candidates = []
    for resp in responses:
        # Check if already exists
        existing = db.query(Candidate).filter(Candidate.hh_resume_id == resp["hh_resume_id"]).first()
        if not existing:
            new_candidates.append(Candidate(
                vacancy_id=vacancy_id,
                filename=f"HH_Resume_{resp['hh_resume_id']}.txt",
                content=resp["content"],
                hh_resume_id=resp["hh_resume_id"],
                status="NEW"
            ))
    
    if new_candidates:
        # Check if we exceeded limit during sync
        # Process only as many as the limit allows
        status = subscription_service.get_subscription_status(current_user)
        remaining = status["limit"] - status["used"]
        
        to_process = new_candidates[:remaining]
        
        # Re-verify the list to process
        actual_new = []
        for c in to_process:
            db.add(c)
            subscription_service.record_resume_usage(current_user)
            actual_new.append(c)

        db.commit()
        for c in actual_new:
            db.refresh(c)
        
        if len(new_candidates) > remaining:
            # Maybe return a partial success?
            pass
            
    # Return all candidates for this vacancy, sorted
    return db.query(Candidate).filter(Candidate.vacancy_id == vacancy_id).order_by(Candidate.score.desc()).all()

@router.post("/{candidate_id}/generate_outreach")
def generate_outreach(
    candidate_id: int,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """
    Generate an AI outreach message for the candidate.
    """
    candidate = db.query(Candidate).filter(Candidate.id == candidate_id).first()
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")
        
    vacancy = db.query(Vacancy).filter(Vacancy.id == candidate.vacancy_id, Vacancy.owner_id == current_user.id).first()
    if not vacancy:
        raise HTTPException(status_code=403, detail="Not authorized")

    from app.services.ai_outreach import ai_outreach_service
    # Fetch AI Settings
    from app.models.ai_settings import AISettings
    from app.core.config import settings as app_settings
    ai_settings = db.query(AISettings).filter(AISettings.user_id == current_user.id).first()
    model = ai_settings.model_name if ai_settings else app_settings.AI_MODEL_NAME

    message = ai_outreach_service.generate_message(
        candidate_name=candidate.filename.replace(".txt", "").replace("HH_Resume_", "Candidate"),
        vacancy_title=vacancy.title,
        skills=candidate.skills_match,
        model=model
    )
    
    return {"message": message}

@router.post("/{candidate_id}/send_outreach")
def send_outreach(
    candidate_id: int,
    message_data: dict, # {"message": "..."}
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """
    Send the outreach message via HH.ru service.
    """
    candidate = db.query(Candidate).filter(Candidate.id == candidate_id).first()
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")
    
    if not candidate.hh_resume_id:
        # Mock send for local files
        return {"status": "sent", "mock": True, "note": "Local candidate, message logged."}

    vacancy = db.query(Vacancy).filter(Vacancy.id == candidate.vacancy_id, Vacancy.owner_id == current_user.id).first()
    
    from app.services.hh import hh_service
    result = hh_service.send_message(
        hh_resume_id=candidate.hh_resume_id,
        message=message_data["message"],
        vacancy_id=vacancy.hh_id if vacancy and vacancy.hh_id else "test",
        token=current_user.hh_access_token
    )
    
    return result

@router.get("/subscription/status")
def get_subscription_status(
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """
    Get current user's subscription status and limits.
    """
    return subscription_service.get_subscription_status(current_user)

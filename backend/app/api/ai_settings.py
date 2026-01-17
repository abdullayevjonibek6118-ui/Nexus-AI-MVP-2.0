
from typing import Any
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.api import deps
from app.models.ai_settings import AISettings as AISettingsModel
from app.models.user import User
from app.schemas.ai_settings import AISettings, AISettingsCreate, AISettingsUpdate

router = APIRouter()

@router.get("/", response_model=AISettings)
def get_ai_settings(
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """
    Get current user's AI settings.
    """
    settings = db.query(AISettingsModel).filter(AISettingsModel.user_id == current_user.id).first()
    
    if not settings:
        # Create default settings if none exist
        settings = AISettingsModel(user_id=current_user.id)
        db.add(settings)
        db.commit()
        db.refresh(settings)
    
    return settings

@router.post("/", response_model=AISettings)
def create_or_update_ai_settings(
    settings_in: AISettingsCreate,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """
    Create or update AI settings for current user.
    """
    settings = db.query(AISettingsModel).filter(AISettingsModel.user_id == current_user.id).first()
    
    if settings:
        # Update existing
        settings.ai_role = settings_in.ai_role
        settings.system_prompt = settings_in.system_prompt
        settings.model_name = settings_in.model_name
        settings.temperature = settings_in.temperature
    else:
        # Create new
        settings = AISettingsModel(
            user_id=current_user.id,
            **settings_in.dict()
        )
        db.add(settings)
    
    db.commit()
    db.refresh(settings)
    return settings

@router.put("/{settings_id}", response_model=AISettings)
def update_ai_settings(
    settings_id: int,
    settings_in: AISettingsUpdate,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """
    Update specific AI settings.
    """
    settings = db.query(AISettingsModel).filter(
        AISettingsModel.id == settings_id,
        AISettingsModel.user_id == current_user.id
    ).first()
    
    if not settings:
        raise HTTPException(status_code=404, detail="AI Settings not found")
    
    update_data = settings_in.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(settings, field, value)
    
    db.commit()
    db.refresh(settings)
    return settings

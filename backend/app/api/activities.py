from typing import Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.api import deps
from app.models.activity import ActivityLog
from pydantic import BaseModel
from datetime import datetime

router = APIRouter()

class ActivitySchema(BaseModel):
    id: int
    action_type: str
    description: str
    entity_type: Optional[str] = None
    entity_id: Optional[str] = None
    entity_name: Optional[str] = None
    created_date: datetime

    class Config:
        orm_mode = True

@router.get("/", response_model=List[ActivitySchema])
def read_activities(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    current_user = Depends(deps.get_current_active_user),
):
    activities = db.query(ActivityLog).order_by(ActivityLog.created_date.desc()).offset(skip).limit(limit).all()
    return activities

@router.post("/", response_model=ActivitySchema)
def create_activity(
    action_type: str,
    description: str,
    entity_type: Optional[str] = None,
    entity_id: Optional[str] = None,
    entity_name: Optional[str] = None,
    db: Session = Depends(deps.get_db),
    current_user = Depends(deps.get_current_active_user),
):
    activity = ActivityLog(
        action_type=action_type,
        description=description,
        entity_type=entity_type,
        entity_id=entity_id,
        entity_name=entity_name,
        created_by=current_user.email
    )
    db.add(activity)
    db.commit()
    db.refresh(activity)
    return activity

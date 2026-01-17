from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.api import deps
from app.models.chat import ChatMessage
from pydantic import BaseModel
from datetime import datetime

router = APIRouter()

class ChatMessageSchema(BaseModel):
    id: int
    candidate_id: int
    role: str
    content: str
    created_at: datetime

    class Config:
        orm_mode = True

class ChatMessageCreate(BaseModel):
    candidate_id: int
    role: str
    content: str

@router.get("/{candidate_id}", response_model=List[ChatMessageSchema])
def get_chat_history(
    candidate_id: int,
    db: Session = Depends(deps.get_db),
    current_user = Depends(deps.get_current_active_user),
):
    messages = db.query(ChatMessage).filter(ChatMessage.candidate_id == candidate_id).order_by(ChatMessage.created_at.asc()).all()
    return messages

@router.post("/", response_model=ChatMessageSchema)
def create_chat_message(
    msg: ChatMessageCreate,
    db: Session = Depends(deps.get_db),
    current_user = Depends(deps.get_current_active_user),
):
    db_msg = ChatMessage(
        candidate_id=msg.candidate_id,
        role=msg.role,
        content=msg.content
    )
    db.add(db_msg)
    db.commit()
    db.refresh(db_msg)
    return db_msg

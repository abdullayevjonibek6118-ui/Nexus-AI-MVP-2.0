from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, JSON, Text
from sqlalchemy.sql import func
from app.db.base_class import Base

class ChatMessage(Base):
    __tablename__ = "chat_messages"

    id = Column(Integer, primary_key=True, index=True)
    candidate_id = Column(Integer, ForeignKey("candidates.id"))
    role = Column(String) # user, assistant, system
    content = Column(Text)
    metadata_info = Column(JSON, nullable=True) # Renamed from metadata to avoid conflict with Base.metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())

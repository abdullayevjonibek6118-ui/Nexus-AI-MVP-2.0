from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, JSON
from sqlalchemy.sql import func
from app.db.base_class import Base

class ActivityLog(Base):
    __tablename__ = "activity_logs"

    id = Column(Integer, primary_key=True, index=True)
    action_type = Column(String, index=True)
    description = Column(String)
    entity_type = Column(String, nullable=True)
    entity_id = Column(String, nullable=True)
    entity_name = Column(String, nullable=True)
    metadata_info = Column(JSON, nullable=True) # Renamed to avoid reserved word
    created_date = Column(DateTime(timezone=True), server_default=func.now())
    created_by = Column(String, nullable=True)

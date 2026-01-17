from datetime import datetime
from sqlalchemy import Boolean, Column, Integer, String, DateTime
from sqlalchemy.orm import relationship
from app.db.base_class import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String, nullable=True)
    is_active = Column(Boolean(), default=True)
    # Subscription & Trial
    trial_start_date = Column(DateTime, default=datetime.utcnow)
    subscription_tier = Column(String, default="FREE")
    subscription_end_date = Column(DateTime, nullable=True)
    resumes_used_current_period = Column(Integer, default=0)

    # HH.ru OAuth
    
    # Relationships
    ai_settings = relationship("AISettings", back_populates="user", uselist=False)

    @property
    def hh_connected(self) -> bool:
        return bool(self.hh_access_token)

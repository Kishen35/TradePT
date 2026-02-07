from sqlalchemy import Column, DateTime, Integer, String, Text, func
from app.config.db import Base

class ConversationalLogs(Base):
    __tablename__ = "conversational_logs"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True, nullable=False)
    role = Column(String, nullable=False)  # "user" | "assistant"
    message = Column(Text, nullable=False)
    model = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

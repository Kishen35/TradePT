from pydantic import BaseModel
from typing import Literal

class ConversationalLogCreate(BaseModel):
  user_id: int
  role: Literal["user", "assistant"]
  message: str
  model: str | None = None

class ConversationalLogResponse(BaseModel):
    id: int
    user_id: int
    role: Literal["user", "assistant"]
    message: str
    model: str | None = None

    class Config:
        from_attributes = True  # SQLAlchemy compatibility

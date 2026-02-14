from pydantic import BaseModel
from typing import Literal, Optional

class UserCreate(BaseModel):
    name: str
    email: str
    password: str
    experience_level: Literal["beginner", "intermediate", "advanced"]
    trading_duration: Literal["scalper", "day trader", "swing trader", "long-term investor"]
    risk_tolerance: Literal["cut loss", "wait see", "layering"]
    capital_allocation: Literal["low risk", "medium risk", "high risk"]
    asset_preference: Literal["forex", "commodities", "crypto"]

class UserLogin(BaseModel):
    email: str
    password: str
    
class TraderTypeUpdate(BaseModel):
    trader_type: Literal["momentum", "precision"]

class UserResponse(BaseModel):
    id: int
    name: str
    email: str
    experience_level: Literal["beginner", "intermediate", "advanced"]
    trading_duration: Literal["scalper", "day trader", "swing trader", "long-term investor"]
    risk_tolerance: Literal["cut loss", "wait see", "layering"]
    capital_allocation: Literal["low risk", "medium risk", "high risk"]
    asset_preference: Literal["forex", "commodities", "crypto"]
    trader_type: Optional[Literal["momentum", "precision"]] = None

    class Config:
        from_attributes = True  # SQLAlchemy compatibility

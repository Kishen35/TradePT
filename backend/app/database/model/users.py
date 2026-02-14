from sqlalchemy import Column, Integer, String
from app.config.db import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True)
    password = Column(String, nullable=False)
    experience_level = Column(String, default="beginner")       # e.g., beginner, intermediate, advanced
    trading_duration = Column(String, default="scalper")        # e.g., scalper, day trader, swing trader, long-term investor
    risk_tolerance = Column(String, default="cut loss")         # e.g., cut loss, wait see, layering
    capital_allocation = Column(String, default="low risk")     # e.g., low risk, medium risk, high risk
    asset_preference = Column(String, default="forex")          # e.g., forex, commodities, crypto
    trader_type = Column(String, nullable=True, default=None)  # "momentum" or "precision", set after style profiling

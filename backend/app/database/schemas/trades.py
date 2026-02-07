"""
Trade Schemas for the TradePT Application

These are Pydantic schemas for validation and serialization.
NOTE: The actual Trade SQLAlchemy model must be created in database/models/trades.py
by a team member with database modification permissions.

Required Trade model fields:
- id: Integer, primary key
- user_id: Integer, foreign key to users.id
- contract_type: String (e.g., "CALL", "PUT", "MULTIPLIER")
- symbol: String (e.g., "EURUSD", "Volatility 75")
- buy_price: Float
- sell_price: Float (nullable)
- profit_loss: Float (nullable)
- purchase_time: DateTime
- sell_time: DateTime (nullable)
"""
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List


class TradeBase(BaseModel):
    """Base schema for Trade data."""
    user_id: int
    contract_type: str = Field(..., examples=["CALL", "PUT", "MULTIPLIER"])
    symbol: str = Field(..., examples=["EURUSD", "Volatility 75", "BTC/USD"])
    buy_price: float = Field(..., gt=0, description="Entry price for the trade")
    sell_price: Optional[float] = Field(None, gt=0, description="Exit price for the trade")
    profit_loss: Optional[float] = Field(None, description="Realized profit or loss")
    purchase_time: datetime = Field(..., description="Trade entry time")
    sell_time: Optional[datetime] = Field(None, description="Trade exit time")


class TradeCreate(TradeBase):
    """Schema for creating a new trade."""
    pass


class TradeUpdate(BaseModel):
    """Schema for updating a trade."""
    sell_price: Optional[float] = None
    profit_loss: Optional[float] = None
    sell_time: Optional[datetime] = None


class TradeResponse(TradeBase):
    """Schema for trade responses."""
    id: int

    class Config:
        from_attributes = True


class TradeStatistics(BaseModel):
    """Aggregated trade statistics for AI analysis."""
    total_trades: int = Field(default=0, description="Total number of trades")
    winning_trades: int = Field(default=0, description="Number of profitable trades")
    losing_trades: int = Field(default=0, description="Number of losing trades")
    win_rate: float = Field(default=0.0, ge=0, le=100, description="Win rate percentage")
    total_profit_loss: float = Field(default=0.0, description="Total P/L in dollars")
    average_profit: float = Field(default=0.0, description="Average profit per winning trade")
    average_loss: float = Field(default=0.0, description="Average loss per losing trade")
    largest_win: float = Field(default=0.0, description="Largest single winning trade")
    largest_loss: float = Field(default=0.0, description="Largest single losing trade")
    average_trade_duration_hours: float = Field(default=0.0, description="Average trade duration")
    most_traded_symbol: str = Field(default="N/A", description="Most frequently traded symbol")
    most_traded_contract_type: str = Field(default="N/A", description="Most common contract type")


class PatternDetectionResult(BaseModel):
    """Result from pattern detection analysis."""
    pattern_name: str = Field(..., description="Name of the detected pattern")
    detected: bool = Field(..., description="Whether the pattern was detected")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence score 0-1")
    details: str = Field(..., description="Description of the pattern finding")


class TradeAnalysisRequest(BaseModel):
    """Request for trade analysis."""
    user_id: int
    days: int = Field(default=7, ge=1, le=90, description="Number of days to analyze")


class TradeAnalysisResponse(BaseModel):
    """Response from trade analysis."""
    statistics: TradeStatistics
    patterns: List[PatternDetectionResult]
    insights_summary: str = Field(default="", description="Brief summary of findings")

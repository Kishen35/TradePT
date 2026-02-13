
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Optional, Protocol


class TradeProtocol(Protocol):
    """Protocol defining expected Trade object interface."""
    id: int
    user_id: int
    contract_type: str
    symbol: str
    buy_price: float
    sell_price: Optional[float]
    profit_loss: Optional[float]
    purchase_time: datetime
    sell_time: Optional[datetime]


class TradingPattern(Enum):
    """Enumeration of detectable trading patterns."""
    REVENGE_TRADING = "revenge_trading"
    OVERTRADING = "overtrading"
    LOSS_CHASING = "loss_chasing"
    CONSISTENT_TIMING = "consistent_timing"
    GOOD_POSITION_SIZING = "position_sizing"
    EMOTIONAL_TRADING = "emotional_trading"
    RISK_ISSUES = "risk_issues"


@dataclass
class PatternDetectionResult:
    """Result of pattern detection analysis."""
    pattern: TradingPattern
    detected: bool
    confidence: float
    details: str


@dataclass
class MockTradeData:
    """Mock Trade object (matches database model)."""
    id: int
    user_id: int
    contract_type: str
    symbol: str
    buy_price: float
    sell_price: float
    profit_loss: float
    purchase_time: datetime
    sell_time: datetime

@dataclass
class TradeData:
    """Trade object (matches database model)."""
    app_id: int
    buy_price: float
    contract_id: int
    contract_type: str
    duration_type: str
    growth_rate: str
    longcode: str
    payout: float
    purchase_time: datetime
    sell_price: float
    sell_time: datetime
    shortcode: str
    transaction_id: int
    underlying_symbol: str
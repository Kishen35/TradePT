
from dataclasses import dataclass
from datetime import datetime

@dataclass
class MarketSnapshot:
    """Current market data for a symbol."""
    symbol: str
    current_price: float
    change_percent: float
    timestamp: datetime

@dataclass
class AccountInfo:
    """User's account information from Deriv."""
    balance: float
    currency: str
    open_positions: int
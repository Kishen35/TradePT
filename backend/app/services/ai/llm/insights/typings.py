
from dataclasses import dataclass, field
from typing import Dict, Any, List
from datetime import datetime


@dataclass
class TradingInsight:
    """A single trading insight."""
    type: str  # "strength", "weakness", "observation"
    message: str
    priority: str  # "high", "medium", "low"


@dataclass
class InsightResponse:
    """Complete insight response for a user."""
    summary: str
    insights: List[TradingInsight]
    recommendations: List[str]
    statistics: Dict[str, Any]
    suggested_lesson: str = ""
    generated_at: str = field(default_factory=lambda: datetime.now().isoformat())

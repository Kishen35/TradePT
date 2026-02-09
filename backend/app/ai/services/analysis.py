"""
Trading Pattern Analysis Service

Provides statistical analysis of trade data including:
- Win rate calculation
- Profit/loss analysis
- Pattern detection (revenge trading, overtrading, etc.)

NOTE: This service requires a Trade model to exist in the database.
Until the Trade model is created, this service uses mock data for testing.
"""
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any, Protocol
from sqlalchemy.orm import Session
from dataclasses import dataclass
from enum import Enum
import statistics
import random
import logging

logger = logging.getLogger(__name__)


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
class MockTrade:
    """Mock trade object for development and testing."""
    id: int
    user_id: int
    contract_type: str
    symbol: str
    buy_price: float
    sell_price: float
    profit_loss: float
    purchase_time: datetime
    sell_time: datetime


def get_recent_trades(
    db: Session,
    user_id: int,
    days: int = 7
) -> List[Any]:
    """
    Fetch recent trades for a user from the database.

    Args:
        db: SQLAlchemy database session
        user_id: The user's ID
        days: Number of days to look back (default: 7)

    Returns:
        List of Trade objects

    NOTE: Currently returns mock data. When Trade model is created,
    uncomment the database query code below.
    """
    # TODO: Uncomment when Trade model exists in database/models/trades.py
    # from app.database.models.trades import Trade
    #
    # cutoff_date = datetime.now() - timedelta(days=days)
    # return db.query(Trade).filter(
    #     Trade.user_id == user_id,
    #     Trade.purchase_time >= cutoff_date
    # ).order_by(Trade.purchase_time.desc()).all()

    logger.info(f"Fetching trades for user {user_id} (last {days} days) - using mock data")
    return _get_mock_trades(user_id, days)


def calculate_win_rate(trades: List[Any]) -> float:
    """
    Calculate the win rate from a list of trades.

    Args:
        trades: List of Trade objects with profit_loss field

    Returns:
        Win rate as a percentage (0.0 to 100.0)
    """
    if not trades:
        return 0.0

    winning_trades = sum(1 for t in trades if hasattr(t, 'profit_loss') and t.profit_loss and t.profit_loss > 0)
    return (winning_trades / len(trades)) * 100


def calculate_statistics(trades: List[Any]) -> Dict[str, Any]:
    """
    Calculate comprehensive statistics from trade data.

    Args:
        trades: List of Trade objects

    Returns:
        Dictionary containing all calculated statistics
    """
    if not trades:
        return {
            "total_trades": 0,
            "winning_trades": 0,
            "losing_trades": 0,
            "win_rate": 0.0,
            "total_profit_loss": 0.0,
            "average_profit": 0.0,
            "average_loss": 0.0,
            "largest_win": 0.0,
            "largest_loss": 0.0,
            "average_trade_duration_hours": 0.0,
            "most_traded_symbol": "N/A",
            "most_traded_contract_type": "N/A",
        }

    # Separate winning and losing trades
    profits = []
    losses = []
    for t in trades:
        pl = getattr(t, 'profit_loss', 0) or 0
        if pl > 0:
            profits.append(pl)
        elif pl < 0:
            losses.append(pl)

    # Calculate trade durations
    durations = []
    for t in trades:
        sell_time = getattr(t, 'sell_time', None)
        purchase_time = getattr(t, 'purchase_time', None)
        if sell_time and purchase_time:
            duration = (sell_time - purchase_time).total_seconds() / 3600
            durations.append(duration)

    # Count symbols and contract types
    symbol_counts: Dict[str, int] = {}
    contract_counts: Dict[str, int] = {}
    for t in trades:
        symbol = getattr(t, 'symbol', 'Unknown')
        contract = getattr(t, 'contract_type', 'Unknown')
        symbol_counts[symbol] = symbol_counts.get(symbol, 0) + 1
        contract_counts[contract] = contract_counts.get(contract, 0) + 1

    total_pl = sum(getattr(t, 'profit_loss', 0) or 0 for t in trades)

    return {
        "total_trades": len(trades),
        "winning_trades": len(profits),
        "losing_trades": len(losses),
        "win_rate": calculate_win_rate(trades),
        "total_profit_loss": round(total_pl, 2),
        "average_profit": round(statistics.mean(profits), 2) if profits else 0.0,
        "average_loss": round(statistics.mean(losses), 2) if losses else 0.0,
        "largest_win": round(max(profits), 2) if profits else 0.0,
        "largest_loss": round(min(losses), 2) if losses else 0.0,
        "average_trade_duration_hours": round(statistics.mean(durations), 2) if durations else 0.0,
        "most_traded_symbol": max(symbol_counts, key=symbol_counts.get) if symbol_counts else "N/A",
        "most_traded_contract_type": max(contract_counts, key=contract_counts.get) if contract_counts else "N/A",
    }


def detect_patterns(trades: List[Any]) -> List[PatternDetectionResult]:
    """
    Detect trading patterns from trade history.

    Detects:
    - Revenge trading: Rapid trades after losses
    - Overtrading: Excessive trading frequency
    - Loss chasing: Increasing positions after losses
    - Consistent timing: Regular trading schedule (positive)
    - Risk issues: Average loss > 2x average win

    Args:
        trades: List of Trade objects

    Returns:
        List of detected patterns with confidence scores
    """
    patterns = []

    if not trades:
        return patterns

    # Sort by purchase time
    sorted_trades = sorted(trades, key=lambda t: getattr(t, 'purchase_time', datetime.min))

    # Detect revenge trading
    patterns.append(_detect_revenge_trading(sorted_trades))

    # Detect overtrading
    patterns.append(_detect_overtrading(sorted_trades))

    # Detect consistent timing (positive pattern)
    patterns.append(_detect_consistent_timing(sorted_trades))

    # Detect risk issues
    patterns.append(_detect_risk_issues(sorted_trades))

    return patterns


def _detect_revenge_trading(trades: List[Any]) -> PatternDetectionResult:
    """
    Detect revenge trading pattern.

    Revenge trading is identified when:
    - 3+ consecutive losses are followed by rapid new trades
    - New trade occurs within 30 minutes of a loss
    """
    if len(trades) < 3:
        return PatternDetectionResult(
            pattern=TradingPattern.REVENGE_TRADING,
            detected=False,
            confidence=0.0,
            details="Insufficient data for analysis (need at least 3 trades)"
        )

    rapid_trades_after_loss = 0
    consecutive_losses = 0
    max_consecutive_losses = 0

    for i in range(1, len(trades)):
        prev_trade = trades[i - 1]
        curr_trade = trades[i]

        prev_pl = getattr(prev_trade, 'profit_loss', 0) or 0
        prev_time = getattr(prev_trade, 'purchase_time', datetime.min)
        curr_time = getattr(curr_trade, 'purchase_time', datetime.min)

        # Check if previous trade was a loss
        if prev_pl < 0:
            consecutive_losses += 1
            max_consecutive_losses = max(max_consecutive_losses, consecutive_losses)
            # Check if current trade was within 30 minutes
            time_diff = (curr_time - prev_time).total_seconds() / 60
            if time_diff < 30:
                rapid_trades_after_loss += 1
        else:
            consecutive_losses = 0

    ratio = rapid_trades_after_loss / (len(trades) - 1) if len(trades) > 1 else 0
    detected = ratio > 0.25 or max_consecutive_losses >= 3

    return PatternDetectionResult(
        pattern=TradingPattern.REVENGE_TRADING,
        detected=detected,
        confidence=min(ratio * 2.5, 1.0),
        details=f"Found {rapid_trades_after_loss} rapid trades after losses. Max consecutive losses: {max_consecutive_losses}"
    )


def _detect_overtrading(trades: List[Any]) -> PatternDetectionResult:
    """
    Detect overtrading pattern.

    Overtrading is identified when average trades per day > 10
    """
    if len(trades) < 2:
        return PatternDetectionResult(
            pattern=TradingPattern.OVERTRADING,
            detected=False,
            confidence=0.0,
            details="Insufficient data for analysis"
        )

    first_trade_time = getattr(trades[0], 'purchase_time', datetime.now())
    last_trade_time = getattr(trades[-1], 'purchase_time', datetime.now())

    date_range = (last_trade_time - first_trade_time).days or 1
    trades_per_day = len(trades) / date_range

    # More than 10 trades per day indicates overtrading
    detected = trades_per_day > 10
    confidence = min(trades_per_day / 20, 1.0)

    return PatternDetectionResult(
        pattern=TradingPattern.OVERTRADING,
        detected=detected,
        confidence=confidence,
        details=f"Average {trades_per_day:.1f} trades per day over {date_range} days"
    )


def _detect_consistent_timing(trades: List[Any]) -> PatternDetectionResult:
    """
    Detect consistent trading timing (positive pattern).

    Consistent timing indicates discipline and routine.
    """
    if len(trades) < 5:
        return PatternDetectionResult(
            pattern=TradingPattern.CONSISTENT_TIMING,
            detected=False,
            confidence=0.0,
            details="Insufficient data for analysis (need at least 5 trades)"
        )

    # Extract trading hours
    hours = [getattr(t, 'purchase_time', datetime.now()).hour for t in trades]

    # Calculate standard deviation of trading hours
    if len(set(hours)) == 1:
        std_dev = 0
    else:
        std_dev = statistics.stdev(hours)

    # Low standard deviation indicates consistent timing
    detected = std_dev < 3
    confidence = max(0, 1 - (std_dev / 6))

    return PatternDetectionResult(
        pattern=TradingPattern.CONSISTENT_TIMING,
        detected=detected,
        confidence=round(confidence, 2),
        details=f"Trading hour standard deviation: {std_dev:.1f}. {'Consistent' if detected else 'Variable'} trading times."
    )


def _detect_risk_issues(trades: List[Any]) -> PatternDetectionResult:
    """
    Detect risk management issues.

    Risk issues identified when average loss > 2x average win.
    """
    if len(trades) < 3:
        return PatternDetectionResult(
            pattern=TradingPattern.RISK_ISSUES,
            detected=False,
            confidence=0.0,
            details="Insufficient data for analysis"
        )

    profits = [getattr(t, 'profit_loss', 0) or 0 for t in trades if (getattr(t, 'profit_loss', 0) or 0) > 0]
    losses = [abs(getattr(t, 'profit_loss', 0) or 0) for t in trades if (getattr(t, 'profit_loss', 0) or 0) < 0]

    if not profits or not losses:
        return PatternDetectionResult(
            pattern=TradingPattern.RISK_ISSUES,
            detected=False,
            confidence=0.0,
            details="Need both winning and losing trades for risk analysis"
        )

    avg_profit = statistics.mean(profits)
    avg_loss = statistics.mean(losses)

    # Risk issues if average loss is more than 2x average profit
    ratio = avg_loss / avg_profit if avg_profit > 0 else float('inf')
    detected = ratio > 2

    return PatternDetectionResult(
        pattern=TradingPattern.RISK_ISSUES,
        detected=detected,
        confidence=min((ratio - 1) / 3, 1.0) if ratio > 1 else 0.0,
        details=f"Average loss (${avg_loss:.2f}) is {ratio:.1f}x average profit (${avg_profit:.2f})"
    )


def _get_mock_trades(user_id: int, days: int) -> List[MockTrade]:
    """
    Generate mock trade data for development and testing.

    This function creates realistic mock trade data with various patterns.
    Remove this function when Trade model is implemented.

    Args:
        user_id: The user's ID
        days: Number of days of data to generate

    Returns:
        List of MockTrade objects
    """
    random.seed(user_id * 100 + days)  # Consistent data per user/period

    base_time = datetime.now() - timedelta(days=days)
    mock_trades = []

    symbols = ["EURUSD", "Volatility 75", "BTC/USD", "AAPL", "TSLA"]
    contract_types = ["CALL", "PUT", "MULTIPLIER"]

    # Generate realistic number of trades
    num_trades = random.randint(5, min(days * 5, 50))

    for i in range(num_trades):
        # Randomize trade parameters
        buy_price = random.uniform(100, 1000)
        # Slightly favor profitable trades for realistic data
        is_winner = random.random() < 0.55
        if is_winner:
            profit_pct = random.uniform(0.01, 0.08)
        else:
            profit_pct = random.uniform(-0.10, -0.01)

        sell_price = buy_price * (1 + profit_pct)
        profit_loss = sell_price - buy_price

        purchase_time = base_time + timedelta(
            hours=random.randint(0, days * 24)
        )
        # Add some time for trade duration
        trade_duration = timedelta(hours=random.uniform(0.5, 48))
        sell_time = purchase_time + trade_duration

        mock_trades.append(MockTrade(
            id=i + 1,
            user_id=user_id,
            contract_type=random.choice(contract_types),
            symbol=random.choice(symbols),
            buy_price=round(buy_price, 2),
            sell_price=round(sell_price, 2),
            profit_loss=round(profit_loss, 2),
            purchase_time=purchase_time,
            sell_time=sell_time
        ))

    # Sort by purchase time
    mock_trades.sort(key=lambda t: t.purchase_time)

    return mock_trades


def format_duration(hours: float) -> str:
    """
    Format duration in human-readable format.

    Args:
        hours: Duration in hours

    Returns:
        Formatted string (e.g., "30 minutes", "2.5 hours", "1.2 days")
    """
    if hours < 1:
        return f"{int(hours * 60)} minutes"
    elif hours < 24:
        return f"{hours:.1f} hours"
    else:
        return f"{hours / 24:.1f} days"

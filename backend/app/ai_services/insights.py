"""
Trading Insight Generator Service

Uses Claude API to generate personalized trading insights
based on statistical analysis of user trade data.
"""
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
from datetime import datetime
import json
import logging

from app.config.ai_config import get_ai_settings
from app.ai_services.analysis import (
    get_recent_trades,
    calculate_statistics,
    detect_patterns,
    PatternDetectionResult,
    format_duration
)
from app.prompts.insight_prompts import (
    INSIGHT_SYSTEM_PROMPT,
    INSIGHT_USER_TEMPLATE,
    PATTERN_DESCRIPTIONS,
    FALLBACK_INSIGHTS
)
from app.ai_services.deriv_market import get_market_service

logger = logging.getLogger(__name__)


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


class InsightGenerator:
    """
    Generates personalized trading insights using Claude AI.

    Combines statistical analysis with AI to provide actionable
    feedback on trading performance.
    """

    def __init__(self):
        """Initialize the insight generator with Claude client."""
        self.settings = get_ai_settings()
        self._client = None

    def _get_client(self):
        """Lazy load the Claude client."""
        if self._client is None:
            if not self.settings.is_anthropic_configured():
                logger.warning("Anthropic API key not configured. Using fallback insights.")
                return None
            try:
                import anthropic
                self._client = anthropic.Anthropic(api_key=self.settings.anthropic_api_key)
            except ImportError:
                logger.error("Anthropic package not installed.")
                return None
            except Exception as e:
                logger.error(f"Failed to initialize Anthropic client: {e}")
                return None
        return self._client

    async def generate_insights(
        self,
        db,
        user_id: int,
        days: int = 7,
        user_level: str = "beginner",
        user_context: Optional[Dict[str, Any]] = None
    ) -> InsightResponse:
        """
        Generate trading insights for a user.

        Args:
            db: Database session
            user_id: The user's ID
            days: Number of days to analyze
            user_level: User's skill level
            user_context: Optional user preferences from questionnaire

        Returns:
            InsightResponse with insights and recommendations
        """
        # Fetch and analyze trades
        trades = get_recent_trades(db, user_id, days)

        if not trades:
            return self._empty_response()

        statistics = calculate_statistics(trades)
        patterns = detect_patterns(trades)

        # Format patterns for the prompt
        pattern_text = self._format_patterns(patterns)

        # Calculate average trade duration
        avg_duration = format_duration(statistics["average_trade_duration_hours"])

        # Parse user preferences from context
        if user_context is None:
            user_context = {}

        preferences = {
            "experience_level": user_context.get("experience_level", user_level),
            "trading_style": user_context.get("trading_style", "day_trader"),
            "risk_behavior": user_context.get("risk_behavior", "conservative"),
            "risk_per_trade": user_context.get("risk_per_trade", 2.0),
            "preferred_assets": user_context.get("preferred_assets", [])
        }

        # Fetch market context from Deriv API
        market_context = "Market data not available"
        try:
            market_service = get_market_service()
            market_context = await market_service.get_market_context_safe(
                preferences["preferred_assets"]
            )
        except Exception as e:
            logger.warning(f"Could not fetch market context: {e}")

        # Try to generate AI insight
        client = self._get_client()
        if client:
            try:
                response = await self._call_claude(
                    statistics, pattern_text, avg_duration, days, user_level,
                    preferences, market_context
                )
                return self._parse_response(response, statistics)
            except Exception as e:
                logger.error(f"Error generating AI insights: {e}")

        # Fall back to non-AI insights
        return self._fallback_response(statistics, patterns)

    async def _call_claude(
        self,
        stats: Dict[str, Any],
        pattern_text: str,
        avg_duration: str,
        days: int,
        user_level: str,
        preferences: Dict[str, Any] = None,
        market_context: str = "Market data not available"
    ) -> str:
        """Make API call to Claude."""
        import asyncio

        if preferences is None:
            preferences = {}

        prompt = INSIGHT_USER_TEMPLATE.format(
            # User preferences from questionnaire
            experience_level=preferences.get("experience_level", user_level),
            trading_style=preferences.get("trading_style", "day_trader"),
            risk_behavior=preferences.get("risk_behavior", "conservative"),
            risk_per_trade=preferences.get("risk_per_trade", 2.0),
            preferred_assets=", ".join(preferences.get("preferred_assets", [])) or "various",
            # Trading statistics
            days=days,
            total_trades=stats["total_trades"],
            win_rate=stats["win_rate"],
            total_profit_loss=stats["total_profit_loss"],
            winning_trades=stats["winning_trades"],
            losing_trades=stats["losing_trades"],
            avg_duration=avg_duration,
            top_symbol=stats["most_traded_symbol"],
            top_contract_type=stats["most_traded_contract_type"],
            largest_win=stats["largest_win"],
            largest_loss=stats["largest_loss"],
            # Market and patterns
            market_context=market_context,
            detected_patterns=pattern_text,
            user_level=user_level
        )

        # Add JSON instruction to prompt since Claude doesn't have response_format
        json_prompt = prompt + "\n\nIMPORTANT: Respond with valid JSON only. No other text."

        def _sync_call():
            client = self._get_client()
            response = client.messages.create(
                model=self.settings.anthropic_model_name,
                max_tokens=self.settings.anthropic_max_tokens,
                system=INSIGHT_SYSTEM_PROMPT + "\n\nAlways respond with valid JSON format.",
                messages=[
                    {"role": "user", "content": json_prompt}
                ]
            )
            return response.content[0].text

        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, _sync_call)

    def _format_patterns(self, patterns: List[PatternDetectionResult]) -> str:
        """Format detected patterns for the prompt."""
        lines = []
        for pattern in patterns:
            if pattern.detected:
                description = PATTERN_DESCRIPTIONS.get(
                    pattern.pattern.value,
                    pattern.details
                )
                lines.append(f"- {description} (Confidence: {pattern.confidence:.0%})")

        return "\n".join(lines) if lines else "No significant patterns detected."

    def _parse_response(
        self,
        response: str,
        statistics: Dict[str, Any]
    ) -> InsightResponse:
        """Parse the JSON response from Claude."""
        try:
            data = json.loads(response)

            insights = [
                TradingInsight(
                    type=i.get("type", "observation"),
                    message=i.get("message", ""),
                    priority=i.get("priority", "medium")
                )
                for i in data.get("insights", [])
            ]

            return InsightResponse(
                summary=data.get("summary", "Analysis complete."),
                insights=insights,
                recommendations=data.get("recommendations", []),
                statistics=statistics,
                suggested_lesson=data.get("suggested_lesson", ""),
                generated_at=datetime.now().isoformat()
            )
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse Claude response: {e}")
            return self._fallback_response(statistics, [])

    def _empty_response(self) -> InsightResponse:
        """Return response when no trades exist."""
        return InsightResponse(
            summary="No trading data available for analysis.",
            insights=[
                TradingInsight(
                    type="observation",
                    message="Start trading to receive personalized insights.",
                    priority="low"
                )
            ],
            recommendations=["Log your first trade to begin tracking."],
            statistics={},
            suggested_lesson="Introduction to Trading: Key Concepts"
        )

    def _fallback_response(
        self,
        statistics: Dict[str, Any],
        patterns: List[PatternDetectionResult]
    ) -> InsightResponse:
        """Generate fallback response without AI when API fails."""
        insights = []
        recommendations = []

        # Generate basic insights from statistics
        win_rate = statistics.get("win_rate", 0)
        total_pl = statistics.get("total_profit_loss", 0)

        if win_rate >= 60:
            insights.append(TradingInsight(
                type="strength",
                message=FALLBACK_INSIGHTS["high_win_rate"].format(win_rate=win_rate),
                priority="medium"
            ))
        elif win_rate < 40 and statistics.get("total_trades", 0) >= 5:
            insights.append(TradingInsight(
                type="weakness",
                message=FALLBACK_INSIGHTS["low_win_rate"].format(win_rate=win_rate),
                priority="high"
            ))
            recommendations.append("Review your entry criteria for trades")

        if total_pl > 0:
            insights.append(TradingInsight(
                type="strength",
                message=FALLBACK_INSIGHTS["profitable"],
                priority="medium"
            ))
        elif total_pl < 0 and statistics.get("total_trades", 0) >= 3:
            insights.append(TradingInsight(
                type="observation",
                message=FALLBACK_INSIGHTS["losing"],
                priority="medium"
            ))

        # Add pattern-based insights
        for pattern in patterns:
            if pattern.detected:
                is_negative = "REVENGE" in pattern.pattern.name or "OVER" in pattern.pattern.name or "RISK" in pattern.pattern.name
                insights.append(TradingInsight(
                    type="weakness" if is_negative else "strength",
                    message=pattern.details,
                    priority="high" if pattern.confidence > 0.7 else "medium"
                ))

                if is_negative:
                    if "REVENGE" in pattern.pattern.name:
                        recommendations.append("Take a 15-minute break after any loss before trading again")
                    elif "OVER" in pattern.pattern.name:
                        recommendations.append("Set a maximum number of trades per day and stick to it")
                    elif "RISK" in pattern.pattern.name:
                        recommendations.append("Review your position sizing and stop loss strategy")

        # Determine suggested lesson
        suggested_lesson = "Basic Risk Management: Never Risk More Than You Can Afford"
        for pattern in patterns:
            if pattern.detected and "REVENGE" in pattern.pattern.name:
                suggested_lesson = "Managing Trading Emotions"
                break
            elif pattern.detected and "RISK" in pattern.pattern.name:
                suggested_lesson = "Position Sizing Strategies for Consistent Returns"
                break

        return InsightResponse(
            summary=f"Analyzed {statistics.get('total_trades', 0)} trades with {win_rate:.1f}% win rate.",
            insights=insights,
            recommendations=recommendations or ["Keep tracking your trades for more personalized insights."],
            statistics=statistics,
            suggested_lesson=suggested_lesson
        )


# Factory function for dependency injection
_insight_generator: Optional[InsightGenerator] = None


def get_insight_generator() -> InsightGenerator:
    """Get the singleton InsightGenerator instance."""
    global _insight_generator
    if _insight_generator is None:
        _insight_generator = InsightGenerator()
    return _insight_generator

"""
Trading Insight Generator Service

Uses Claude API to generate personalized trading insights
based on statistical analysis of user trade data.
"""
from typing import Dict, Any, Optional, List
from datetime import datetime
import json

from app.services.ai.llm.insights.typings import InsightResponse, TradingInsight
from app.services.ai.llm.insights.insight_prompts import (
    INSIGHT_SYSTEM_PROMPT,
    INSIGHT_USER_TEMPLATE,
    PATTERN_DESCRIPTIONS
)
from app.services.logger.logger import logger
from app.services.ai.llm.connector import LLMConnector
from app.services.analysis.typings import PatternDetectionResult
from app.database.model import users as UserModels

class InsightGenerator(LLMConnector):
    """
    Generates personalized trading insights using Claude AI.

    Combines statistical analysis with AI to provide actionable
    feedback on trading performance.
    """

    def __init__(self):
        """Initialize the insight generator with Claude client."""
        super().__init__()

    async def generate_insights(
        self,
        user_id: int,
        limit: int = 5,
        user_context: Optional[Dict[str, Any]] = None
    ) -> InsightResponse:
        """
        Generate trading insights for a user.

        Args:
            limit: Number of trades to analyze
            user_level: User's skill level
            user_context: Optional user preferences from questionnaire

        Returns:
            InsightResponse with insights and recommendations
        """
        # Fetch and analyze trades
        trades = await self._deriv_service.get_recent_trades(limit)

        if not trades:
            return self._empty_response()

        statistics = self._analysis_service.calculate_statistics(trades)
        patterns = self._analysis_service.detect_patterns(trades)

        # Format patterns for the prompt
        pattern_text = self._format_patterns(patterns)

        # Calculate average trade duration
        avg_duration = self._analysis_service.format_duration(statistics["average_trade_duration_hours"])

        # Parse user preferences from context
        if user_context is None:
            user_context = {}

        try:
            user = self._db.query(UserModels.User).filter(UserModels.User.id == user_id).first()
            if user:
                db_experience = user.experience_level or "beginner"
                db_trading_style = user.trading_duration or "day trader"
                db_risk_behavior = user.risk_tolerance or "cut loss"
                db_capital_allocation = user.capital_allocation or "low risk"
                db_asset_preference = user.asset_preference or "commodities"
        except Exception as e:
                logger.error(f"Error fetching user profile: {e}")

        preferences = {
            "experience_level": user_context.get("experience_level", db_experience),
            "capital_allocation": user_context.get("capital_allocation", db_capital_allocation),
            "trading_style": user_context.get("trading_style", db_trading_style),
            "risk_behavior": user_context.get("risk_behavior", db_risk_behavior),
            "risk_per_trade": user_context.get("risk_per_trade", 2.0),
            "preferred_assets": user_context.get("preferred_assets", db_asset_preference)
        }

        # Fetch market context from Deriv API
        market_context = "Market data not available"
        try:
            market_context = await self._deriv_service.get_market_context_safe(
                [preferences["preferred_assets"]]
            )
        except Exception as e:
            logger.warning(f"Could not fetch market context: {e}")

        # Try to generate AI insight
        self._client = self._get_client()
        if self._client:
            try:
                response = await self._get_insight_llm(
                    statistics, pattern_text, avg_duration, limit, preferences["experience_level"],
                    preferences, market_context
                )
                return self._parse_response(response, statistics)
            except Exception as e:
                logger.error(f"Error generating AI insights: {e}")

        # Fallback removed - return basic stats response without AI insights
        return InsightResponse(
            summary=f"Analyzed {statistics.get('total_trades', 0)} trades.",
            insights=[],
            recommendations=["AI insights are currently unavailable. Please check configuration."],
            statistics=statistics,
            suggested_lesson=""
        )

    async def _get_insight_llm(
        self,
        stats: Dict[str, Any],
        pattern_text: str,
        avg_duration: str,
        days: int,
        user_level: str,
        preferences: Dict[str, Any] = None,
        market_context: str = "Market data not available"
    ) -> str:
        """Make API call to LLM for insights generation."""
        if preferences is None:
            preferences = {}

        prompt = INSIGHT_USER_TEMPLATE.format(
            # User preferences from questionnaire
            experience_level=preferences.get("experience_level", user_level),
            trading_style=preferences.get("trading_style", "day_trader"),
            capital_allocation=preferences.get("capital_allocation", "low risk"),
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
        
        return await self._call_llm(
            system_prompt=INSIGHT_SYSTEM_PROMPT,
            messages=[
                {"role": "user", "content": json_prompt}
            ],
            max_tokens=1024
        )

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
            return InsightResponse(
                summary="Error parsing AI response.",
                insights=[],
                recommendations=[],
                statistics=statistics,
                suggested_lesson=""
            )

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


# Factory function for dependency injection
_insight_generator: Optional[InsightGenerator] = None
def get_insight_generator() -> InsightGenerator:
    """Get the singleton InsightGenerator instance."""
    global _insight_generator
    if _insight_generator is None:
        _insight_generator = InsightGenerator()
    return _insight_generator

# Example usage:
if __name__ == "__main__":
    import asyncio

    async def main():
        generator = get_insight_generator()
        insights = await generator.generate_insights(
            limit=10,
            user_id=1,
            user_context={}
        )
        print(insights)

    asyncio.run(main())

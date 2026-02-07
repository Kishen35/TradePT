"""
Test Suite for TradePT AI Services

Run with: pytest test_ai_services.py -v
"""
import pytest
from datetime import datetime, timedelta
from unittest.mock import MagicMock, patch
import sys
import os

# Add app to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


# ============ Test Data ============

def create_mock_trade(
    trade_id: int,
    user_id: int = 1,
    profit_loss: float = 10.0,
    symbol: str = "EURUSD",
    contract_type: str = "CALL",
    hours_ago: int = 0
):
    """Create a mock trade object for testing."""
    from dataclasses import dataclass

    @dataclass
    class MockTrade:
        id: int
        user_id: int
        contract_type: str
        symbol: str
        buy_price: float
        sell_price: float
        profit_loss: float
        purchase_time: datetime
        sell_time: datetime

    buy_price = 100.0
    sell_price = buy_price + profit_loss

    return MockTrade(
        id=trade_id,
        user_id=user_id,
        contract_type=contract_type,
        symbol=symbol,
        buy_price=buy_price,
        sell_price=sell_price,
        profit_loss=profit_loss,
        purchase_time=datetime.now() - timedelta(hours=hours_ago),
        sell_time=datetime.now() - timedelta(hours=hours_ago - 1)
    )


# ============ Analysis Tests ============

class TestAnalysis:
    """Tests for the analysis module."""

    def test_calculate_win_rate_empty_list(self):
        """Win rate should be 0 for empty trade list."""
        from app.ai_services.analysis import calculate_win_rate

        result = calculate_win_rate([])
        assert result == 0.0

    def test_calculate_win_rate_all_winners(self):
        """Win rate should be 100% for all winning trades."""
        from app.ai_services.analysis import calculate_win_rate

        trades = [
            create_mock_trade(1, profit_loss=10.0),
            create_mock_trade(2, profit_loss=20.0),
            create_mock_trade(3, profit_loss=5.0),
        ]
        result = calculate_win_rate(trades)
        assert result == 100.0

    def test_calculate_win_rate_all_losers(self):
        """Win rate should be 0% for all losing trades."""
        from app.ai_services.analysis import calculate_win_rate

        trades = [
            create_mock_trade(1, profit_loss=-10.0),
            create_mock_trade(2, profit_loss=-20.0),
        ]
        result = calculate_win_rate(trades)
        assert result == 0.0

    def test_calculate_win_rate_mixed(self):
        """Win rate should be calculated correctly for mixed results."""
        from app.ai_services.analysis import calculate_win_rate

        trades = [
            create_mock_trade(1, profit_loss=10.0),   # Win
            create_mock_trade(2, profit_loss=-5.0),   # Loss
            create_mock_trade(3, profit_loss=15.0),   # Win
            create_mock_trade(4, profit_loss=-8.0),   # Loss
        ]
        result = calculate_win_rate(trades)
        assert result == 50.0

    def test_calculate_statistics_empty(self):
        """Statistics should handle empty trade list."""
        from app.ai_services.analysis import calculate_statistics

        result = calculate_statistics([])
        assert result["total_trades"] == 0
        assert result["win_rate"] == 0.0
        assert result["most_traded_symbol"] == "N/A"

    def test_calculate_statistics_with_trades(self):
        """Statistics should be calculated correctly."""
        from app.ai_services.analysis import calculate_statistics

        trades = [
            create_mock_trade(1, profit_loss=10.0, symbol="EURUSD"),
            create_mock_trade(2, profit_loss=-5.0, symbol="EURUSD"),
            create_mock_trade(3, profit_loss=15.0, symbol="BTC/USD"),
        ]
        result = calculate_statistics(trades)

        assert result["total_trades"] == 3
        assert result["winning_trades"] == 2
        assert result["losing_trades"] == 1
        assert result["most_traded_symbol"] == "EURUSD"

    def test_detect_patterns_empty(self):
        """Pattern detection should handle empty list."""
        from app.ai_services.analysis import detect_patterns

        result = detect_patterns([])
        assert result == []

    def test_detect_patterns_insufficient_data(self):
        """Pattern detection should handle insufficient data."""
        from app.ai_services.analysis import detect_patterns

        trades = [create_mock_trade(1)]
        result = detect_patterns(trades)

        # Should have patterns but none detected due to insufficient data
        for pattern in result:
            assert pattern.detected is False

    def test_format_duration_minutes(self):
        """Duration formatting for minutes."""
        from app.ai_services.analysis import format_duration

        assert format_duration(0.5) == "30 minutes"

    def test_format_duration_hours(self):
        """Duration formatting for hours."""
        from app.ai_services.analysis import format_duration

        assert format_duration(2.5) == "2.5 hours"

    def test_format_duration_days(self):
        """Duration formatting for days."""
        from app.ai_services.analysis import format_duration

        assert format_duration(48) == "2.0 days"


# ============ Embeddings Tests ============

class TestEmbeddings:
    """Tests for the embeddings module."""

    def test_embedding_service_initialization(self):
        """EmbeddingService should initialize correctly."""
        from app.ai_services.embeddings import EmbeddingService

        service = EmbeddingService()
        assert service is not None

    def test_get_embedding_fallback(self):
        """Should return fallback embedding when model unavailable."""
        from app.ai_services.embeddings import EmbeddingService

        service = EmbeddingService()
        # Force fallback
        embedding = service._fallback_embedding("test text")

        assert isinstance(embedding, list)
        assert len(embedding) == 64  # 26 + 1 + 37

    def test_calculate_similarity(self):
        """Similarity calculation should work."""
        from app.ai_services.embeddings import EmbeddingService

        service = EmbeddingService()
        vec1 = [1.0, 0.0, 0.0]
        vec2 = [1.0, 0.0, 0.0]
        vec3 = [0.0, 1.0, 0.0]

        # Same vectors should have similarity 1.0
        assert abs(service._fallback_similarity(vec1, vec2) - 1.0) < 0.01

        # Orthogonal vectors should have similarity 0.0
        assert abs(service._fallback_similarity(vec1, vec3) - 0.0) < 0.01

    def test_find_similar_topics(self):
        """Should find similar topics."""
        from app.ai_services.embeddings import EmbeddingService

        service = EmbeddingService()
        topics = [
            "Risk Management Basics",
            "Trading Psychology",
            "Technical Analysis",
        ]

        result = service.find_similar_topics("managing risk", topics, top_k=2)

        assert len(result) <= 2
        assert all("topic" in r and "relevance_score" in r for r in result)


# ============ Insights Tests ============

class TestInsights:
    """Tests for the insights module."""

    def test_insight_generator_initialization(self):
        """InsightGenerator should initialize correctly."""
        from app.ai_services.insights import InsightGenerator

        generator = InsightGenerator()
        assert generator is not None

    def test_empty_response(self):
        """Should return appropriate response for no trades."""
        from app.ai_services.insights import InsightGenerator

        generator = InsightGenerator()
        result = generator._empty_response()

        assert "No trading data" in result.summary
        assert len(result.insights) > 0

    def test_fallback_response(self):
        """Should generate fallback response."""
        from app.ai_services.insights import InsightGenerator

        generator = InsightGenerator()
        stats = {
            "total_trades": 10,
            "win_rate": 60.0,
            "total_profit_loss": 100.0
        }
        result = generator._fallback_response(stats, [])

        assert result.summary != ""
        assert isinstance(result.insights, list)
        assert isinstance(result.recommendations, list)


# ============ Education Tests ============

class TestEducation:
    """Tests for the education module."""

    def test_education_generator_initialization(self):
        """EducationGenerator should initialize correctly."""
        from app.ai_services.education import EducationGenerator

        generator = EducationGenerator()
        assert generator is not None

    def test_fallback_lesson(self):
        """Should generate fallback lesson."""
        from app.ai_services.education import EducationGenerator

        generator = EducationGenerator()
        result = generator._fallback_lesson("Risk Management", "beginner")

        assert "Risk Management" in result.title
        assert result.skill_level == "beginner"
        assert len(result.sections) > 0

    def test_fallback_topics(self):
        """Should generate fallback topic suggestions."""
        from app.ai_services.education import EducationGenerator

        generator = EducationGenerator()
        result = generator._fallback_topics("beginner", [])

        assert len(result) > 0
        assert all(hasattr(s, 'topic') for s in result)


# ============ Chat Tests ============

class TestChat:
    """Tests for the chat module."""

    def test_chatbot_initialization(self):
        """TradingChatBot should initialize correctly."""
        from app.ai_services.chat import TradingChatBot

        chatbot = TradingChatBot()
        assert chatbot is not None

    def test_session_creation(self):
        """Should create new chat sessions."""
        from app.ai_services.chat import TradingChatBot

        chatbot = TradingChatBot()
        session = chatbot.get_or_create_session(None, user_id=1)

        assert session is not None
        assert session.user_id == 1
        assert session.session_id != ""

    def test_quick_response_greeting(self):
        """Should return quick response for greetings."""
        from app.ai_services.chat import TradingChatBot

        chatbot = TradingChatBot()
        result = chatbot._check_quick_response("Hello")

        assert result is not None
        assert "TradePT AI" in result

    def test_quick_response_capabilities(self):
        """Should return capabilities response."""
        from app.ai_services.chat import TradingChatBot

        chatbot = TradingChatBot()
        result = chatbot._check_quick_response("What can you do?")

        assert result is not None
        assert "help" in result.lower()

    def test_fallback_response_stop_loss(self):
        """Should return relevant fallback for stop loss question."""
        from app.ai_services.chat import TradingChatBot

        chatbot = TradingChatBot()
        result = chatbot._get_fallback_response("What is a stop loss?")

        assert "stop loss" in result.lower()

    def test_session_history(self):
        """Should track session history."""
        from app.ai_services.chat import TradingChatBot

        chatbot = TradingChatBot()
        session = chatbot.get_or_create_session("test-session", user_id=1)
        session.add_message("user", "Hello")
        session.add_message("assistant", "Hi there!")

        history = chatbot.get_session_history("test-session")
        assert len(history) == 2

    def test_clear_session(self):
        """Should clear chat sessions."""
        from app.ai_services.chat import TradingChatBot

        chatbot = TradingChatBot()
        chatbot.get_or_create_session("test-clear", user_id=1)
        result = chatbot.clear_session("test-clear")

        assert result is True
        assert chatbot.clear_session("test-clear") is False


# ============ Integration Tests ============

class TestIntegration:
    """Integration tests for the AI services."""

    def test_full_analysis_flow(self):
        """Test complete analysis flow."""
        from app.ai_services.analysis import (
            calculate_statistics,
            detect_patterns,
            calculate_win_rate
        )

        trades = [
            create_mock_trade(i, profit_loss=10.0 if i % 2 == 0 else -5.0)
            for i in range(10)
        ]

        stats = calculate_statistics(trades)
        patterns = detect_patterns(trades)
        win_rate = calculate_win_rate(trades)

        assert stats["total_trades"] == 10
        assert win_rate == 50.0
        assert len(patterns) > 0


# ============ Run Tests ============

if __name__ == "__main__":
    pytest.main([__file__, "-v"])

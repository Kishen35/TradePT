"""
AI Services Module

Provides AI-powered trading analysis, insights, education, and chat services.

Components:
- analysis: Statistical analysis and pattern detection for trade data
- insights: AI-generated trading insights using Groq API
- education: Personalized educational content using Anthropic Claude
- chat: Conversational trading assistant
- embeddings: Semantic search using sentence-transformers
"""
from .analysis import (
    get_recent_trades,
    calculate_win_rate,
    calculate_statistics,
    detect_patterns,
    TradingPattern,
    PatternDetectionResult,
    format_duration
)
from .insights import (
    get_insight_generator,
    InsightGenerator,
    InsightResponse,
    TradingInsight
)
from .education import (
    get_education_generator,
    EducationGenerator,
    GeneratedLesson,
    TopicSuggestion,
    LessonSection,
    QuizQuestion
)
from .chat import (
    get_chatbot,
    TradingChatBot,
    ChatSession,
    ChatMessage
)
from .embeddings import (
    get_embedding_service,
    EmbeddingService
)
from .deriv_market import (
    get_market_service,
    DerivMarketService,
    MarketSnapshot,
    AccountInfo
)

__all__ = [
    # Analysis
    "get_recent_trades",
    "calculate_win_rate",
    "calculate_statistics",
    "detect_patterns",
    "TradingPattern",
    "PatternDetectionResult",
    "format_duration",
    # Insights
    "get_insight_generator",
    "InsightGenerator",
    "InsightResponse",
    "TradingInsight",
    # Education
    "get_education_generator",
    "EducationGenerator",
    "GeneratedLesson",
    "TopicSuggestion",
    "LessonSection",
    "QuizQuestion",
    # Chat
    "get_chatbot",
    "TradingChatBot",
    "ChatSession",
    "ChatMessage",
    # Embeddings
    "get_embedding_service",
    "EmbeddingService",
    # Deriv Market Data
    "get_market_service",
    "DerivMarketService",
    "MarketSnapshot",
    "AccountInfo",
]

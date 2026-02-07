"""
AI Insights API Router

Provides endpoints for:
- Trading insights generation
- Educational lesson generation
- Chat with trading assistant
- Topic suggestions based on user patterns
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
import uuid
import logging

from app.config.db import get_db
from app.ai_services.insights import get_insight_generator
from app.ai_services.education import get_education_generator
from app.ai_services.chat import get_chatbot
from app.ai_services.analysis import (
    get_recent_trades,
    calculate_statistics,
    detect_patterns
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/ai", tags=["AI Services"])


# ============ Request/Response Models ============

class InsightItem(BaseModel):
    """A single insight."""
    type: str = Field(..., description="Type: strength, weakness, or observation")
    message: str = Field(..., description="The insight message")
    priority: str = Field(..., description="Priority: high, medium, or low")


class InsightsResponse(BaseModel):
    """Response model for trading insights."""
    summary: str = Field(..., description="Overall summary")
    insights: List[InsightItem] = Field(default_factory=list, description="List of insights")
    recommendations: List[str] = Field(default_factory=list, description="Actionable recommendations")
    statistics: dict = Field(default_factory=dict, description="Trading statistics")
    suggested_lesson: str = Field(default="", description="Suggested next lesson topic")
    generated_at: str = Field(..., description="Timestamp of generation")


class LessonRequest(BaseModel):
    """Request model for lesson generation."""
    topic: str = Field(..., min_length=3, max_length=200, description="Lesson topic")
    skill_level: str = Field(
        default="beginner",
        pattern="^(beginner|intermediate|advanced)$",
        description="User's skill level"
    )
    instruments: List[str] = Field(default_factory=list, description="Trading instruments")
    weakness: Optional[str] = Field(None, description="Identified weakness to address")
    performance_summary: Optional[str] = Field(None, description="Recent performance summary")
    length: str = Field(
        default="medium",
        pattern="^(short|medium|long)$",
        description="Desired lesson length"
    )
    include_examples: bool = Field(default=True, description="Include practical examples")


class LessonSection(BaseModel):
    """A lesson section."""
    heading: str
    content: str
    type: str


class QuizQuestion(BaseModel):
    """A quiz question."""
    question: str
    options: List[str]
    correct: str
    explanation: str


class LessonResponse(BaseModel):
    """Response model for generated lessons."""
    title: str
    skill_level: str
    estimated_time_minutes: int
    sections: List[LessonSection]
    quiz: List[QuizQuestion]
    key_takeaways: List[str]


class ChatRequest(BaseModel):
    """Request model for chat messages."""
    user_id: int = Field(..., description="User ID")
    message: str = Field(..., min_length=1, max_length=2000, description="User's message")
    session_id: Optional[str] = Field(None, description="Session ID for conversation continuity")
    user_context: Optional[dict] = Field(None, description="Optional user context")


class ChatResponse(BaseModel):
    """Response model for chat."""
    session_id: str = Field(..., description="Session ID")
    response: str = Field(..., description="Assistant's response")


class TopicSuggestion(BaseModel):
    """A suggested topic."""
    topic: str
    relevance_score: float
    reason: str


class TopicSuggestionResponse(BaseModel):
    """Response model for topic suggestions."""
    topics: List[TopicSuggestion]


# ============ Endpoints ============

@router.get("/insights/{user_id}", response_model=InsightsResponse)
async def get_trading_insights(
    user_id: int,
    days: int = Query(default=7, ge=1, le=90, description="Days to analyze"),
    user_level: str = Query(default="beginner", pattern="^(beginner|intermediate|advanced)$"),
    db: Session = Depends(get_db)
):
    """
    Generate trading insights for a user.

    Analyzes the user's recent trades and provides personalized
    insights, pattern detection, and recommendations.

    - **user_id**: The user's ID
    - **days**: Number of days to analyze (1-90)
    - **user_level**: User's skill level

    Returns insights including:
    - Summary of trading performance
    - Detected patterns (revenge trading, overtrading, etc.)
    - Personalized recommendations
    - Suggested educational topics
    """
    try:
        generator = get_insight_generator()
        result = await generator.generate_insights(db, user_id, days, user_level)

        return InsightsResponse(
            summary=result.summary,
            insights=[
                InsightItem(
                    type=i.type,
                    message=i.message,
                    priority=i.priority
                )
                for i in result.insights
            ],
            recommendations=result.recommendations,
            statistics=result.statistics,
            suggested_lesson=result.suggested_lesson,
            generated_at=result.generated_at
        )
    except Exception as e:
        logger.error(f"Error generating insights for user {user_id}: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error generating insights: {str(e)}"
        )


@router.post("/lesson/generate", response_model=LessonResponse)
async def generate_lesson(request: LessonRequest):
    """
    Generate a personalized trading lesson.

    Creates educational content tailored to the user's skill level,
    trading instruments, and identified weaknesses.

    Request body:
    - **topic**: The lesson topic (e.g., "Risk Management Basics")
    - **skill_level**: beginner, intermediate, or advanced
    - **instruments**: List of trading instruments (optional)
    - **weakness**: Identified weakness to address (optional)
    - **length**: short, medium, or long
    - **include_examples**: Whether to include practical examples

    Returns a complete lesson with sections, quiz, and key takeaways.
    """
    try:
        generator = get_education_generator()
        result = await generator.generate_lesson(
            topic=request.topic,
            skill_level=request.skill_level,
            instruments=request.instruments,
            weakness=request.weakness,
            performance_summary=request.performance_summary,
            length=request.length,
            include_examples=request.include_examples
        )

        return LessonResponse(
            title=result.title,
            skill_level=result.skill_level,
            estimated_time_minutes=result.estimated_time_minutes,
            sections=[
                LessonSection(
                    heading=s.heading,
                    content=s.content,
                    type=s.type
                )
                for s in result.sections
            ],
            quiz=[
                QuizQuestion(
                    question=q.question,
                    options=q.options,
                    correct=q.correct,
                    explanation=q.explanation
                )
                for q in result.quiz
            ],
            key_takeaways=result.key_takeaways
        )
    except Exception as e:
        logger.error(f"Error generating lesson: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error generating lesson: {str(e)}"
        )


@router.post("/chat", response_model=ChatResponse)
async def chat_with_assistant(request: ChatRequest):
    """
    Chat with the trading assistant.

    Provides conversational help with trading concepts, strategies,
    and education. Maintains conversation history within sessions.

    Request body:
    - **user_id**: The user's ID
    - **message**: User's message (1-2000 characters)
    - **session_id**: Optional session ID for conversation continuity
    - **user_context**: Optional context about the user

    Returns the assistant's response and session ID.
    """
    try:
        chatbot = get_chatbot()

        response, session_id = await chatbot.chat(
            session_id=request.session_id,
            user_id=request.user_id,
            message=request.message,
            user_context=request.user_context
        )

        return ChatResponse(
            session_id=session_id,
            response=response
        )
    except Exception as e:
        logger.error(f"Error in chat: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error in chat: {str(e)}"
        )


@router.get("/suggest-topic/{user_id}", response_model=TopicSuggestionResponse)
async def suggest_topics(
    user_id: int,
    skill_level: str = Query(
        default="beginner",
        pattern="^(beginner|intermediate|advanced)$",
        description="User's skill level"
    ),
    db: Session = Depends(get_db)
):
    """
    Suggest educational topics for a user.

    Analyzes the user's trading patterns and performance to suggest
    relevant educational content.

    - **user_id**: The user's ID
    - **skill_level**: User's skill level

    Returns ranked topic suggestions with relevance scores.
    """
    try:
        # Get user's trading patterns for context
        trades = get_recent_trades(db, user_id, days=30)
        stats = calculate_statistics(trades)
        patterns = detect_patterns(trades)

        # Extract detected pattern names
        pattern_names = [p.pattern.value for p in patterns if p.detected]

        generator = get_education_generator()
        suggestions = await generator.suggest_topics(
            skill_level=skill_level,
            instruments=[stats.get("most_traded_symbol", "general")],
            win_rate=stats.get("win_rate", 50),
            patterns=pattern_names,
            completed_lessons=[]  # TODO: Get from user profile when available
        )

        return TopicSuggestionResponse(
            topics=[
                TopicSuggestion(
                    topic=s.topic,
                    relevance_score=s.relevance_score,
                    reason=s.reason
                )
                for s in suggestions
            ]
        )
    except Exception as e:
        logger.error(f"Error suggesting topics for user {user_id}: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error suggesting topics: {str(e)}"
        )


@router.delete("/chat/session/{session_id}")
async def clear_chat_session(session_id: str):
    """
    Clear a chat session.

    Removes the conversation history for a session.

    - **session_id**: The session ID to clear

    Returns success message or 404 if session not found.
    """
    chatbot = get_chatbot()
    cleared = chatbot.clear_session(session_id)

    if cleared:
        return {"message": "Session cleared successfully", "session_id": session_id}
    else:
        raise HTTPException(status_code=404, detail="Session not found")


@router.get("/chat/history/{session_id}")
async def get_chat_history(session_id: str):
    """
    Get chat history for a session.

    - **session_id**: The session ID

    Returns list of messages in the session.
    """
    chatbot = get_chatbot()
    history = chatbot.get_session_history(session_id)

    if history:
        return {"session_id": session_id, "messages": history}
    else:
        raise HTTPException(status_code=404, detail="Session not found or empty")


@router.get("/health")
async def health_check():
    """
    Check AI services health status.

    Returns status of each AI service component.
    """
    from app.config.ai_config import get_ai_settings

    settings = get_ai_settings()

    return {
        "status": "ok",
        "services": {
            "groq_configured": settings.is_groq_configured(),
            "anthropic_configured": settings.is_anthropic_configured(),
            "embedding_model": settings.embedding_model_name
        }
    }

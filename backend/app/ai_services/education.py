"""
Educational Content Generator Service

Uses Anthropic Claude API to generate personalized trading lessons
based on user skill level, trading patterns, and identified weaknesses.
"""
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
from datetime import datetime
import json
import logging

from app.config.ai_config import get_ai_settings
from app.ai_services.embeddings import get_embedding_service
from app.prompts.education_prompts import (
    EDUCATION_SYSTEM_PROMPT,
    LESSON_GENERATION_TEMPLATE,
    TOPIC_SUGGESTION_TEMPLATE,
    SKILL_LEVELS,
    LESSON_TOPICS
)

logger = logging.getLogger(__name__)


@dataclass
class LessonSection:
    """A section within a lesson."""
    heading: str
    content: str
    type: str  # "text", "example", "warning", "tip"


@dataclass
class QuizQuestion:
    """A quiz question."""
    question: str
    options: List[str]
    correct: str
    explanation: str


@dataclass
class GeneratedLesson:
    """A complete generated lesson."""
    title: str
    skill_level: str
    estimated_time_minutes: int
    sections: List[LessonSection]
    quiz: List[QuizQuestion]
    key_takeaways: List[str]
    next_topics: List[str] = field(default_factory=list)


@dataclass
class TopicSuggestion:
    """A suggested lesson topic."""
    topic: str
    relevance_score: float
    reason: str
    difficulty: str = "beginner"
    estimated_duration_minutes: int = 15


class EducationGenerator:
    """
    Generates personalized educational content using Anthropic Claude.

    Creates custom lessons tailored to the user's skill level,
    trading instruments, and identified weaknesses.
    """

    def __init__(self):
        """Initialize the education generator with Anthropic client."""
        self.settings = get_ai_settings()
        self._client = None
        self.embedding_service = get_embedding_service()

    def _get_client(self):
        """Lazy load the Anthropic client."""
        if self._client is None:
            if not self.settings.is_anthropic_configured():
                logger.warning("Anthropic API key not configured. Using fallback lessons.")
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

    async def generate_lesson(
        self,
        topic: str,
        skill_level: str = "beginner",
        instruments: Optional[List[str]] = None,
        weakness: Optional[str] = None,
        performance_summary: Optional[str] = None,
        length: str = "medium",
        include_examples: bool = True
    ) -> GeneratedLesson:
        """
        Generate a personalized lesson.

        Args:
            topic: The lesson topic
            skill_level: User's skill level (beginner/intermediate/advanced)
            instruments: User's primary trading instruments
            weakness: Identified weakness to address
            performance_summary: Summary of recent performance
            length: Desired length (short/medium/long)
            include_examples: Whether to include practical examples

        Returns:
            GeneratedLesson with full content
        """
        # Validate skill level
        if skill_level not in SKILL_LEVELS:
            skill_level = "beginner"

        instruments = instruments or ["general"]
        weakness = weakness or "general improvement"
        performance_summary = performance_summary or "No recent data available"

        client = self._get_client()
        if client:
            try:
                response = await self._call_anthropic_lesson(
                    topic, skill_level, instruments, weakness,
                    performance_summary, length, include_examples
                )
                return self._parse_lesson_response(response, skill_level)
            except Exception as e:
                logger.error(f"Error generating lesson: {e}")

        return self._fallback_lesson(topic, skill_level)

    async def suggest_topics(
        self,
        skill_level: str,
        instruments: List[str],
        win_rate: float,
        patterns: List[str],
        completed_lessons: Optional[List[str]] = None
    ) -> List[TopicSuggestion]:
        """
        Suggest relevant lesson topics based on user profile.

        Args:
            skill_level: User's skill level
            instruments: Trading instruments
            win_rate: User's win rate
            patterns: Detected trading patterns
            completed_lessons: Previously completed lesson IDs

        Returns:
            List of suggested topics ranked by relevance
        """
        completed_lessons = completed_lessons or []

        client = self._get_client()
        if client:
            try:
                response = await self._call_anthropic_topics(
                    skill_level, instruments, win_rate, patterns, completed_lessons
                )
                return self._parse_topics_response(response)
            except Exception as e:
                logger.error(f"Error suggesting topics: {e}")

        return self._fallback_topics(skill_level, patterns)

    async def _call_anthropic_lesson(
        self,
        topic: str,
        skill_level: str,
        instruments: List[str],
        weakness: str,
        performance_summary: str,
        length: str,
        include_examples: bool
    ) -> str:
        """Make API call to Anthropic Claude for lesson generation."""
        import asyncio

        prompt = LESSON_GENERATION_TEMPLATE.format(
            skill_level=skill_level,
            instruments=", ".join(instruments),
            weakness=weakness,
            performance_summary=performance_summary,
            topic=topic,
            length=length,
            include_examples=str(include_examples).lower()
        )

        def _sync_call():
            client = self._get_client()
            response = client.messages.create(
                model=self.settings.anthropic_model_name,
                max_tokens=self.settings.anthropic_max_tokens,
                system=EDUCATION_SYSTEM_PROMPT,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            return response.content[0].text

        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, _sync_call)

    async def _call_anthropic_topics(
        self,
        skill_level: str,
        instruments: List[str],
        win_rate: float,
        patterns: List[str],
        completed_lessons: List[str]
    ) -> str:
        """Make API call to Anthropic Claude for topic suggestions."""
        import asyncio

        prompt = TOPIC_SUGGESTION_TEMPLATE.format(
            skill_level=skill_level,
            instruments=", ".join(instruments) if instruments else "various",
            win_rate=win_rate,
            patterns=", ".join(patterns) if patterns else "none detected",
            completed_lessons=", ".join(completed_lessons) if completed_lessons else "none"
        )

        def _sync_call():
            client = self._get_client()
            response = client.messages.create(
                model=self.settings.anthropic_model_name,
                max_tokens=1024,
                system=EDUCATION_SYSTEM_PROMPT,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            return response.content[0].text

        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, _sync_call)

    def _parse_lesson_response(self, response: str, skill_level: str) -> GeneratedLesson:
        """Parse the JSON lesson response from Claude."""
        try:
            # Extract JSON from response (Claude might include markdown)
            json_start = response.find("{")
            json_end = response.rfind("}") + 1
            if json_start == -1 or json_end == 0:
                raise ValueError("No JSON found in response")

            json_str = response[json_start:json_end]
            data = json.loads(json_str)

            sections = [
                LessonSection(
                    heading=s.get("heading", ""),
                    content=s.get("content", ""),
                    type=s.get("type", "text")
                )
                for s in data.get("sections", [])
            ]

            quiz = [
                QuizQuestion(
                    question=q.get("question", ""),
                    options=q.get("options", []),
                    correct=q.get("correct", ""),
                    explanation=q.get("explanation", "")
                )
                for q in data.get("quiz", [])
            ]

            return GeneratedLesson(
                title=data.get("title", "Trading Lesson"),
                skill_level=data.get("skill_level", skill_level),
                estimated_time_minutes=data.get("estimated_time_minutes", 15),
                sections=sections,
                quiz=quiz,
                key_takeaways=data.get("key_takeaways", []),
                next_topics=data.get("next_topics", [])
            )
        except (json.JSONDecodeError, KeyError, ValueError) as e:
            logger.error(f"Failed to parse lesson response: {e}")
            raise

    def _parse_topics_response(self, response: str) -> List[TopicSuggestion]:
        """Parse the JSON topics response from Claude."""
        try:
            json_start = response.find("{")
            json_end = response.rfind("}") + 1
            if json_start == -1 or json_end == 0:
                raise ValueError("No JSON found in response")

            json_str = response[json_start:json_end]
            data = json.loads(json_str)

            return [
                TopicSuggestion(
                    topic=t.get("topic", ""),
                    relevance_score=t.get("relevance_score", 0.5),
                    reason=t.get("reason", ""),
                    difficulty=t.get("difficulty", "beginner"),
                    estimated_duration_minutes=t.get("estimated_duration_minutes", 15)
                )
                for t in data.get("suggested_topics", [])
            ]
        except (json.JSONDecodeError, KeyError, ValueError) as e:
            logger.error(f"Failed to parse topics response: {e}")
            return []

    def _fallback_lesson(self, topic: str, skill_level: str) -> GeneratedLesson:
        """Generate a fallback lesson when API fails."""
        return GeneratedLesson(
            title=f"Introduction to {topic}",
            skill_level=skill_level,
            estimated_time_minutes=10,
            sections=[
                LessonSection(
                    heading="Overview",
                    content=f"This lesson covers the fundamentals of {topic}. "
                            "The full personalized lesson will be available shortly. "
                            "In the meantime, here are some key points to consider.",
                    type="text"
                ),
                LessonSection(
                    heading="Key Concept",
                    content=f"Understanding {topic} is essential for improving your trading. "
                            "Take time to research and practice these concepts.",
                    type="text"
                ),
                LessonSection(
                    heading="Practice Tip",
                    content="Start with paper trading to apply these concepts without risking real money.",
                    type="tip"
                )
            ],
            quiz=[],
            key_takeaways=[
                "Learning is a continuous process in trading",
                "Practice in a risk-free environment first",
                "Keep a trading journal to track your progress"
            ],
            next_topics=LESSON_TOPICS.get(skill_level, LESSON_TOPICS["beginner"])[:3]
        )

    def _fallback_topics(
        self,
        skill_level: str,
        patterns: List[str]
    ) -> List[TopicSuggestion]:
        """Generate fallback topic suggestions."""
        topics = LESSON_TOPICS.get(skill_level, LESSON_TOPICS["beginner"])

        # Prioritize based on detected patterns
        prioritized = []

        # Check for pattern-specific topics
        pattern_topics = {
            "revenge_trading": "Managing Trading Emotions",
            "overtrading": "Building a Complete Trading Plan",
            "risk_issues": "Position Sizing Strategies for Consistent Returns",
            "loss_chasing": "Basic Risk Management: Never Risk More Than You Can Afford"
        }

        for pattern in patterns:
            pattern_lower = pattern.lower()
            for key, topic in pattern_topics.items():
                if key in pattern_lower and topic in topics:
                    prioritized.append(TopicSuggestion(
                        topic=topic,
                        relevance_score=0.95,
                        reason=f"Recommended based on detected {pattern} pattern",
                        difficulty=skill_level,
                        estimated_duration_minutes=15
                    ))

        # Add remaining topics
        for i, topic in enumerate(topics[:5]):
            if topic not in [p.topic for p in prioritized]:
                prioritized.append(TopicSuggestion(
                    topic=topic,
                    relevance_score=0.8 - (i * 0.1),
                    reason=f"Standard recommendation for {skill_level} level",
                    difficulty=skill_level,
                    estimated_duration_minutes=15
                ))

        return prioritized[:5]


# Factory function for dependency injection
_education_generator: Optional[EducationGenerator] = None


def get_education_generator() -> EducationGenerator:
    """Get the singleton EducationGenerator instance."""
    global _education_generator
    if _education_generator is None:
        _education_generator = EducationGenerator()
    return _education_generator

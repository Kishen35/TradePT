
from dataclasses import dataclass, field
from typing import List

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
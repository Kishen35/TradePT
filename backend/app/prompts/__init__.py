"""
Prompt Templates Module

Contains all prompt templates for AI services:
- insight_prompts: Templates for trading insight generation
- education_prompts: Templates for educational content
- chat_prompts: Templates for chat interactions
"""
from app.prompts.insight_prompts import (
    INSIGHT_SYSTEM_PROMPT,
    INSIGHT_USER_TEMPLATE,
    PATTERN_DESCRIPTIONS
)
from app.prompts.education_prompts import (
    EDUCATION_SYSTEM_PROMPT,
    LESSON_GENERATION_TEMPLATE,
    TOPIC_SUGGESTION_TEMPLATE,
    SKILL_LEVELS,
    LESSON_TOPICS
)
from app.prompts.chat_prompts import (
    CHAT_SYSTEM_PROMPT,
    CHAT_WITH_HISTORY_TEMPLATE,
    CONTEXT_BUILDING_TEMPLATE,
    QUICK_RESPONSES
)

__all__ = [
    "INSIGHT_SYSTEM_PROMPT",
    "INSIGHT_USER_TEMPLATE",
    "PATTERN_DESCRIPTIONS",
    "EDUCATION_SYSTEM_PROMPT",
    "LESSON_GENERATION_TEMPLATE",
    "TOPIC_SUGGESTION_TEMPLATE",
    "SKILL_LEVELS",
    "LESSON_TOPICS",
    "CHAT_SYSTEM_PROMPT",
    "CHAT_WITH_HISTORY_TEMPLATE",
    "CONTEXT_BUILDING_TEMPLATE",
    "QUICK_RESPONSES",
]

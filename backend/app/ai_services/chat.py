"""
Trading Chatbot Service

Uses Anthropic Claude API to provide conversational trading assistance.
Maintains conversation history and context for coherent multi-turn dialogues.
"""
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
from datetime import datetime
import uuid
import logging

from app.config.ai_config import get_ai_settings
from app.prompts.chat_prompts import (
    CHAT_SYSTEM_PROMPT,
    CHAT_WITH_HISTORY_TEMPLATE,
    CONTEXT_BUILDING_TEMPLATE,
    QUICK_RESPONSES
)
from app.ai_services.deriv_market import get_market_service

logger = logging.getLogger(__name__)


@dataclass
class ChatMessage:
    """A single chat message."""
    role: str  # "user" or "assistant"
    content: str
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class ChatSession:
    """A chat session with history."""
    session_id: str
    user_id: int
    messages: List[ChatMessage] = field(default_factory=list)
    user_context: str = ""
    created_at: datetime = field(default_factory=datetime.now)

    def add_message(self, role: str, content: str) -> None:
        """Add a message to the session."""
        self.messages.append(ChatMessage(role=role, content=content))

    def get_history_text(self, max_messages: int = 10) -> str:
        """Get formatted conversation history."""
        recent = self.messages[-max_messages:]
        return "\n".join(
            f"{m.role.capitalize()}: {m.content}"
            for m in recent
        )

    def get_messages_for_api(self, max_messages: int = 10) -> List[Dict[str, str]]:
        """Get messages formatted for API call."""
        recent = self.messages[-max_messages:]
        return [{"role": m.role, "content": m.content} for m in recent]


class TradingChatBot:
    """
    AI-powered trading assistant chatbot.

    Provides conversational help with trading concepts, strategies,
    and education while maintaining context from previous messages.
    """

    def __init__(self):
        """Initialize the chatbot with Anthropic client."""
        self.settings = get_ai_settings()
        self._client = None
        self._sessions: Dict[str, ChatSession] = {}

    def _get_client(self):
        """Lazy load the Anthropic client."""
        if self._client is None:
            if not self.settings.is_anthropic_configured():
                logger.warning("Anthropic API key not configured. Using fallback responses.")
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

    def get_or_create_session(
        self,
        session_id: Optional[str],
        user_id: int,
        user_context: Optional[Dict[str, Any]] = None
    ) -> ChatSession:
        """
        Get an existing session or create a new one.

        Args:
            session_id: Unique session identifier (None to create new)
            user_id: The user's ID
            user_context: Optional user context for personalization

        Returns:
            ChatSession instance
        """
        if session_id and session_id in self._sessions:
            return self._sessions[session_id]

        # Create new session
        new_session_id = session_id or str(uuid.uuid4())

        context_str = ""
        if user_context:
            # Parse questionnaire preferences
            experience_level = user_context.get("experience_level", "beginner")
            trading_style = user_context.get("trading_style", "day_trader")
            risk_behavior = user_context.get("risk_behavior", "conservative")
            risk_per_trade = user_context.get("risk_per_trade", 2.0)
            preferred_assets = user_context.get("preferred_assets", [])

            # Parse performance data
            skill_level = user_context.get("skill_level", experience_level)
            instruments = user_context.get("instruments", preferred_assets)
            trend = user_context.get("trend", "unknown")
            win_rate = user_context.get("win_rate", "unknown")
            patterns = user_context.get("patterns", [])

            # Market context placeholder (will be populated by deriv_market service)
            market_context = user_context.get("market_context", "Market data not available")

            context_str = CONTEXT_BUILDING_TEMPLATE.format(
                # Questionnaire preferences
                experience_level=experience_level,
                trading_style=trading_style,
                risk_behavior=risk_behavior,
                risk_per_trade=risk_per_trade,
                preferred_assets=", ".join(preferred_assets) if preferred_assets else "various",
                # Performance data
                skill_level=skill_level,
                instruments=", ".join(instruments) if isinstance(instruments, list) else instruments or "various",
                trend=trend,
                win_rate=win_rate,
                patterns=", ".join(patterns) if patterns else "none detected",
                # Market context
                market_context=market_context
            )

        session = ChatSession(
            session_id=new_session_id,
            user_id=user_id,
            user_context=context_str
        )
        self._sessions[new_session_id] = session
        return session

    async def chat(
        self,
        session_id: Optional[str],
        user_id: int,
        message: str,
        user_context: Optional[Dict[str, Any]] = None
    ) -> tuple[str, str]:
        """
        Process a chat message and generate a response.

        Args:
            session_id: Session identifier for conversation continuity
            user_id: The user's ID
            message: The user's message
            user_context: Optional context about the user

        Returns:
            Tuple of (response, session_id)
        """
        # Fetch market context from Deriv API
        if user_context is None:
            user_context = {}

        if "market_context" not in user_context:
            try:
                market_service = get_market_service()
                preferred_assets = user_context.get("preferred_assets", [])
                market_context = await market_service.get_market_context_safe(preferred_assets)
                user_context["market_context"] = market_context
            except Exception as e:
                logger.warning(f"Could not fetch market context: {e}")
                user_context["market_context"] = "Market data temporarily unavailable"

        # Get or create session
        session = self.get_or_create_session(session_id, user_id, user_context)

        # Add user message to history
        session.add_message("user", message)

        # Check for quick responses (greetings, etc.)
        quick_response = self._check_quick_response(message)
        if quick_response:
            session.add_message("assistant", quick_response)
            return quick_response, session.session_id

        # Build system prompt with user context
        system_prompt = CHAT_SYSTEM_PROMPT.format(
            user_context=session.user_context or "No specific context available."
        )

        # Try to get AI response
        client = self._get_client()
        if client:
            try:
                response = await self._call_anthropic(
                    system_prompt=system_prompt,
                    messages=session.get_messages_for_api()
                )
                session.add_message("assistant", response)
                return response, session.session_id
            except Exception as e:
                logger.error(f"Error in chat: {e}")

        # Fallback response
        fallback = self._get_fallback_response(message)
        session.add_message("assistant", fallback)
        return fallback, session.session_id

    async def _call_anthropic(
        self,
        system_prompt: str,
        messages: List[Dict[str, str]]
    ) -> str:
        """Make API call to Anthropic Claude."""
        import asyncio

        def _sync_call():
            client = self._get_client()
            response = client.messages.create(
                model=self.settings.anthropic_model_name,
                max_tokens=1024,
                system=system_prompt,
                messages=messages
            )
            return response.content[0].text

        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, _sync_call)

    def _check_quick_response(self, message: str) -> Optional[str]:
        """Check if message matches a quick response pattern."""
        message_lower = message.lower().strip()

        # Greetings
        greetings = ["hi", "hello", "hey", "good morning", "good afternoon", "good evening", "howdy"]
        if any(message_lower == g or message_lower.startswith(g + " ") or message_lower.startswith(g + ",") for g in greetings):
            return QUICK_RESPONSES["greeting"]

        # Capability questions
        capability_keywords = ["what can you do", "help me", "how can you help", "your capabilities", "what are you"]
        if any(kw in message_lower for kw in capability_keywords):
            return QUICK_RESPONSES["capabilities"]

        # Goodbye
        goodbye_keywords = ["bye", "goodbye", "see you", "thanks bye", "thank you bye"]
        if any(kw in message_lower for kw in goodbye_keywords):
            return QUICK_RESPONSES["goodbye"]

        # Off-topic questions (weather, sports, entertainment, etc.)
        off_topic_keywords = [
            "weather", "sports", "movie", "music", "food", "recipe",
            "joke", "game", "celebrity", "politics", "news", "netflix",
            "football", "basketball", "soccer", "concert", "party",
            "restaurant", "travel", "vacation", "holiday"
        ]
        if any(kw in message_lower for kw in off_topic_keywords):
            return QUICK_RESPONSES["off_topic"]

        return None

    def _get_fallback_response(self, message: str) -> str:
        """Generate a fallback response when AI is unavailable."""
        message_lower = message.lower()

        # Try to match common trading questions
        if "stop loss" in message_lower:
            return ("A stop loss is an order to close your position at a predetermined price level "
                    "to limit potential losses. It's a crucial risk management tool that every trader should use.")

        if "position size" in message_lower or "lot size" in message_lower:
            return ("Position sizing determines how much of your capital to risk on each trade. "
                    "A common rule is to never risk more than 1-2% of your account on a single trade.")

        if "revenge trading" in message_lower:
            return ("Revenge trading is making impulsive trades to recover losses quickly. "
                    "It's dangerous because it bypasses your trading plan. Take a break after losses instead.")

        if "win rate" in message_lower:
            return ("Win rate is the percentage of your trades that are profitable. "
                    "While important, it should be balanced with your risk-reward ratio. "
                    "You can be profitable with a 40% win rate if your winners are larger than your losers.")

        if "risk" in message_lower and "reward" in message_lower:
            return ("Risk-reward ratio compares potential loss to potential gain. "
                    "A 1:2 ratio means risking $1 to potentially make $2. "
                    "Most successful traders aim for at least 1:2 or better.")

        # Generic fallback
        return ("I'm here to help with trading questions. I can explain concepts like risk management, "
                "trading psychology, technical analysis, and more. What would you like to know?")

    def clear_session(self, session_id: str) -> bool:
        """
        Clear a chat session.

        Args:
            session_id: The session to clear

        Returns:
            True if session was cleared, False if not found
        """
        if session_id in self._sessions:
            del self._sessions[session_id]
            return True
        return False

    def get_session_history(self, session_id: str) -> List[Dict[str, Any]]:
        """
        Get the message history for a session.

        Args:
            session_id: The session identifier

        Returns:
            List of message dictionaries
        """
        session = self._sessions.get(session_id)
        if session:
            return [
                {
                    "role": m.role,
                    "content": m.content,
                    "timestamp": m.timestamp.isoformat()
                }
                for m in session.messages
            ]
        return []


# Singleton instance
_chatbot: Optional[TradingChatBot] = None


def get_chatbot() -> TradingChatBot:
    """Get the singleton chatbot instance."""
    global _chatbot
    if _chatbot is None:
        _chatbot = TradingChatBot()
    return _chatbot

"""
Trading Chatbot Service

Uses Anthropic Claude API to provide conversational trading assistance.
Maintains conversation history and context for coherent multi-turn dialogues.
"""
from typing import Dict, List
from app.services.analysis.analysis import get_analysis_service
from app.services.deriv.deriv import get_deriv_service
from app.services.logger.logger import logger
from app.config.ai import get_ai_settings
from app.config.db import get_db
import anthropic
import asyncio

class LLMConnector:
    """
    Connector for interacting with the Anthropic Claude LLM.
    """

    def __init__(self):
        """Initialize the LLM Connector with Anthropic client."""
        self._db = next(get_db())
        self._settings = get_ai_settings()
        self._deriv_service = get_deriv_service()
        self._analysis_service = get_analysis_service()
        self._client = None

    def _get_client(self):
        """Load the Anthropic client."""
        if self._client is None:
            if not self._settings.is_anthropic_configured():
                logger.warning("Anthropic API key not configured. AI features will be unavailable.")
                return None
            try:
                self._client = anthropic.Anthropic(api_key=self._settings.anthropic_api_key)
            except ImportError:
                logger.error("Anthropic package not installed.")
                return None
            except Exception as e:
                logger.error(f"Failed to initialize Anthropic client: {e}")
                return None
        return self._client

    async def _call_llm(
        self,
        system_prompt: str,
        messages: List[Dict[str, str]],
        max_tokens: int = 1024
    ) -> str:
        """Make API call to Anthropic Claude."""

        def _sync_call():
            client = self._get_client()
            response = client.messages.create(
                model=self._settings.anthropic_model_name,
                max_tokens=max_tokens,
                system=system_prompt,
                messages=messages
            )
            return response.content[0].text

        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, _sync_call)
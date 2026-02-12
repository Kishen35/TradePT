"""
AI Configuration Settings

Loads API keys and model configurations from environment variables.
Uses pydantic-settings for validation and type safety.
"""
from functools import lru_cache
from pydantic_settings import BaseSettings
from pydantic import Field


class AISettings(BaseSettings):
    """AI service configuration loaded from environment variables."""

    # Groq API Configuration (for insights generation)
    groq_api_key: str = Field(default="", alias="GROQ_API_KEY")
    groq_model_name: str = Field(default="llama-3.3-70b-versatile", alias="GROQ_MODEL_NAME")
    groq_max_tokens: int = Field(default=2048, alias="GROQ_MAX_TOKENS")
    groq_temperature: float = Field(default=0.7, alias="GROQ_TEMPERATURE")

    # Anthropic API Configuration (for education and chat)
    anthropic_api_key: str = Field(default="", alias="ANTHROPIC_API_KEY")
    anthropic_model_name: str = Field(default="claude-sonnet-4-20250514", alias="ANTHROPIC_MODEL_NAME")
    anthropic_max_tokens: int = Field(default=4096, alias="ANTHROPIC_MAX_TOKENS")

    # Embedding Configuration
    embedding_model_name: str = Field(
        default="all-MiniLM-L6-v2",
        alias="EMBEDDING_MODEL_NAME"
    )
    embedding_cache_dir: str = Field(default="./models", alias="EMBEDDING_CACHE_DIR")

    # General Settings
    debug_mode: bool = Field(default=False, alias="AI_DEBUG_MODE")
    request_timeout: int = Field(default=30, alias="AI_REQUEST_TIMEOUT")

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "case_sensitive": False,
        "extra": "ignore"
    }

    def is_groq_configured(self) -> bool:
        """Check if Groq API is configured."""
        return bool(self.groq_api_key and self.groq_api_key != "your_groq_api_key_here")

    def is_anthropic_configured(self) -> bool:
        """Check if Anthropic API is configured."""
        return bool(self.anthropic_api_key and self.anthropic_api_key != "your_anthropic_api_key_here")


@lru_cache()
def get_ai_settings() -> AISettings:
    """
    Get cached AI settings instance.

    Uses lru_cache to ensure settings are only loaded once.

    Returns:
        AISettings: The configured AI settings
    """
    return AISettings()

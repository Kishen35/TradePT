"""
Claude API Router

Provides direct access to Anthropic Claude models
for structured or raw prompt generation.
"""

from typing import Optional, List
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from app.config.ai import get_ai_settings
from app.services.logger.logger import logger
from anthropic import AsyncAnthropic

router = APIRouter(prefix="/api/claude", tags=["Claude API"])


# ============ Request / Response Models ============

class ClaudeMessage(BaseModel):
    role: str = Field(..., pattern="^(user|assistant|system)$")
    content: str


class ClaudeRequest(BaseModel):
    model: str = Field(default="claude-3-5-sonnet-20241022")
    messages: List[ClaudeMessage]
    temperature: float = Field(default=0.7, ge=0, le=1)
    max_tokens: int = Field(default=1024, ge=1, le=8192)
    system: Optional[str] = None


class ClaudeResponse(BaseModel):
    model: str
    response: str
    usage: Optional[dict] = None


# ============ Endpoint ============

@router.post("/", response_model=ClaudeResponse)
async def call_claude(request: ClaudeRequest):
    """
    Direct Claude API endpoint.

    Allows flexible message passing to Anthropic Claude.

    Request body:
    - **model**: Claude model name
    - **messages**: List of chat messages
    - **temperature**: Creativity level (0-1)
    - **max_tokens**: Max response tokens
    - **system**: Optional system instruction

    Returns Claude's response and usage metadata.
    """

    try:
        settings = get_ai_settings()

        if not settings.is_anthropic_configured():
            raise HTTPException(
                status_code=500,
                detail="Anthropic API key not configured"
            )

        client = AsyncAnthropic(api_key=settings.anthropic_api_key)

        response = await client.messages.create(
            model=request.model,
            max_tokens=request.max_tokens,
            temperature=request.temperature,
            system=(
                [{"type": "text", "text": request.system}]
                if request.system else None
            ),
            messages=[
                {
                    "role": m.role,
                    "content": [{"type": "text", "text": m.content}]
                }
                for m in request.messages
            ]
        )

        return ClaudeResponse(
            model=response.model,
            response=response.content[0].text,
            usage={
                "input_tokens": response.usage.input_tokens,
                "output_tokens": response.usage.output_tokens
            }
        )

    except Exception as e:
        logger.error(f"Claude API error: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Claude API error: {str(e)}"
        )

"""
TradePT AI Router

All AI endpoints consolidated in one file:
- /ai/health - Check if AI services are working
- /ai/analyze - Analyze trade setup (Safe/Not Safe)
- /ai/chat - Chatbot for trading questions
- /ai/lesson - Generate personalized lessons
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import logging
import json
import os
import asyncio
from pathlib import Path

# Load .env file
from dotenv import load_dotenv

# Find the .env file (in backend directory)
env_path = Path(__file__).parent.parent.parent / ".env"
load_dotenv(env_path)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/ai", tags=["ai"])

# ============================================================================
# PYDANTIC MODELS (Request/Response Schemas)
# ============================================================================

class TradeSetup(BaseModel):
    """Trade parameters scraped from Deriv UI"""
    trade_type: Optional[str] = None      # "Accumulators", "Multipliers", etc.
    growth_rate: Optional[str] = None     # "3%"
    stake: Optional[str] = None           # "10"
    take_profit_enabled: Optional[bool] = False
    max_payout: Optional[str] = None      # "6,000.00 USD"
    max_ticks: Optional[str] = None       # "85 ticks"


class AnalyzeRequest(BaseModel):
    """Request for /ai/analyze endpoint"""
    balance: str
    symbol: Optional[str] = None
    positions: Optional[List[Dict]] = []
    recentTrades: Optional[List[Dict]] = []
    winRate: Optional[str] = None
    trade_setup: Optional[TradeSetup] = None
    user_preferences: Optional[Dict[str, Any]] = {}


class AnalyzeResponse(BaseModel):
    """Response from /ai/analyze endpoint"""
    safe_to_trade: bool
    recommendation: str
    reason: str
    risk_level: str
    tip: str


class ChatRequest(BaseModel):
    """Request for /ai/chat endpoint"""
    message: str
    session_id: Optional[str] = None
    user_id: Optional[int] = 1
    user_context: Optional[Dict[str, Any]] = {}
    market_data: Optional[Dict[str, Any]] = {}


class ChatResponse(BaseModel):
    """Response from /ai/chat endpoint"""
    response: str
    session_id: str


class LessonRequest(BaseModel):
    """Request for /ai/lesson endpoint"""
    topic: str
    user_level: Optional[str] = "beginner"
    user_context: Optional[Dict[str, Any]] = {}


class LessonSection(BaseModel):
    """A section within a lesson"""
    heading: str
    content: str
    type: str = "text"  # "text", "example", "warning", "tip"


class QuizQuestion(BaseModel):
    """A quiz question"""
    question: str
    options: List[str]
    correct: str
    explanation: str


class LessonResponse(BaseModel):
    """Response from /ai/lesson endpoint"""
    title: str
    skill_level: str
    estimated_time_minutes: int
    sections: List[LessonSection]
    quiz: List[QuizQuestion]
    key_takeaways: List[str]


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def get_anthropic_client():
    """Get Anthropic client with lazy loading"""
    try:
        import anthropic
        api_key = os.getenv("ANTHROPIC_API_KEY", "")
        if not api_key or api_key == "your_anthropic_api_key_here":
            return None
        return anthropic.Anthropic(api_key=api_key)
    except ImportError:
        logger.error("Anthropic package not installed. Run: pip install anthropic")
        return None
    except Exception as e:
        logger.error(f"Failed to initialize Anthropic client: {e}")
        return None


def get_model_name():
    """Get the configured model name"""
    return os.getenv("ANTHROPIC_MODEL_NAME", "claude-sonnet-4-20250514")


async def call_claude(prompt: str, system_prompt: str = "", max_tokens: int = 1024) -> str:
    """
    Call Claude API with the given prompt.
    Returns the response text or raises an exception.
    """
    client = get_anthropic_client()
    if not client:
        raise HTTPException(status_code=503, detail="AI service not configured")

    def _sync_call():
        # Make API call - only include system if provided
        if system_prompt and system_prompt.strip():
            response = client.messages.create(
                model=get_model_name(),
                max_tokens=max_tokens,
                system=system_prompt,
                messages=[{"role": "user", "content": prompt}]
            )
        else:
            response = client.messages.create(
                model=get_model_name(),
                max_tokens=max_tokens,
                messages=[{"role": "user", "content": prompt}]
            )
        return response.content[0].text

    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, _sync_call)


# ============================================================================
# ENDPOINT 1: /ai/health - Health Check
# ============================================================================

@router.get("/health")
async def health_check():
    """
    Check if AI services are working.

    Returns:
        status: "ok" if everything is working
        anthropic_configured: True if API key is set
    """
    client = get_anthropic_client()
    return {
        "status": "ok",
        "anthropic_configured": client is not None,
        "model": get_model_name()
    }


# ============================================================================
# ENDPOINT 2: /ai/analyze - Trade Analysis (Safe/Not Safe)
# ============================================================================

@router.post("/analyze", response_model=AnalyzeResponse)
async def analyze_trade(request: AnalyzeRequest):
    """
    Analyze if a trade setup is safe based on:
    - Account balance and positions
    - Trade parameters (type, stake, growth rate, etc.)
    - User preferences (experience level, risk tolerance)

    Returns:
        safe_to_trade: Boolean
        recommendation: "SAFE TO TRADE" or "NOT SAFE TO TRADE"
        reason: Explanation
        risk_level: "low", "medium", or "high"
        tip: Actionable advice
    """

    # Build the prompt with all scraped data
    trade_setup = request.trade_setup or TradeSetup()

    prompt = f"""You are a trading safety advisor. Analyze this EXACT trade setup:

## Account Information
- Balance: {request.balance}
- Current Symbol: {request.symbol or "Not specified"}
- Open Positions: {len(request.positions or [])} positions
- Recent Win Rate: {request.winRate or "Unknown"}

## Trade Setup (User Selected These Values)
- Trade Type: {trade_setup.trade_type or "Unknown"}
- Growth Rate: {trade_setup.growth_rate or "N/A"}
- Stake Amount: {trade_setup.stake or "Unknown"} USD
- Take Profit: {"Enabled" if trade_setup.take_profit_enabled else "Disabled"}
- Max Payout: {trade_setup.max_payout or "Unknown"}
- Max Ticks: {trade_setup.max_ticks or "Unknown"}

## User Profile
- Experience: {request.user_preferences.get("experience_level", "beginner")}
- Risk Tolerance: {request.user_preferences.get("risk_behavior", "conservative")}

## Your Task
Analyze if this SPECIFIC trade setup is safe for this user.

Consider:
1. Is the stake appropriate for their balance? (Risk % = stake/balance)
2. Is the trade type suitable for their experience level?
3. Are there any red flags in the setup?

Respond in this EXACT JSON format (no other text):
{{
  "safe_to_trade": true,
  "recommendation": "SAFE TO TRADE",
  "reason": "One clear sentence explaining why",
  "risk_level": "low",
  "tip": "One actionable tip for this specific trade"
}}"""

    try:
        response_text = await call_claude(prompt, max_tokens=500)

        # Parse JSON from response (handle markdown code blocks)
        json_text = response_text
        if "```json" in json_text:
            json_text = json_text.split("```json")[1].split("```")[0]
        elif "```" in json_text:
            json_text = json_text.split("```")[1].split("```")[0]

        result = json.loads(json_text.strip())
        return AnalyzeResponse(**result)

    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse Claude response: {e}")
        # Return a safe fallback
        return AnalyzeResponse(
            safe_to_trade=False,
            recommendation="ANALYSIS ERROR",
            reason="Could not analyze trade. Please check your settings and try again.",
            risk_level="unknown",
            tip="Make sure your stake is less than 2% of your balance for safety."
        )
    except Exception as e:
        logger.error(f"Error in analyze_trade: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# ENDPOINT 3: /ai/chat - Trading Chatbot
# ============================================================================

# Simple in-memory session storage (replace with Redis/DB in production)
_chat_sessions: Dict[str, List[Dict[str, str]]] = {}

@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Chat with the AI trading assistant.

    Sends user message to Claude with context about:
    - User preferences (experience, risk tolerance)
    - Market data (balance, positions, trades)
    - Conversation history

    Returns:
        response: AI's response
        session_id: Session ID for conversation continuity
    """
    import uuid

    # Get or create session
    session_id = request.session_id or str(uuid.uuid4())
    if session_id not in _chat_sessions:
        _chat_sessions[session_id] = []

    # Check for quick responses (greetings, off-topic)
    quick_response = check_quick_response(request.message)
    if quick_response:
        _chat_sessions[session_id].append({"role": "user", "content": request.message})
        _chat_sessions[session_id].append({"role": "assistant", "content": quick_response})
        return ChatResponse(response=quick_response, session_id=session_id)

    # Build context from user data
    user_context = request.user_context or {}
    market_data = request.market_data or {}

    system_prompt = f"""You are TradePT AI, a knowledgeable and supportive trading assistant.

Your role:
- Answer trading-related questions clearly and helpfully
- Explain trading concepts and terminology
- Provide general market education
- Help with trading psychology and mindset
- Discuss risk management strategies
- Give DIRECT answers when asked about trades (BUY, SELL, HOLD, or WAIT)

Your limitations (be transparent about these):
- You cannot provide specific financial advice
- You cannot predict market movements with certainty
- You cannot execute trades or manage accounts

User Context:
- Experience Level: {user_context.get("experience_level", "beginner")}
- Trading Style: {user_context.get("trading_style", "day_trader")}
- Risk Behavior: {user_context.get("risk_behavior", "conservative")}
- Preferred Assets: {user_context.get("preferred_assets", ["various"])}

Market Data:
- Balance: {market_data.get("balance", "Unknown")}
- Current Symbol: {market_data.get("symbol", "Unknown")}
- Open Positions: {len(market_data.get("positions", []))}
- Win Rate: {market_data.get("winRate", "Unknown")}

Communication style:
- Be conversational and friendly
- Use examples when explaining concepts
- Keep responses concise but helpful
- Include relevant disclaimers when discussing strategies

IMPORTANT FORMATTING RULES:
- DO NOT use markdown formatting (no #, *, **, _, or other markdown symbols)
- Write in plain text only
- Use simple line breaks for structure
- Keep responses clean and easy to read"""

    # Add user message to history
    _chat_sessions[session_id].append({"role": "user", "content": request.message})

    # Build messages for API (last 10 messages for context)
    messages = _chat_sessions[session_id][-10:]

    try:
        client = get_anthropic_client()
        if not client:
            return ChatResponse(
                response="I'm having trouble connecting to my brain right now. Please try again in a moment.",
                session_id=session_id
            )

        def _sync_call():
            response = client.messages.create(
                model=get_model_name(),
                max_tokens=1024,
                system=system_prompt,
                messages=messages
            )
            return response.content[0].text

        loop = asyncio.get_event_loop()
        response_text = await loop.run_in_executor(None, _sync_call)

        # Add assistant response to history
        _chat_sessions[session_id].append({"role": "assistant", "content": response_text})

        return ChatResponse(response=response_text, session_id=session_id)

    except Exception as e:
        logger.error(f"Error in chat: {e}")
        fallback = get_fallback_response(request.message)
        return ChatResponse(response=fallback, session_id=session_id)


def check_quick_response(message: str) -> Optional[str]:
    """Check if message matches a quick response pattern."""
    message_lower = message.lower().strip()

    # Greetings
    greetings = ["hi", "hello", "hey", "good morning", "good afternoon", "good evening"]
    if any(message_lower == g or message_lower.startswith(g + " ") for g in greetings):
        return "Hello! I'm TradePT AI, your trading assistant. I can help you understand trading concepts, analyze your trades, and suggest educational content. What would you like to learn about today?"

    # Off-topic questions
    off_topic_keywords = [
        "weather", "sports", "movie", "music", "food", "recipe",
        "joke", "game", "celebrity", "politics", "news", "netflix"
    ]
    if any(kw in message_lower for kw in off_topic_keywords):
        return "That's an interesting topic, but I'm specialized in trading education and analysis. Is there something related to trading I can help you with?"

    # Goodbye
    goodbye_keywords = ["bye", "goodbye", "see you", "thanks bye"]
    if any(kw in message_lower for kw in goodbye_keywords):
        return "Great chatting with you! Remember, consistent learning and practice are keys to trading improvement. Feel free to come back anytime!"

    return None


def get_fallback_response(message: str) -> str:
    """Generate a fallback response when AI is unavailable."""
    message_lower = message.lower()

    if "stop loss" in message_lower:
        return "A stop loss is an order to close your position at a predetermined price level to limit potential losses. It's a crucial risk management tool that every trader should use."

    if "position size" in message_lower:
        return "Position sizing determines how much of your capital to risk on each trade. A common rule is to never risk more than 1-2% of your account on a single trade."

    if "risk" in message_lower and "reward" in message_lower:
        return "Risk-reward ratio compares potential loss to potential gain. A 1:2 ratio means risking $1 to potentially make $2. Most successful traders aim for at least 1:2 or better."

    return "I'm here to help with trading questions. I can explain concepts like risk management, trading psychology, technical analysis, and more. What would you like to know?"


# ============================================================================
# ENDPOINT 4: /ai/lesson - Personalized Lesson Generator
# ============================================================================

@router.post("/lesson", response_model=LessonResponse)
async def generate_lesson(request: LessonRequest):
    """
    Generate a personalized 2-minute trading lesson.

    Creates content tailored to:
    - User's skill level
    - Requested topic
    - User's trading preferences

    Returns:
        title: Lesson title
        sections: Lesson content sections
        quiz: Quiz questions
        key_takeaways: Summary points
    """

    user_context = request.user_context or {}

    prompt = f"""Create a 2-minute trading lesson on: "{request.topic}"

Target audience:
- Skill level: {request.user_level}
- Experience: {user_context.get("experience_level", request.user_level)}
- Trading style: {user_context.get("trading_style", "general")}

Requirements:
1. Keep it simple - explain like talking to someone new to trading
2. Use real examples with numbers
3. Include practical tips they can use TODAY
4. Add 2 quiz questions to test understanding

Respond in this EXACT JSON format:
{{
  "title": "Lesson title here",
  "skill_level": "{request.user_level}",
  "estimated_time_minutes": 2,
  "sections": [
    {{
      "heading": "What is [Topic]?",
      "content": "Simple explanation here...",
      "type": "text"
    }},
    {{
      "heading": "Real Example",
      "content": "Let's say you have $1,000...",
      "type": "example"
    }},
    {{
      "heading": "Pro Tip",
      "content": "Always remember to...",
      "type": "tip"
    }}
  ],
  "quiz": [
    {{
      "question": "What is the main purpose of X?",
      "options": ["Option A", "Option B", "Option C", "Option D"],
      "correct": "Option B",
      "explanation": "Because..."
    }}
  ],
  "key_takeaways": [
    "Takeaway 1",
    "Takeaway 2",
    "Takeaway 3"
  ]
}}

JSON only, no other text."""

    try:
        response_text = await call_claude(prompt, max_tokens=2000)

        # Parse JSON from response
        json_text = response_text
        if "```json" in json_text:
            json_text = json_text.split("```json")[1].split("```")[0]
        elif "```" in json_text:
            json_text = json_text.split("```")[1].split("```")[0]

        result = json.loads(json_text.strip())

        # Convert sections and quiz to proper models
        sections = [LessonSection(**s) for s in result.get("sections", [])]
        quiz = [QuizQuestion(**q) for q in result.get("quiz", [])]

        return LessonResponse(
            title=result.get("title", f"Introduction to {request.topic}"),
            skill_level=result.get("skill_level", request.user_level),
            estimated_time_minutes=result.get("estimated_time_minutes", 2),
            sections=sections,
            quiz=quiz,
            key_takeaways=result.get("key_takeaways", [])
        )

    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse lesson response: {e}")
        # Return a fallback lesson
        return LessonResponse(
            title=f"Introduction to {request.topic}",
            skill_level=request.user_level,
            estimated_time_minutes=2,
            sections=[
                LessonSection(
                    heading="Overview",
                    content=f"This lesson covers the fundamentals of {request.topic}. Understanding this concept is essential for improving your trading skills.",
                    type="text"
                ),
                LessonSection(
                    heading="Key Concept",
                    content="Take time to research and practice these concepts before applying them to real trades.",
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
            ]
        )
    except Exception as e:
        logger.error(f"Error generating lesson: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# ENDPOINT 5: /ai/clear-session - Clear Chat Session
# ============================================================================

@router.delete("/session/{session_id}")
async def clear_session(session_id: str):
    """Clear a chat session."""
    if session_id in _chat_sessions:
        del _chat_sessions[session_id]
        return {"status": "cleared", "session_id": session_id}
    return {"status": "not_found", "session_id": session_id}

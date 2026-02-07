# TradePT AI Services

AI-powered trading analysis, education, and chat services for the TradePT platform.

## Overview

The AI integration layer provides:
- **Trading Insights**: AI-generated analysis of trading patterns and performance
- **Educational Content**: Personalized lessons based on skill level and weaknesses
- **Chat Assistant**: Conversational trading help with context awareness
- **Semantic Search**: Vector embeddings for matching patterns to relevant lessons

## Architecture

```
backend/app/
├── ai_services/              # AI service implementations
│   ├── __init__.py          # Module exports
│   ├── analysis.py          # Statistical analysis & pattern detection
│   ├── insights.py          # Groq AI insight generation
│   ├── education.py         # Claude lesson generation
│   ├── chat.py              # Conversational assistant
│   └── embeddings.py        # Semantic search with sentence-transformers
│
├── config/
│   └── ai_config.py         # API keys and settings
│
├── prompts/                  # LLM prompt templates
│   ├── insight_prompts.py   # Insight generation prompts
│   ├── education_prompts.py # Lesson generation prompts
│   └── chat_prompts.py      # Chat interaction prompts
│
└── routers/
    └── ai_insights.py       # FastAPI endpoints
```

## API Endpoints

### GET /ai/insights/{user_id}
Generate personalized trading insights.

**Parameters:**
- `user_id` (path): User's ID
- `days` (query, default=7): Days to analyze (1-90)
- `user_level` (query, default="beginner"): Skill level

**Response:**
```json
{
  "summary": "Analyzed 15 trades with 60% win rate",
  "insights": [
    {"type": "strength", "message": "Strong win rate!", "priority": "high"}
  ],
  "recommendations": ["Consider reducing position sizes after losses"],
  "statistics": {"win_rate": 60.0, "total_trades": 15},
  "suggested_lesson": "Risk Management Basics",
  "generated_at": "2024-01-15T10:30:00"
}
```

**curl Example:**
```bash
curl http://localhost:8000/ai/insights/1?days=7&user_level=beginner
```

### POST /ai/lesson/generate
Generate a personalized lesson.

**Request Body:**
```json
{
  "topic": "Risk Management Basics",
  "skill_level": "beginner",
  "instruments": ["EURUSD", "BTC/USD"],
  "weakness": "position sizing",
  "length": "medium",
  "include_examples": true
}
```

**Response:**
```json
{
  "title": "Risk Management Fundamentals",
  "skill_level": "beginner",
  "estimated_time_minutes": 15,
  "sections": [
    {"heading": "Introduction", "content": "...", "type": "text"}
  ],
  "quiz": [
    {"question": "What is the 1% rule?", "options": [...], "correct": "A", "explanation": "..."}
  ],
  "key_takeaways": ["Never risk more than 1-2% per trade"]
}
```

**curl Example:**
```bash
curl -X POST http://localhost:8000/ai/lesson/generate \
  -H "Content-Type: application/json" \
  -d '{"topic": "Stop Loss Strategies", "skill_level": "beginner"}'
```

### POST /ai/chat
Chat with the trading assistant.

**Request Body:**
```json
{
  "user_id": 1,
  "message": "What is a stop loss?",
  "session_id": "optional-uuid"
}
```

**Response:**
```json
{
  "session_id": "uuid",
  "response": "A stop loss is an order to close your position..."
}
```

**curl Example:**
```bash
curl -X POST http://localhost:8000/ai/chat \
  -H "Content-Type: application/json" \
  -d '{"user_id": 1, "message": "Hello!"}'
```

### GET /ai/suggest-topic/{user_id}
Get recommended lesson topics.

**Parameters:**
- `user_id` (path): User's ID
- `skill_level` (query, default="beginner"): Skill level

**Response:**
```json
{
  "topics": [
    {"topic": "Managing Trading Emotions", "relevance_score": 0.95, "reason": "Based on detected revenge trading pattern"}
  ]
}
```

### GET /ai/health
Check AI services status.

```bash
curl http://localhost:8000/ai/health
```

## Setup Instructions

### 1. Install Dependencies

```bash
cd backend
pip install -r requirements.txt
```

### 2. Configure API Keys

Copy the example environment file:
```bash
cp .env.example .env
```

Edit `.env` with your API keys:
```
GROQ_API_KEY=your_groq_api_key_here
ANTHROPIC_API_KEY=your_anthropic_api_key_here
```

### 3. Get API Keys

**Groq API (for fast insights):**
1. Go to https://console.groq.com/
2. Create an account
3. Generate an API key

**Anthropic API (for education & chat):**
1. Go to https://console.anthropic.com/
2. Create an account
3. Generate an API key

### 4. Start the Server

```bash
cd backend
uvicorn app.main:app --reload
```

### 5. Test the Endpoints

```bash
# Health check
curl http://localhost:8000/ai/health

# Get insights
curl http://localhost:8000/ai/insights/1

# Chat
curl -X POST http://localhost:8000/ai/chat \
  -H "Content-Type: application/json" \
  -d '{"user_id": 1, "message": "Hello!"}'
```

## How It Works

### Data Flow

```
User Trade Data → Analysis → Pattern Detection → AI Generation → Personalized Response
                    ↓
            Statistics:          Patterns:             AI APIs:
            - Win rate          - Revenge trading     - Groq (insights)
            - Profit/Loss       - Overtrading         - Claude (education)
            - Trade frequency   - Risk issues         - Local embeddings
```

### Pattern Detection

The system detects these trading patterns:

| Pattern | Detection Criteria | Action |
|---------|-------------------|--------|
| Revenge Trading | Rapid trades after losses (<30 min) | Suggest break, emotion lesson |
| Overtrading | >10 trades per day average | Suggest trading plan lesson |
| Risk Issues | Average loss > 2x average win | Suggest position sizing lesson |
| Consistent Timing | Low trading hour variance | Positive reinforcement |

### Prompt Engineering

**Insight Prompts:** Focus on being supportive, actionable, and concise.
- Temperature: 0.7 (creative but focused)
- Max tokens: 2048
- JSON response format enforced

**Education Prompts:** Create structured, skill-appropriate content.
- Temperature: 0.8 (more creative for engagement)
- Max tokens: 4096
- Includes quiz generation

**Chat Prompts:** Conversational, educational, with user context.
- Temperature: 0.7
- Max tokens: 1024
- Maintains conversation history

## Technical Decisions

### Why Groq for Insights?
- **Speed**: Groq is extremely fast (~50ms response)
- **Cost**: Lower cost per token
- **JSON Mode**: Native JSON response support
- **Best for**: Short, focused analysis

### Why Claude for Education?
- **Quality**: Better at long-form educational content
- **Context**: Handles complex lesson structures
- **Best for**: Detailed explanations, quizzes

### Why Local Embeddings?
- **No API Cost**: Runs locally with sentence-transformers
- **Privacy**: Trade concepts don't leave the server
- **Best for**: Semantic search, pattern matching

## Fallback Behavior

When AI APIs are unavailable, the system provides fallback responses:

1. **Insights**: Rule-based analysis from statistics
2. **Lessons**: Template-based lesson structure
3. **Chat**: Pre-defined responses for common questions
4. **Embeddings**: Character-frequency based fallback

## Testing

Run the test suite:
```bash
cd backend
pytest test_ai_services.py -v
```

## Troubleshooting

### API Key Issues
```
Error: Groq API key not configured
```
- Check that `.env` file exists
- Verify API key is correct
- Restart the server after adding keys

### Import Errors
```
ModuleNotFoundError: No module named 'groq'
```
- Run: `pip install -r requirements.txt`

### Rate Limiting
```
Error: Rate limit exceeded
```
- The system will fall back to non-AI responses
- Consider caching responses
- Check your API tier limits

## Demo Script

For judges/mentors, demonstrate:

1. **Start fresh**: `uvicorn app.main:app --reload`

2. **Show AI health**:
   ```bash
   curl http://localhost:8000/ai/health
   ```

3. **Get insights for user 1**:
   ```bash
   curl http://localhost:8000/ai/insights/1
   ```

4. **Chat interaction**:
   ```bash
   curl -X POST http://localhost:8000/ai/chat \
     -H "Content-Type: application/json" \
     -d '{"user_id": 1, "message": "Why do I keep losing trades?"}'
   ```

5. **Generate personalized lesson**:
   ```bash
   curl -X POST http://localhost:8000/ai/lesson/generate \
     -H "Content-Type: application/json" \
     -d '{"topic": "Managing Trading Emotions", "skill_level": "beginner"}'
   ```

6. **Key talking points**:
   - "The AI analyzes YOUR actual trading behavior"
   - "It detects patterns like revenge trading automatically"
   - "Education is personalized to your weaknesses"
   - "Works even without API keys using fallbacks"

## Notes for Teammates

### Trade Model Required

The AI services need a Trade model. Please create in `database/models/trades.py`:

```python
class Trade(Base):
    __tablename__ = "trades"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    contract_type = Column(String)  # "CALL", "PUT", "MULTIPLIER"
    symbol = Column(String)         # "EURUSD", "Volatility 75"
    buy_price = Column(Float)
    sell_price = Column(Float, nullable=True)
    profit_loss = Column(Float, nullable=True)
    purchase_time = Column(DateTime)
    sell_time = Column(DateTime, nullable=True)
```

Until then, the system uses mock data for testing.

### Integration Points

- Import AI router in main.py ✅
- Call `/ai/insights/{user_id}` from Chrome extension
- Store session_id for chat continuity
- Pass user_context for personalization

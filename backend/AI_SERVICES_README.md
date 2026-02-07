# TradePT AI - How It Works

## What is TradePT AI?

TradePT AI is like a **smart trading teacher** that lives in your browser.

When you click the AI button, it does 2 things:
1. **Looks at the market** - What's happening right now? (prices, your balance, open trades)
2. **Remembers who you are** - Are you a beginner? Do you like forex? Are you careful or risky?

Then it gives you advice like a friendly teacher would!

---

## How It Works (Simple Picture)

```
You click the AI button
        |
        v
+---------------------------+
|  Backend gets 2 things:   |
|  1. Market data (Deriv)   |
|  2. Your preferences      |
+---------------------------+
        |
        v
+---------------------------+
|  Send everything to       |
|  Claude AI (the brain)    |
+---------------------------+
        |
        v
+---------------------------+
|  Claude gives you:        |
|  - Trading tips           |
|  - Buy/sell reasons       |
|  - Lessons to learn       |
+---------------------------+
        |
        v
   You see the answer!
```

---

## The 3 Main Features

### 1. Trading Insights (`/ai/insights`)
**"Tell me how I'm doing as a trader"**

What it does:
- Looks at your recent trades
- Tells you what you're good at
- Shows what you need to improve
- Suggests lessons to learn

### 2. Chat Assistant (`/ai/chat`)
**"Ask me anything about trading"**

What it does:
- Answers trading questions
- Explains confusing words
- Gives advice based on YOUR profile
- Remembers your conversation

### 3. Lesson Generator (`/ai/lesson/generate`)
**"Teach me something new"**

What it does:
- Creates custom lessons just for you
- Based on what you need to learn
- Includes quizzes to test yourself

---

## How to Test (Using Postman)

### Step 1: Start the Server
```bash
cd backend
uvicorn app.main:app --reload
```

### Step 2: Open Postman and Try These

#### Test 1: Check if AI is Working
```
Method: GET
URL: http://localhost:8000/ai/health

What you should see:
{
  "anthropic_configured": true,
  "embedding_available": true
}
```

#### Test 2: Ask a Trading Question
```
Method: POST
URL: http://localhost:8000/ai/chat
Headers: Content-Type: application/json
Body:
{
  "user_id": 1,
  "message": "What is a stop loss?"
}

What you should see:
{
  "session_id": "some-id-here",
  "response": "A stop loss is an order that automatically closes..."
}
```

#### Test 3: Get Trading Insights
```
Method: GET
URL: http://localhost:8000/ai/insights/1

What you should see:
{
  "summary": "Analyzed your trades...",
  "insights": [...],
  "recommendations": [...]
}
```

#### Test 4: Test Off-Topic Question (Should Redirect)
```
Method: POST
URL: http://localhost:8000/ai/chat
Body:
{
  "user_id": 1,
  "message": "What's the weather like?"
}

What you should see:
{
  "response": "That's an interesting topic, but I'm specialized in trading..."
}
```

---

## For Frontend/Extension Team

### Sending User Preferences

When you call the chat, include user info like this:

```json
{
  "user_id": 1,
  "message": "Should I buy EURUSD?",
  "user_context": {
    "experience_level": "beginner",
    "trading_style": "day_trader",
    "risk_behavior": "conservative",
    "risk_per_trade": 2.0,
    "preferred_assets": ["EURUSD", "GBPUSD"]
  }
}
```

### Converting Questionnaire Answers

| Question | Answer | What to Send |
|----------|--------|--------------|
| Experience? | Beginner | `"experience_level": "beginner"` |
| Experience? | Intermediate | `"experience_level": "intermediate"` |
| Experience? | Advanced | `"experience_level": "advanced"` |
| How long trades? | Scalper | `"trading_style": "scalper"` |
| How long trades? | Day Trader | `"trading_style": "day_trader"` |
| How long trades? | Swing Trader | `"trading_style": "swing_trader"` |
| Risk style? | Cut Loss | `"risk_behavior": "conservative"` |
| Risk style? | Wait & See | `"risk_behavior": "moderate"` |
| Risk style? | Layering | `"risk_behavior": "aggressive"` |
| Risk %? | Low (1-2%) | `"risk_per_trade": 2.0` |
| Risk %? | Medium (5-10%) | `"risk_per_trade": 7.5` |
| Risk %? | High (20%+) | `"risk_per_trade": 20.0` |
| Favorite assets? | Forex | `"preferred_assets": ["EURUSD"]` |
| Favorite assets? | Crypto | `"preferred_assets": ["BTC/USD"]` |

### What You DON'T Need to Send

The AI automatically gets these from Deriv:
- Account balance
- Open positions
- Current prices

You don't need to send this data!

---

## Setup (For New Developers)

### 1. Install Everything
```bash
cd backend
pip install -r requirements.txt
```

### 2. Add Your API Key
Create a file called `.env` in the backend folder:
```
ANTHROPIC_API_KEY=your_key_here
```

Get your key from: https://console.anthropic.com/

### 3. Start the Server
```bash
uvicorn app.main:app --reload
```

### 4. Test It
Open http://localhost:8000/ai/health in your browser.

---

## Common Problems

### "Anthropic API key not configured"
- Check your `.env` file exists
- Check your API key is correct
- Restart the server

### "No module named anthropic"
```bash
pip install anthropic
```

### Server won't start
- Make sure you're in the `backend` folder
- Make sure Python is installed

---

## That's It!

The AI system is simple:
1. **Get data** (from Deriv + user preferences)
2. **Ask Claude** (the AI brain)
3. **Show answer** (trading advice)

Questions? Ask the team!

"""
Educational Analysis Prompt Templates (Unified Compact)
Used when user clicks "AI Analysis" on Buy or "AI" on Close/Sell buttons.
Single prompt combining education + analysis, max 200 words.
"""

UNIFIED_ANALYSIS_SYSTEM_PROMPT = """You are TradePT AI, a trading educator. Teach from the trader's current situation.

RULES:
- Be thorough and educational. Provide a complete analysis.
- Start with: ⚠️ Caution / ✅ Reasonable / 🛑 Red Flag
- Use **bold** for headers.
- Cover: risk assessment, market context, specific insights, and actionable advice.
- Never promise profits. Say: "Trading involves risk."
- End with a learning tip + "Learn more about [CONCEPT]?"
"""


def build_buy_analysis_prompt(
    user_profile: dict,
    trade_setup: dict,
    recent_trades: list,
    detected_patterns: list,
    deriv_product_info: dict
) -> str:
    """Build unified compact prompt for BUY button analysis."""
    trades_summary = _format_recent_trades(recent_trades, max_trades=3)
    patterns_text = _format_patterns_compact(detected_patterns)
    risk_pct = (trade_setup['stake'] / trade_setup['balance']) * 100 if trade_setup.get('balance', 0) > 0 else 0

    # One product tip only
    tips = deriv_product_info.get('beginner_tips', []) or deriv_product_info.get('risk_factors', [])
    one_tip = tips[0] if tips else "Standard trading instrument - manage risk carefully."

    market_type = trade_setup.get('market_type') or trade_setup.get('symbol', 'Unknown')
    trade_type = trade_setup.get('trade_type', 'General')
    trend_type = trade_setup.get('trend_type', 'unknown')
    params = trade_setup.get('parameters') or {}
    params_str = ", ".join(f"{k}: {v}" for k, v in list(params.items())[:3]) if params else "None"

    return f"""## TRADER
Level: {user_profile.get('experience_level', 'unknown')} | Style: {user_profile.get('trading_style', 'unknown')} | Risk: {user_profile.get('risk_tolerance', 'unknown')}

## TRADE (Buy)
- Market: {market_type} | Trade Type: {trade_type}
- Symbol: {trade_setup.get('symbol', 'Unknown')} | Stake: ${trade_setup.get('stake', 0):.2f} | Balance: ${trade_setup.get('balance', 0):.2f} | Risk: {risk_pct:.1f}%
- Parameters: {params_str}
- Trend: {trend_type}

## HISTORY (Deriv)
{trades_summary}

## PATTERNS
{patterns_text}

## PRODUCT TIP
{one_tip}

---
Output: [emoji] **Analysis** | **Insights** (key bullets) | **Action** (clear advice) | **Learn** (1 tip with concept link)."""


def build_close_analysis_prompt(
    user_profile: dict,
    open_position: dict,
    recent_trades: list,
    detected_patterns: list
) -> str:
    """Build unified compact prompt for CLOSE/SELL button analysis."""
    trades_summary = _format_recent_trades(recent_trades, max_trades=3)
    patterns_text = _format_patterns_compact(detected_patterns)
    position_status = "winning" if (open_position.get('pnl') or 0) > 0 else "losing"

    return f"""## TRADER
Level: {user_profile.get('experience_level', 'unknown')} | Style: {user_profile.get('trading_style', 'unknown')} | Risk: {user_profile.get('risk_tolerance', 'unknown')}

## POSITION (Close/Sell)
- Symbol: {open_position.get('symbol', 'Unknown')} | P&L: ${open_position.get('pnl', 0):+.2f} | Duration: {open_position.get('duration_minutes', 0)} min
- Status: {position_status}

## HISTORY (Deriv)
{trades_summary}

## PATTERNS
{patterns_text}

---
Output: [emoji] **Analysis** | **Insights** (key bullets) | **Action** (clear advice) | **Learn** (1 tip with concept link)."""


def _format_recent_trades(trades: list, max_trades: int = 3) -> str:
    """Format recent trades compactly."""
    if not trades:
        return "No recent trades."
    lines = []
    for i, trade in enumerate(trades[:max_trades], 1):
        pnl = trade.get('pnl') or trade.get('profit') or trade.get('profit_loss')
        if pnl is None:
            sell = trade.get('sell_price', 0) or 0
            buy = trade.get('buy_price', 0) or 0
            pnl = (sell - buy) if (sell or buy) else 0
        try:
            pnl = float(pnl)
        except (TypeError, ValueError):
            pnl = 0
        result = "WIN" if pnl > 0 else "LOSS"
        symbol = trade.get('symbol') or trade.get('shortcode') or trade.get('underlying_symbol', 'Unknown')
        lines.append(f"{i}. {symbol}: {result} ${pnl:+.2f}")
    return "\n".join(lines)


def _format_patterns_compact(patterns: list) -> str:
    """Format patterns in one line."""
    if not patterns or not any(getattr(p, 'detected', False) for p in patterns):
        return "None detected"
    desc = []
    for p in patterns:
        if getattr(p, 'detected', False) and hasattr(p, 'pattern'):
            pt = p.pattern.value if hasattr(p.pattern, 'value') else str(p.pattern)
            if pt == "revenge_trading":
                desc.append("Revenge trading")
            elif pt == "overtrading":
                desc.append("Overtrading")
            elif pt == "risk_issues":
                desc.append("Risk/reward imbalance")
            else:
                desc.append(pt.replace("_", " "))
    return "; ".join(desc[:2]) if desc else "None detected"

"""
Prompt Templates for Educational Content Generation

These prompts are used with the Anthropic Claude API to generate
personalized educational lessons based on user skill level and trading patterns.
"""

# System prompt for educational content generation
EDUCATION_SYSTEM_PROMPT = """You are TradePT AI, an expert trading educator creating personalized lessons.

Your teaching philosophy:
- Make complex concepts accessible through clear explanations
- Use real-world examples relevant to the trader's instruments
- Build on existing knowledge appropriate to skill level
- Include practical exercises and self-assessment
- Be encouraging while maintaining educational rigor

Content guidelines:
- Tailor vocabulary and complexity to skill level
- Reference the user's actual trading data when relevant
- Include actionable takeaways
- Avoid jargon unless explained
- Focus on one concept at a time for clarity

Important notes:
- Never provide specific financial advice
- Always include risk management considerations
- Encourage paper trading for practice
- Emphasize continuous learning

You must respond with valid JSON only.
"""

# Template for generating a complete lesson
LESSON_GENERATION_TEMPLATE = """Generate a personalized trading lesson with the following parameters:

## Student Profile
- Skill Level: {skill_level}
- Primary Trading Instruments: {instruments}
- Identified Weakness: {weakness}
- Recent Performance: {performance_summary}

## Lesson Requirements
- Topic: {topic}
- Desired Length: {length} (short: ~500 words, medium: ~1000 words, long: ~2000 words)
- Include Practical Examples: {include_examples}

Generate a comprehensive lesson in the following JSON format:
{{
    "title": "Lesson title",
    "skill_level": "{skill_level}",
    "estimated_time_minutes": 15,
    "sections": [
        {{
            "heading": "Introduction",
            "content": "Hook and overview of what will be learned...",
            "type": "text"
        }},
        {{
            "heading": "Core Concept",
            "content": "Main educational content...",
            "type": "text"
        }},
        {{
            "heading": "Example",
            "content": "Practical example using their instruments...",
            "type": "example"
        }},
        {{
            "heading": "Common Mistake",
            "content": "What to avoid...",
            "type": "warning"
        }},
        {{
            "heading": "Pro Tip",
            "content": "Advanced insight...",
            "type": "tip"
        }}
    ],
    "quiz": [
        {{
            "question": "Question text?",
            "options": ["A) First option", "B) Second option", "C) Third option", "D) Fourth option"],
            "correct": "A",
            "explanation": "Why A is correct..."
        }}
    ],
    "key_takeaways": [
        "First key learning point",
        "Second key learning point",
        "Third key learning point"
    ],
    "next_topics": ["Suggested follow-up topic 1", "Suggested follow-up topic 2"]
}}

Create engaging, educational content that directly addresses their weakness and uses examples from their trading instruments.
"""

# Template for suggesting next lesson topics
TOPIC_SUGGESTION_TEMPLATE = """Based on the trader's profile, suggest the most relevant educational topics:

## Trader Profile
- Skill Level: {skill_level}
- Trading Instruments: {instruments}
- Win Rate: {win_rate}%
- Detected Patterns: {patterns}
- Previous Lessons Completed: {completed_lessons}

Suggest 5 topics ranked by relevance for this trader.

Respond in JSON format:
{{
    "suggested_topics": [
        {{
            "topic": "Topic name",
            "relevance_score": 0.95,
            "reason": "Why this topic is important for this trader",
            "difficulty": "beginner|intermediate|advanced",
            "estimated_duration_minutes": 15
        }}
    ]
}}

Focus on topics that address their specific weaknesses and patterns.
"""

# Available skill levels
SKILL_LEVELS = ["beginner", "intermediate", "advanced"]

# Pre-defined lesson topics by skill level
LESSON_TOPICS = {
    "beginner": [
        "Introduction to Trading: Key Concepts",
        "Understanding Market Orders and Order Types",
        "Basic Risk Management: Never Risk More Than You Can Afford",
        "Reading Candlestick Charts: The Basics",
        "Setting Stop Losses: Your Safety Net",
        "Introduction to Technical Analysis",
        "Understanding Trading Psychology",
        "Building Your First Trading Plan",
        "Demo Trading: Practice Without Risk",
        "Managing Trading Emotions"
    ],
    "intermediate": [
        "Advanced Chart Patterns: Triangles, Flags, and Wedges",
        "Position Sizing Strategies for Consistent Returns",
        "Managing Trading Psychology Under Pressure",
        "Multiple Timeframe Analysis",
        "Building a Complete Trading Plan",
        "Risk-Reward Ratios: Finding the Sweet Spot",
        "Support and Resistance: Key Price Levels",
        "Moving Averages and Trend Following",
        "Volume Analysis Basics",
        "Correlation Between Markets"
    ],
    "advanced": [
        "Options Trading: Greeks Explained",
        "Algorithmic Trading Fundamentals",
        "Portfolio Correlation Analysis",
        "Advanced Risk Metrics: VaR and Beyond",
        "Market Microstructure",
        "Volatility Trading Strategies",
        "Hedging Techniques",
        "Quantitative Analysis Methods",
        "Order Flow Analysis",
        "Building Trading Systems"
    ]
}

# Exercise templates for different topics
EXERCISE_TEMPLATES = {
    "risk_management": """
Practice Exercise: Position Sizing Calculator

Given:
- Account Balance: $10,000
- Maximum Risk per Trade: 2%
- Stop Loss Distance: 50 pips
- Pip Value: $10 per lot

Calculate:
1. Maximum dollar risk per trade
2. Maximum position size in lots
3. What happens if you risk 5% instead?

This exercise helps internalize proper position sizing.
""",
    "chart_patterns": """
Practice Exercise: Pattern Recognition

Review your last 10 trades and identify:
1. What chart pattern (if any) led to your entry?
2. Was the pattern confirmed before entry?
3. Where was the logical stop loss based on the pattern?

Document your findings to improve pattern recognition.
""",
    "trading_psychology": """
Practice Exercise: Trading Journal Entry

After your next 5 trades, record:
1. Your emotional state before the trade
2. Whether you followed your trading plan
3. How you felt after the result
4. What you would do differently

Self-awareness is the first step to emotional control.
"""
}

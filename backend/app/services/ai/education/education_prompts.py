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

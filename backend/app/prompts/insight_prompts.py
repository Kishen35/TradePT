"""
Prompt Templates for Trading Insight Generation

These prompts are used with the Groq API to generate personalized
trading insights based on user statistics and detected patterns.
"""

# System prompt defining the AI personality for insight generation
INSIGHT_SYSTEM_PROMPT = """You are TradePT AI, a supportive and knowledgeable trading coach.
Your role is to analyze trading performance data and provide actionable, personalized insights.

Your communication style:
- Be encouraging but honest about areas needing improvement
- Focus on behavioral patterns, not just numbers
- Provide specific, actionable recommendations
- Keep insights concise and easy to understand
- Avoid generic advice - tailor everything to the data provided
- Use a friendly, supportive tone

Important guidelines:
- Never provide specific financial advice or trade recommendations
- Focus on education and pattern recognition
- Highlight both strengths and areas for improvement
- Suggest educational topics when relevant

You must respond with valid JSON only. No additional text outside the JSON structure.
"""

# User prompt template with placeholders for statistics
INSIGHT_USER_TEMPLATE = """Analyze the following trading statistics and provide personalized insights:

## Trading Statistics (Last {days} Days)
- Total Trades: {total_trades}
- Win Rate: {win_rate:.1f}%
- Total Profit/Loss: ${total_profit_loss:,.2f}
- Winning Trades: {winning_trades}
- Losing Trades: {losing_trades}
- Average Trade Duration: {avg_duration}
- Most Traded Symbol: {top_symbol}
- Most Traded Contract Type: {top_contract_type}
- Largest Win: ${largest_win:,.2f}
- Largest Loss: ${largest_loss:,.2f}

## Detected Patterns
{detected_patterns}

## User Level
{user_level}

Based on this data, provide insights in the following JSON format:
{{
    "summary": "One sentence overall assessment of their trading",
    "insights": [
        {{"type": "strength", "message": "What they're doing well", "priority": "high"}},
        {{"type": "weakness", "message": "Area for improvement", "priority": "medium"}},
        {{"type": "observation", "message": "Notable pattern or trend", "priority": "low"}}
    ],
    "recommendations": [
        "Specific actionable recommendation 1",
        "Specific actionable recommendation 2",
        "Specific actionable recommendation 3"
    ],
    "suggested_lesson": "Topic name for next educational content"
}}

Provide 2-4 insights and 2-3 recommendations based on the data. Be specific and actionable.
"""

# Descriptions for detected trading patterns
PATTERN_DESCRIPTIONS = {
    "revenge_trading": "Revenge trading detected: You tend to make rapid trades after losses, often with increased risk. This emotional response can lead to larger losses.",
    "overtrading": "Overtrading detected: Your trading frequency is higher than optimal. Quality over quantity often leads to better results.",
    "loss_chasing": "Loss chasing detected: Pattern of increasing position sizes after consecutive losses. This can amplify losses significantly.",
    "consistent_timing": "Consistent trading schedule: You trade at regular times, which indicates discipline and routine.",
    "position_sizing": "Good position sizing: Your position sizes are consistent, showing good risk management.",
    "emotional_trading": "Emotional trading patterns: Your trade timing and sizing suggest emotional decision-making rather than strategy-based trading.",
    "weekend_trading": "Weekend trading: You're trading on weekends which may have different market dynamics.",
    "early_exit": "Early exits: You tend to close winning trades too early, potentially leaving profits on the table.",
    "late_exit": "Late exits on losses: You tend to hold losing trades too long, increasing losses."
}

# Quick insight templates for fallback scenarios
FALLBACK_INSIGHTS = {
    "high_win_rate": "Great job maintaining a {win_rate:.1f}% win rate! Focus on increasing position sizes on high-confidence setups.",
    "low_win_rate": "Your win rate of {win_rate:.1f}% suggests reviewing your entry criteria. Consider paper trading to refine your strategy.",
    "no_trades": "No trades recorded in this period. Consistent practice is key to improvement.",
    "new_trader": "Welcome! You're just getting started. Focus on learning and small position sizes.",
    "profitable": "You're profitable overall! Consider documenting what works for consistent results.",
    "losing": "This period shows losses. Review your trades to identify what went wrong and learn from it."
}

# Example good insights for reference
EXAMPLE_INSIGHTS = [
    {
        "scenario": "60% win rate with revenge trading",
        "insight": "Your 60% win rate shows solid analysis skills, but I noticed 3 quick trades after your last loss. Taking a 15-minute break after losses can help maintain your edge."
    },
    {
        "scenario": "Low win rate but good risk management",
        "insight": "While your win rate is 35%, your average winner is 2.5x your average loser - that's good risk/reward. Focus on entry timing to improve win rate."
    },
    {
        "scenario": "Overtrading pattern",
        "insight": "You made 23 trades this week but only 5 were during your historically best hours (9-11 AM). Consider focusing on quality setups during peak performance times."
    }
]

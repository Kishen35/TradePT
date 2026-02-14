"""
Deriv Trading Products Knowledge Base
Static reference data for educational content generation
"""

DERIV_PRODUCTS = {
    "Accumulators": {
        "description": "Accumulators allow you to grow your potential profit with each passing tick, provided the tick movement stays within a specified range around the entry spot",
        "parameters": {
            "growth_rate": "Percentage increase per tick (1%, 2%, 3%, 4%, 5%)",
            "take_profit": "Target profit level to automatically close trade",
            "stake": "Initial investment amount"
        },
        "risk_factors": [
            "Higher growth rate = higher risk of hitting barrier",
            "No stop loss - trade runs until barrier or take profit hit",
            "Tick-by-tick accumulation requires constant monitoring"
        ],
        "beginner_tips": [
            "Start with 1-2% growth rate to minimize barrier risk",
            "ALWAYS set take profit - never leave open-ended",
            "Practice on demo first to understand tick mechanics",
            "Don't chase losses by increasing growth rate"
        ],
        "common_mistakes": [
            "Setting growth rate too high (3%+ for beginners)",
            "No take profit set (greed)",
            "Not understanding how barriers work",
            "Overtrading after wins"
        ]
    },
    
    "Multipliers": {
        "description": "Multipliers allow you to trade on the price movement of an asset with increased market exposure using leverage",
        "parameters": {
            "multiplier": "Leverage factor (x5, x10, x25, x50, x100, x250, x1000)",
            "stop_loss": "Maximum loss threshold",
            "take_profit": "Target profit threshold",
            "stake": "Initial margin"
        },
        "risk_factors": [
            "Higher multiplier = can lose entire stake faster",
            "Overnight fees for positions held >1 day",
            "Volatility can trigger stop loss quickly"
        ],
        "beginner_tips": [
            "Start with x5 or x10 multiplier",
            "ALWAYS set stop loss (2-3% of balance max)",
            "Use take profit to lock in gains automatically",
            "Never use full balance on one trade"
        ]
    },
    
    "Volatility_Indices": {
        "description": "Synthetic indices that simulate real-world market volatility with constant characteristics",
        "types": {
            "V10_1s": {"volatility": "10% annually", "tick_rate": "1 tick per second"},
            "V25_1s": {"volatility": "25% annually", "tick_rate": "1 tick per second"},
            "V50_1s": {"volatility": "50% annually", "tick_rate": "1 tick per second"},
            "V75_1s": {"volatility": "75% annually", "tick_rate": "1 tick per second"},
            "V100_1s": {"volatility": "100% annually", "tick_rate": "1 tick per second"}
        },
        "characteristics": [
            "Available 24/7 unlike forex markets",
            "No fundamental news impact",
            "Predictable volatility levels",
            "Ideal for testing strategies"
        ],
        "beginner_tips": [
            "Start with V10 or V25 for lower volatility",
            "Use V100 for scalping practice",
            "Technical analysis works well on synthetics",
            "Less affected by world events = easier to learn"
        ]
    },
    
    "Boom_Crash_Indices": {
        "description": "Synthetic indices with intermittent spikes (Boom) or drops (Crash)",
        "types": {
            "Boom_300": "1 spike per 300 ticks on average",
            "Boom_500": "1 spike per 500 ticks on average",
            "Crash_300": "1 drop per 300 ticks on average",
            "Crash_500": "1 drop per 500 ticks on average"
        },
        "risk_factors": [
            "Spikes/drops are sudden and unpredictable",
            "High risk for beginners",
            "Can wipe out position instantly"
        ],
        "beginner_tips": [
            "AVOID as complete beginner",
            "Only trade after mastering basics",
            "Use very tight stop losses",
            "Never hold positions long-term"
        ]
    },
    
    "Forex": {
        "description": "Foreign exchange currency pairs (e.g., EUR/USD, GBP/USD)",
        "characteristics": [
            "Market hours: 24/5 (closed weekends)",
            "Affected by economic news and data",
            "Major pairs have tightest spreads",
            "Different sessions: Asian, European, US"
        ],
        "major_pairs": {
            "EUR/USD": "Most liquid, tightest spreads",
            "GBP/USD": "More volatile than EUR/USD",
            "USD/JPY": "Safe haven pair",
            "AUD/USD": "Commodity-correlated"
        },
        "beginner_tips": [
            "Start with EUR/USD (most predictable)",
            "Avoid trading during major news releases",
            "Learn one pair deeply before diversifying",
            "Understand pip values for position sizing"
        ]
    }
}


# Pattern to Module Mapping
PATTERN_MODULE_MAPPING = {
    "revenge_trading": {
        "module_title": "Managing Trading Emotions",
        "category": "Psychology",
        "urgency": "high",
        "reason": "Revenge trading detected - making rapid trades after losses to 'make it back' leads to bigger losses"
    },
    "overtrading": {
        "module_title": "Quality Over Quantity",
        "category": "Psychology",
        "urgency": "high",
        "reason": "Overtrading detected - excessive trades reduce win rate and increase costs"
    },
    "no_stop_loss": {
        "module_title": "Stop Loss Fundamentals",
        "category": "Risk_Management",
        "urgency": "critical",
        "reason": "Trading without stop losses detected - critical risk management issue"
    },
    "poor_risk_reward": {
        "module_title": "Risk:Reward Ratios Explained",
        "category": "Risk_Management",
        "urgency": "high",
        "reason": "Poor risk/reward ratio - average loss > 2x average win"
    },
    "holding_losses": {
        "module_title": "When to Cut Losses",
        "category": "Psychology",
        "urgency": "medium",
        "reason": "Holding losing positions too long - emotional attachment to trades"
    },
    "early_exits": {
        "module_title": "Managing Winning Positions",
        "category": "Risk_Management",
        "urgency": "medium",
        "reason": "Cutting winners too early - leaving profits on the table"
    },
    "high_growth_rate_accumulator": {
        "module_title": "Accumulators Explained",
        "category": "Market_Structure",
        "urgency": "medium",
        "reason": "Using high growth rates in Accumulators - understand the mechanics"
    },
    "no_take_profit": {
        "module_title": "Position Sizing 101",
        "category": "Risk_Management",
        "urgency": "high",
        "reason": "Not setting take profit - greed can turn wins into losses"
    }
}


def get_product_info(product_name: str) -> dict:
    """Get detailed info about a Deriv product"""
    return DERIV_PRODUCTS.get(product_name, {})


def get_module_for_pattern(pattern: str) -> dict:
    """Map detected pattern to recommended module"""
    return PATTERN_MODULE_MAPPING.get(pattern, {})

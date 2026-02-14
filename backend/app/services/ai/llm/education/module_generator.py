"""
AI-Powered Module Content Generator
Uses AI to create educational modules personalized by trader type (momentum/precision).
"""

import json
import asyncio
from typing import Dict, List, Optional
from anthropic import Anthropic
from app.config.ai import get_ai_settings
import logging
logger = logging.getLogger(__name__)


# ============ Hardcoded Module Definitions ============
# 12 modules across 4 categories, with content variants per trader type.
# Module 1 (RSI) uses AI generation for quiz; the rest are hardcoded.

MODULES = [
    # ── Technical Analysis (4 modules) ──
    {
        "id": 1,
        "title": "RSI - Relative Strength Index",
        "category": "Technical_Analysis",
        "key_concepts": ["momentum oscillator", "overbought/oversold levels", "14-period standard"],
        "estimated_minutes": 4,
        "exp_reward": 50,
        "ai_generated_quiz": True,  # Only this module uses AI for quiz
        "momentum_focus": "Using RSI to confirm breakout momentum and trend strength",
        "precision_focus": "Using RSI divergences to spot reversals and mean reversion entries",
    },
    {
        "id": 2,
        "title": "Support & Resistance",
        "category": "Technical_Analysis",
        "key_concepts": ["key price levels", "horizontal lines", "bounces and breakouts"],
        "estimated_minutes": 5,
        "exp_reward": 50,
        "ai_generated_quiz": False,
        "momentum_focus": "Identifying breakout levels to ride momentum after price breaks through",
        "precision_focus": "Identifying bounce zones for patient entries at key levels",
        "hardcoded_quiz": {
            "momentum": [
                {
                    "question": "Price breaks above a strong resistance level with high volume. As a momentum trader, what is the best action?",
                    "options": ["A) Wait for price to return below resistance", "B) Enter long on the breakout with a stop below the level", "C) Short the market expecting a reversal", "D) Ignore it — breakouts always fail"],
                    "correct": "B",
                    "explanation": "Momentum traders capitalize on breakouts. A break above resistance with volume confirms buyer strength. Placing a stop below the broken level (now support) manages risk while riding the trend."
                },
                {
                    "question": "You notice price has tested a support level 3 times without breaking. What does this suggest for momentum trading?",
                    "options": ["A) The support is weakening and will break soon", "B) The support is strong — look for a breakout in the opposite direction (upward)", "C) Support levels don't matter for momentum traders", "D) You should short at support"],
                    "correct": "B",
                    "explanation": "Multiple tests of support that hold indicate strong buying interest. Momentum traders look for the resulting breakout when buyers push price away from support into a new trend leg upward."
                }
            ],
            "precision": [
                {
                    "question": "Price approaches a support level that has held 3 times before. As a precision trader, what is the ideal strategy?",
                    "options": ["A) Buy immediately before it touches support", "B) Wait for price to touch support, show a rejection candle, then enter long", "C) Short at support since it might break", "D) Ignore support levels entirely"],
                    "correct": "B",
                    "explanation": "Precision traders wait for confirmation. A rejection candle (hammer, pin bar) at a proven support level gives a high-probability entry with a tight stop just below the level."
                },
                {
                    "question": "Price breaks above resistance but the candle has a very long upper wick. What should a precision trader do?",
                    "options": ["A) Enter long — any break is a signal", "B) Avoid the trade — the long wick signals rejection and a possible false breakout", "C) Enter short immediately", "D) Double the position size"],
                    "correct": "B",
                    "explanation": "Precision traders look for clean price action. A long upper wick at resistance indicates sellers rejected the breakout. This is a classic false breakout pattern — patience avoids the trap."
                }
            ]
        }
    },
    {
        "id": 3,
        "title": "MACD Indicator",
        "category": "Technical_Analysis",
        "key_concepts": ["signal line crossovers", "histogram", "trend confirmation"],
        "estimated_minutes": 5,
        "exp_reward": 50,
        "ai_generated_quiz": False,
        "momentum_focus": "Using MACD crossovers to time entries into trending moves",
        "precision_focus": "Using MACD divergence to identify exhaustion and reversal setups",
        "hardcoded_quiz": {
            "momentum": [
                {
                    "question": "The MACD line crosses above the signal line while both are below zero. What does this mean for a momentum trader?",
                    "options": ["A) Strong sell signal", "B) Early bullish momentum — potential trend reversal upward", "C) No signal — MACD must be above zero", "D) Time to exit all positions"],
                    "correct": "B",
                    "explanation": "A bullish crossover below zero indicates momentum is shifting from bearish to bullish. Momentum traders use this as an early entry signal, often confirmed by price action above a moving average."
                },
                {
                    "question": "The MACD histogram is growing taller (larger bars). What does this indicate?",
                    "options": ["A) Momentum is weakening", "B) Momentum is strengthening — the trend is accelerating", "C) The market is about to reverse", "D) Volume is increasing"],
                    "correct": "B",
                    "explanation": "Growing histogram bars mean the MACD line is moving further from the signal line — momentum is increasing. Momentum traders use this to stay in winning trades longer."
                }
            ],
            "precision": [
                {
                    "question": "Price makes a new high but MACD makes a lower high. What is this pattern called and what does it suggest?",
                    "options": ["A) Bearish divergence — momentum is weakening despite new highs", "B) Bullish confirmation — the trend is strong", "C) MACD lag — ignore it", "D) Normal MACD behavior in an uptrend"],
                    "correct": "A",
                    "explanation": "Bearish divergence occurs when price makes higher highs but MACD makes lower highs. This signals weakening momentum and is a key signal for precision traders looking for reversal entries."
                },
                {
                    "question": "As a precision trader, when is the best time to enter a trade using MACD?",
                    "options": ["A) As soon as any crossover happens", "B) When MACD divergence aligns with a key support/resistance level", "C) When the histogram is at its tallest", "D) Only when MACD is above zero"],
                    "correct": "B",
                    "explanation": "Precision traders combine multiple confirmations. MACD divergence at a key S/R level provides a high-probability setup with clear stop placement and well-defined risk."
                }
            ]
        }
    },
    {
        "id": 4,
        "title": "Candlestick Patterns",
        "category": "Technical_Analysis",
        "key_concepts": ["doji", "engulfing", "hammer", "shooting star"],
        "estimated_minutes": 5,
        "exp_reward": 50,
        "ai_generated_quiz": False,
        "momentum_focus": "Spotting continuation patterns that confirm trend strength",
        "precision_focus": "Identifying reversal patterns at key levels for precise entries",
        "hardcoded_quiz": {
            "momentum": [
                {
                    "question": "During a strong uptrend, you see three consecutive bullish candles with increasing body sizes. What does this pattern suggest?",
                    "options": ["A) The trend is about to reverse", "B) Three white soldiers — strong bullish momentum continuation", "C) Overbought condition — sell immediately", "D) Normal market noise"],
                    "correct": "B",
                    "explanation": "Three white soldiers (progressive bullish candles) indicate strong buying momentum. Momentum traders use this as confirmation to stay long or add to positions during a trend."
                },
                {
                    "question": "Which candlestick pattern best confirms a breakout for momentum traders?",
                    "options": ["A) Doji at resistance", "B) Marubozu (full body, no wicks) closing above resistance", "C) Shooting star above resistance", "D) Inside bar at resistance"],
                    "correct": "B",
                    "explanation": "A marubozu (strong full-body candle) closing above resistance shows decisive buyer commitment. No wicks mean there was no hesitation — the strongest breakout confirmation."
                }
            ],
            "precision": [
                {
                    "question": "You see a hammer candlestick at a known support level. What should a precision trader do?",
                    "options": ["A) Buy immediately on the hammer", "B) Wait for the next candle to confirm the hammer (close above hammer's body), then enter", "C) Ignore it — single candles don't matter", "D) Short the market"],
                    "correct": "B",
                    "explanation": "Precision traders always seek confirmation. A hammer at support shows potential reversal, but the next candle closing above the hammer's body confirms it. This reduces false signal entries."
                },
                {
                    "question": "A bearish engulfing pattern appears at a strong resistance level after a long uptrend. What does this mean?",
                    "options": ["A) Continuation of the uptrend", "B) Strong reversal signal — sellers overpowered buyers at a key level", "C) Insignificant — engulfing patterns are unreliable", "D) Enter a long position"],
                    "correct": "B",
                    "explanation": "A bearish engulfing at resistance in an extended uptrend is a high-probability reversal signal. The large bearish candle completely engulfs the prior bullish candle, showing seller dominance."
                }
            ]
        }
    },
    # ── Trading Psychology (3 modules) ──
    {
        "id": 5,
        "title": "Managing Trading Emotions",
        "category": "Psychology",
        "key_concepts": ["fear and greed", "emotional discipline", "taking breaks"],
        "estimated_minutes": 4,
        "exp_reward": 50,
        "ai_generated_quiz": False,
        "momentum_focus": "Managing FOMO and the urge to chase every breakout",
        "precision_focus": "Managing impatience while waiting for the perfect setup",
        "hardcoded_quiz": {
            "momentum": [
                {
                    "question": "You see a massive breakout happening but you missed the entry. You feel a strong urge to chase it. What should you do?",
                    "options": ["A) Jump in immediately — you can't miss this", "B) Wait for a pullback to the breakout level before entering", "C) Enter with double position size to make up for the late entry", "D) Short it — it's gone too far"],
                    "correct": "B",
                    "explanation": "FOMO (Fear of Missing Out) is a momentum trader's biggest enemy. Chasing late entries means poor risk/reward. Waiting for a pullback retest gives a better entry with clear stop placement."
                },
                {
                    "question": "After 3 winning momentum trades, you feel invincible and want to take bigger positions. What psychological trap is this?",
                    "options": ["A) Smart trading — winners should bet bigger", "B) Overconfidence bias — winning streaks can lead to reckless sizing", "C) Positive reinforcement — always increase after wins", "D) Normal behavior for profitable traders"],
                    "correct": "B",
                    "explanation": "Overconfidence after a winning streak leads to oversized positions and careless entries. Professional traders stick to their position sizing rules regardless of recent results."
                }
            ],
            "precision": [
                {
                    "question": "You've been waiting 2 hours for your setup but the market hasn't reached your entry level. You start thinking about entering early. What should you do?",
                    "options": ["A) Enter now — close enough is good enough", "B) Stick to your plan — patience IS the edge for precision traders", "C) Switch to a different instrument", "D) Cancel the trade entirely"],
                    "correct": "B",
                    "explanation": "Precision trading requires patience. Your edge comes from entering at exact levels with tight stops. Entering early widens your stop and reduces your risk/reward ratio."
                },
                {
                    "question": "Your precision setup triggered, hit your target for +2R profit. You feel like the analysis was obvious and want to skip analysis on the next trade. What is happening?",
                    "options": ["A) You've mastered the market", "B) Hindsight bias — the trade looks obvious AFTER it worked, but the process still matters", "C) You can trade on instinct now", "D) Your system is perfect and doesn't need checking"],
                    "correct": "B",
                    "explanation": "Hindsight bias makes past trades look obvious. Precision traders succeed by following the same rigorous process every time, not by skipping steps after wins."
                }
            ]
        }
    },
    {
        "id": 6,
        "title": "Avoiding Revenge Trading",
        "category": "Psychology",
        "key_concepts": ["revenge trading", "15-minute rule", "breaking the cycle"],
        "estimated_minutes": 4,
        "exp_reward": 50,
        "ai_generated_quiz": False,
        "momentum_focus": "Stopping the cycle of chasing losses with bigger momentum bets",
        "precision_focus": "Preventing the urge to lower entry standards after a loss",
        "hardcoded_quiz": {
            "momentum": [
                {
                    "question": "You just lost $50 on a failed breakout. You see another breakout forming and want to enter with a bigger position to recover. What is this?",
                    "options": ["A) Good opportunity to recover", "B) Revenge trading — emotional reaction to recoup losses", "C) Smart doubling-down strategy", "D) Normal position scaling"],
                    "correct": "B",
                    "explanation": "This is textbook revenge trading. The desire to 'make it back' leads to larger positions on unvetted setups. The 15-minute rule: after a loss, step away for at least 15 minutes."
                },
                {
                    "question": "What is the most effective way to prevent revenge trading after a loss?",
                    "options": ["A) Take the next trade immediately to stay in the zone", "B) Have a pre-defined daily loss limit and stop trading when reached", "C) Increase position size to recover faster", "D) Switch to a different timeframe"],
                    "correct": "B",
                    "explanation": "A daily loss limit (e.g., max 3% of account) is a circuit breaker. When hit, you stop trading for the day. This removes the emotional decision from the equation entirely."
                }
            ],
            "precision": [
                {
                    "question": "After a losing trade, you notice yourself considering a setup you would normally skip because it doesn't meet all your criteria. What should you do?",
                    "options": ["A) Take it — lower standards just this once", "B) Recognize this as revenge trading and only take setups that meet ALL criteria", "C) The setup is probably fine if it's close", "D) Enter with a smaller position as a compromise"],
                    "correct": "B",
                    "explanation": "Lowering entry criteria after a loss is a subtle form of revenge trading. Precision traders maintain the same standards regardless of recent results. If it doesn't meet ALL criteria, skip it."
                },
                {
                    "question": "You've had 3 losses in a row following your system. You start questioning if your system works. What is the correct response?",
                    "options": ["A) Abandon the system and try something new", "B) Review the trades objectively — 3 losses can happen within normal variance", "C) Double down on the next trade", "D) Stop trading forever"],
                    "correct": "B",
                    "explanation": "Even a 70% win rate system will have 3-loss streaks regularly. Review trades objectively: did you follow the rules? If yes, the losses are normal variance. If no, fix execution, not the system."
                }
            ]
        }
    },
    {
        "id": 7,
        "title": "Building Trading Discipline",
        "category": "Psychology",
        "key_concepts": ["trading plan", "journal", "consistency"],
        "estimated_minutes": 5,
        "exp_reward": 50,
        "ai_generated_quiz": False,
        "momentum_focus": "Creating rules for when to enter and exit fast-moving trades",
        "precision_focus": "Building a checklist system for patient, methodical trade entries",
        "hardcoded_quiz": {
            "momentum": [
                {
                    "question": "Which element is most important in a momentum trader's trading plan?",
                    "options": ["A) What color chart background to use", "B) Clear entry/exit rules with defined risk per trade", "C) Trading as many breakouts as possible", "D) Only trading in the morning"],
                    "correct": "B",
                    "explanation": "A trading plan with clear rules (entry triggers, stop placement, position sizing, exit criteria) prevents emotional decisions during fast-moving markets. Without rules, momentum trading becomes gambling."
                },
                {
                    "question": "Why should momentum traders keep a trading journal?",
                    "options": ["A) To brag about wins", "B) To identify which breakout patterns work best and refine the strategy over time", "C) Journals are only for beginners", "D) To remember how much money was made"],
                    "correct": "B",
                    "explanation": "A journal reveals patterns: which setups have the best win rate, what time of day works, which instruments trend best. Data-driven refinement is how momentum traders improve."
                }
            ],
            "precision": [
                {
                    "question": "A precision trader's pre-trade checklist should include which of the following?",
                    "options": ["A) Only the entry price", "B) Entry, stop loss, take profit, risk/reward ratio, and market structure context", "C) Just the instrument name", "D) How they feel today"],
                    "correct": "B",
                    "explanation": "Precision traders use comprehensive checklists. Every trade should have a clear entry, stop, target, R:R calculation, and context (trend, key levels, session). If any element is missing, skip the trade."
                },
                {
                    "question": "Consistency in precision trading means:",
                    "options": ["A) Taking the same number of trades every day", "B) Following the same process and rules on every trade, even if it means taking zero trades some days", "C) Never changing your strategy", "D) Always trading the same instrument"],
                    "correct": "B",
                    "explanation": "True consistency is process-based, not outcome-based. Some days have no valid setups. Taking zero trades on those days IS being consistent — it means your filter is working."
                }
            ]
        }
    },
    # ── Risk Management (3 modules) ──
    {
        "id": 8,
        "title": "Position Sizing 101",
        "category": "Risk_Management",
        "key_concepts": ["calculate stake", "percentage-based sizing", "2% rule"],
        "estimated_minutes": 4,
        "exp_reward": 50,
        "ai_generated_quiz": False,
        "momentum_focus": "Sizing positions for breakout trades with wider stops",
        "precision_focus": "Sizing positions for tight-stop entries to maximize R-multiples",
        "hardcoded_quiz": {
            "momentum": [
                {
                    "question": "You have a $1000 account and want to risk 2% on a breakout trade. Your stop loss is 50 pips. What should your position size be?",
                    "options": ["A) As much as possible for maximum profit", "B) $20 risk / 50 pips = $0.40 per pip", "C) $100 per pip", "D) It doesn't matter for small accounts"],
                    "correct": "B",
                    "explanation": "2% of $1000 = $20 max risk. Dividing by stop distance (50 pips) gives $0.40/pip. This ensures even if the breakout fails, you only lose 2% — surviving to trade the next setup."
                },
                {
                    "question": "Why do momentum traders typically need wider stops than precision traders?",
                    "options": ["A) They don't — stops should always be tight", "B) Breakout entries have more initial volatility, so tighter stops get hit before the move develops", "C) Wider stops mean more profit", "D) It's just personal preference"],
                    "correct": "B",
                    "explanation": "Breakouts often have a volatile 'shakeout' phase. A stop that's too tight gets clipped before the real move. Wider stops require smaller position sizes to maintain the same dollar risk."
                }
            ],
            "precision": [
                {
                    "question": "A precision trader enters at support with a 10-pip stop and a 30-pip target. With a $500 account risking 1%, what is the position size?",
                    "options": ["A) $5 risk / 10 pips = $0.50 per pip", "B) $50 per pip", "C) Max leverage available", "D) Cannot be calculated"],
                    "correct": "A",
                    "explanation": "1% of $500 = $5. With a tight 10-pip stop, that's $0.50/pip. The tight stop is the precision trader's advantage — it allows good position sizing with high R:R (1:3 here)."
                },
                {
                    "question": "What is the biggest advantage of tight stops for precision traders?",
                    "options": ["A) They never get hit", "B) Smaller dollar risk per trade allows higher R-multiples and more trades before hitting daily limits", "C) They look better in the journal", "D) Brokers prefer tight stops"],
                    "correct": "B",
                    "explanation": "Tight stops = small risk per trade. This means you can achieve 1:3+ R:R ratios even with small account targets, and your daily loss limit allows more opportunities before stopping."
                }
            ]
        }
    },
    {
        "id": 9,
        "title": "Stop Loss Fundamentals",
        "category": "Risk_Management",
        "key_concepts": ["stop placement", "stop hunts", "trailing stops"],
        "estimated_minutes": 5,
        "exp_reward": 50,
        "ai_generated_quiz": False,
        "momentum_focus": "Using trailing stops to lock in profits during trending moves",
        "precision_focus": "Placing stops behind structure for minimal risk",
        "hardcoded_quiz": {
            "momentum": [
                {
                    "question": "During a strong uptrend, when should a momentum trader move their stop loss?",
                    "options": ["A) Never — keep the original stop", "B) Trail it below each new higher low as the trend develops", "C) Remove it once in profit", "D) Move it to break-even immediately after entry"],
                    "correct": "B",
                    "explanation": "Trailing stops below higher lows lets momentum traders stay in winning trends while protecting profits. Each new higher low confirms the trend — your stop follows the trend structure."
                },
                {
                    "question": "Your momentum trade is up +2R but the trend still looks strong. What should you do?",
                    "options": ["A) Close immediately — profit is profit", "B) Trail stop to +1R and let the rest run", "C) Remove stop loss entirely", "D) Add to the position with no stop"],
                    "correct": "B",
                    "explanation": "Locking in +1R via trailing stop means you can't lose on this trade. Letting the remainder run captures extended momentum moves — this is how momentum traders achieve outsized wins."
                }
            ],
            "precision": [
                {
                    "question": "Where should a precision trader place their stop loss on a long entry at support?",
                    "options": ["A) Exactly at the support level", "B) A few pips below the support level, behind the market structure", "C) 100 pips below for safety", "D) No stop needed if the support is strong"],
                    "correct": "B",
                    "explanation": "Stops go behind structure — a few pips below support allows for normal price noise while invalidating the trade idea if support truly breaks. This gives the tightest logical stop."
                },
                {
                    "question": "What is a 'stop hunt' and how should precision traders handle it?",
                    "options": ["A) A myth — it doesn't exist", "B) Price briefly spikes past obvious stop levels before reversing, so place stops slightly beyond obvious levels", "C) Always use mental stops instead", "D) Use no stops to avoid being hunted"],
                    "correct": "B",
                    "explanation": "Stop hunts are real — institutional traders push price past obvious levels to trigger retail stops. Precision traders place stops a few pips beyond the obvious level to survive the spike."
                }
            ]
        }
    },
    {
        "id": 10,
        "title": "Risk:Reward Ratios",
        "category": "Risk_Management",
        "key_concepts": ["1:2 minimum", "R-multiples", "win rate vs R:R"],
        "estimated_minutes": 5,
        "exp_reward": 50,
        "ai_generated_quiz": False,
        "momentum_focus": "Why momentum traders aim for 1:3+ R:R with lower win rates",
        "precision_focus": "Optimizing tight entries for maximum R:R efficiency",
        "hardcoded_quiz": {
            "momentum": [
                {
                    "question": "A momentum trader has a 40% win rate but averages 1:3 R:R. Over 10 trades risking $10 each, what is the expected result?",
                    "options": ["A) Loss of $60", "B) Profit of $20 (4 wins x $30 = $120 minus 6 losses x $10 = $60)", "C) Break even", "D) Cannot be calculated"],
                    "correct": "B",
                    "explanation": "4 wins at 1:3 = $120 gain. 6 losses at $10 = $60 loss. Net = +$60. Even with more losses than wins, the higher R:R makes momentum trading profitable. Win rate isn't everything."
                },
                {
                    "question": "Why do momentum traders accept lower win rates?",
                    "options": ["A) They don't know what they're doing", "B) Because their winning trades produce much larger gains than their losing trades", "C) Low win rates are always bad", "D) They just get unlucky"],
                    "correct": "B",
                    "explanation": "Momentum trading has more false breakouts (losses) but the real breakouts produce extended moves (big wins). A 35-45% win rate with 1:3+ R:R is more profitable than 60% win rate at 1:1."
                }
            ],
            "precision": [
                {
                    "question": "A precision trader risks 10 pips to target 25 pips. What is the Risk:Reward ratio?",
                    "options": ["A) 1:2.5", "B) 2.5:1", "C) 1:10", "D) 1:1"],
                    "correct": "A",
                    "explanation": "Risk:Reward = risk / reward = 10:25 = 1:2.5. This means for every $1 risked, the potential reward is $2.50. Precision traders typically aim for 1:2 minimum."
                },
                {
                    "question": "A precision trader has a 65% win rate with 1:2 R:R. Over 20 trades risking $10 each, what is the expected profit?",
                    "options": ["A) $0", "B) $190 (13 wins x $20 = $260 minus 7 losses x $10 = $70)", "C) $60", "D) $100"],
                    "correct": "B",
                    "explanation": "13 wins at 1:2 = $260. 7 losses at $10 = $70. Net = +$190. High win rate + good R:R = the precision trader's formula. The tight stops enable the favorable ratio."
                }
            ]
        }
    },
    # ── Advanced Strategies (2 modules) ──
    {
        "id": 11,
        "title": "Accumulators Explained",
        "category": "Advanced_Strategies",
        "key_concepts": ["growth rate", "barrier mechanics", "take profit importance"],
        "estimated_minutes": 5,
        "exp_reward": 50,
        "ai_generated_quiz": False,
        "momentum_focus": "Using accumulators to ride momentum with compounding gains",
        "precision_focus": "Setting precise take-profit levels on accumulators to lock gains",
        "hardcoded_quiz": {
            "momentum": [
                {
                    "question": "In an accumulator trade, the growth rate determines how fast your payout grows. As a momentum trader, when do you select a higher growth rate?",
                    "options": ["A) Always — higher growth = more profit", "B) When the market is trending strongly in your favor and you expect continued momentum", "C) When the market is ranging", "D) Higher growth rates have no risk"],
                    "correct": "B",
                    "explanation": "Higher growth rates compound faster but the barrier is closer. In strong trends, momentum traders accept this trade-off. In choppy markets, the closer barrier makes high growth rates dangerous."
                },
                {
                    "question": "What is the biggest risk of accumulator trades for momentum traders?",
                    "options": ["A) Low returns", "B) Hitting the barrier during a sudden reversal — losing all accumulated gains", "C) They're too slow", "D) No risk if the trend is strong"],
                    "correct": "B",
                    "explanation": "Accumulators can hit the barrier on any reversal, wiping out accumulated gains. Momentum traders must set take-profit levels and not get greedy, even when the trend looks strong."
                }
            ],
            "precision": [
                {
                    "question": "A precision trader should set take-profit on an accumulator based on:",
                    "options": ["A) Gut feeling", "B) The next key support/resistance level or a predetermined R-multiple", "C) When they've doubled their money", "D) Never — let it run forever"],
                    "correct": "B",
                    "explanation": "Precision traders use structure. Setting take-profit at the next key level ensures you lock in gains before the market has a natural reason to reverse. Predetermined R-multiples also work."
                },
                {
                    "question": "Why is a lower growth rate often better for precision traders using accumulators?",
                    "options": ["A) It isn't — always use the highest", "B) The barrier is further away, giving more room for normal price fluctuations while still accumulating", "C) Lower growth rates make more money", "D) The platform doesn't allow high rates"],
                    "correct": "B",
                    "explanation": "Lower growth rates place the barrier further from current price. This means normal volatility won't knock out your trade. Precision traders prefer safety margin over rapid compounding."
                }
            ]
        }
    },
    {
        "id": 12,
        "title": "Volatility Indices Basics",
        "category": "Advanced_Strategies",
        "key_concepts": ["V10 vs V100", "synthetic indices", "24/7 availability"],
        "estimated_minutes": 4,
        "exp_reward": 50,
        "ai_generated_quiz": False,
        "momentum_focus": "Trading high-volatility indices (V75, V100) for bigger momentum moves",
        "precision_focus": "Trading low-volatility indices (V10, V25) for cleaner setups",
        "hardcoded_quiz": {
            "momentum": [
                {
                    "question": "Which Volatility Index is best suited for momentum trading and why?",
                    "options": ["A) V10 — slower is always better", "B) V75 or V100 — higher volatility creates stronger trends and breakout opportunities", "C) All volatility indices are the same", "D) V25 — it's the default"],
                    "correct": "B",
                    "explanation": "V75 and V100 have the most price movement, creating strong breakouts and extended trends. Momentum traders need volatility to generate significant moves. The trade-off is wider stops needed."
                },
                {
                    "question": "What is the main advantage of synthetic volatility indices for momentum traders?",
                    "options": ["A) They're always profitable", "B) 24/7 availability and no market close gaps — trends can develop without interruption", "C) They have no risk", "D) Guaranteed returns"],
                    "correct": "B",
                    "explanation": "Unlike forex/stocks, synthetics trade 24/7 with no weekend gaps. This means momentum setups aren't disrupted by market closes, and trends can develop continuously."
                }
            ],
            "precision": [
                {
                    "question": "Why might a precision trader prefer V10 or V25 over V75?",
                    "options": ["A) V10 is more profitable", "B) Lower volatility means cleaner price action, more predictable patterns, and tighter stops", "C) V75 is too expensive", "D) No reason — always use V75"],
                    "correct": "B",
                    "explanation": "V10/V25 have smoother price action with less noise. Patterns are cleaner, support/resistance levels are more reliable, and stops can be tighter — all precision trader advantages."
                },
                {
                    "question": "Synthetic indices differ from forex in that they:",
                    "options": ["A) Are affected by economic news", "B) Use algorithm-generated price movement independent of real-world events", "C) Can only be traded during business hours", "D) Have guaranteed profits"],
                    "correct": "B",
                    "explanation": "Synthetic indices are algorithmically generated — no news events, no central bank surprises. For precision traders, this means technical analysis is the primary edge, as patterns are driven purely by price mechanics."
                }
            ]
        }
    },
]

# Category ordering per trader type
CATEGORY_ORDER = {
    "momentum": ["Technical_Analysis", "Risk_Management", "Psychology", "Advanced_Strategies"],
    "precision": ["Technical_Analysis", "Psychology", "Risk_Management", "Advanced_Strategies"],
}


class ModuleContentGenerator:
    """Generates educational module content using AI, personalized by trader type."""

    def __init__(self):
        self.settings = get_ai_settings()
        self.anthropic_client = Anthropic(api_key=self.settings.anthropic_api_key)

    def get_all_modules(self, trader_type: str = "momentum") -> List[Dict]:
        """Return all module metadata ordered by trader type preference."""
        order = CATEGORY_ORDER.get(trader_type, CATEGORY_ORDER["momentum"])
        sorted_modules = sorted(MODULES, key=lambda m: (
            order.index(m["category"]) if m["category"] in order else 99,
            m["id"]
        ))
        return [
            {
                "id": m["id"],
                "title": m["title"],
                "category": m["category"],
                "key_concepts": m["key_concepts"],
                "estimated_minutes": m["estimated_minutes"],
                "exp_reward": m["exp_reward"],
                "focus": m.get(f"{trader_type}_focus", m.get("momentum_focus", "")),
            }
            for m in sorted_modules
        ]

    def get_hardcoded_quiz(self, module_id: int, trader_type: str = "momentum") -> Optional[List[Dict]]:
        """Get hardcoded quiz questions for a module by trader type."""
        module = next((m for m in MODULES if m["id"] == module_id), None)
        if not module or module.get("ai_generated_quiz"):
            return None
        quiz_data = module.get("hardcoded_quiz", {})
        return quiz_data.get(trader_type, quiz_data.get("momentum", []))

    async def generate_module(
        self,
        title: str,
        category: str,
        difficulty: str,
        target_concepts: List[str],
        trader_type: str = "momentum",
    ) -> Dict:
        """
        Generate complete module content with AI, personalized for trader type.

        Args:
            title: Module title
            category: Module category
            difficulty: beginner, intermediate, advanced
            target_concepts: Key concepts to cover
            trader_type: "momentum" or "precision"

        Returns:
            Dict with content_json and quiz_questions_json
        """
        module = next((m for m in MODULES if m["title"] == title), None)
        focus = ""
        if module:
            focus = module.get(f"{trader_type}_focus", "")

        system_prompt = self._build_module_system_prompt(trader_type, focus)
        user_prompt = self._build_module_user_prompt(title, category, difficulty, target_concepts)

        try:
            response = await asyncio.to_thread(
                self.anthropic_client.messages.create,
                model=self.settings.anthropic_model_name,
                max_tokens=4000,
                system=system_prompt,
                messages=[{"role": "user", "content": user_prompt}],
            )

            content_text = response.content[0].text
            module_data = self._parse_module_response(content_text)

            logger.info(f"Generated module: {title} (trader_type={trader_type})")
            return module_data

        except Exception as e:
            logger.error(f"Error generating module {title}: {e}")
            raise

    def _build_module_system_prompt(self, trader_type: str = "momentum", focus: str = "") -> str:
        trader_desc = {
            "momentum": "a momentum/breakout trader who values fast entries, trend-following, and riding moves",
            "precision": "a precision/reversal trader who values patience, clean setups, and tight risk management",
        }
        desc = trader_desc.get(trader_type, trader_desc["momentum"])
        focus_line = f"\nTAILOR FOCUS: {focus}" if focus else ""

        return f"""You are an expert trading educator creating micro-lessons for traders.
The student is {desc}.{focus_line}

Your content must be:
1. **Accurate**: Use reliable sources (Investopedia, Babypips, TradingView Education)
2. **Clear**: ELI5 explanations that anyone can understand
3. **Practical**: Real examples tailored to {trader_type} trading style
4. **Safe**: NEVER promise profits, always emphasize risk

MODULE STRUCTURE:
- 4 sections: Introduction, Core Concept, Practical Application, Common Mistakes
- Each section: 150-200 words
- Total reading time: 3-5 minutes
- 2 quiz questions with explanations, tailored to {trader_type} trader perspective

QUIZ GUIDELINES:
- Question 1: Test understanding of core concept from a {trader_type} trader perspective
- Question 2: Test practical application for {trader_type} trading
- 4 options per question (A, B, C, D)
- Detailed explanation for correct answer

OUTPUT FORMAT:
Return ONLY valid JSON with this structure:
{{
  "sections": [
    {{"title": "...", "content": "...", "type": "introduction"}},
    {{"title": "...", "content": "...", "type": "concept"}},
    {{"title": "...", "content": "...", "type": "application"}},
    {{"title": "...", "content": "...", "type": "mistakes"}}
  ],
  "key_takeaways": ["...", "...", "..."],
  "quiz_questions": [
    {{
      "question": "...",
      "options": ["A) ...", "B) ...", "C) ...", "D) ..."],
      "correct": "B",
      "explanation": "..."
    }}
  ],
  "sources": ["Source 1", "Source 2"]
}}

CRITICAL:
- NO markdown code blocks, just raw JSON
- NO financial advice or guarantees
- ALL explanations use simple language
- Tailor ALL examples to {trader_type} trading scenarios
"""

    def _build_module_user_prompt(
        self,
        title: str,
        category: str,
        difficulty: str,
        target_concepts: List[str],
    ) -> str:
        concepts_str = ", ".join(target_concepts)
        return f"""Create a complete educational module:

**Module Title**: {title}
**Category**: {category}
**Difficulty Level**: {difficulty}
**Key Concepts to Cover**: {concepts_str}

Generate 4 sections (Introduction, Core Concept, Practical Application, Common Mistakes),
3-4 key takeaways, 2 quiz questions, and 2-3 sources. Return valid JSON only."""

    def _parse_module_response(self, response_text: str) -> Dict:
        """Parse and validate module response."""
        try:
            cleaned = response_text.strip()
            if cleaned.startswith("```json"):
                cleaned = cleaned[7:]
            if cleaned.startswith("```"):
                cleaned = cleaned[3:]
            if cleaned.endswith("```"):
                cleaned = cleaned[:-3]
            cleaned = cleaned.strip()

            data = json.loads(cleaned)

            required_keys = ["sections", "key_takeaways", "quiz_questions"]
            for key in required_keys:
                if key not in data:
                    raise ValueError(f"Missing required key: {key}")

            if len(data.get("quiz_questions", [])) != 2:
                logger.warning(f"Expected 2 quiz questions, got {len(data.get('quiz_questions', []))}")

            return {
                "content_json": json.dumps(
                    data["sections"] + [{"type": "takeaways", "content": data["key_takeaways"]}]
                ),
                "quiz_questions_json": json.dumps(data["quiz_questions"][:2]),
                "sources": data.get("sources", []),
            }

        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse module JSON: {e}")
            logger.error(f"Response text: {response_text[:500]}")
            raise ValueError(f"Invalid JSON response from AI: {e}")


# Singleton instance
_generator: Optional[ModuleContentGenerator] = None


def get_module_generator() -> ModuleContentGenerator:
    """Get singleton instance."""
    global _generator
    if _generator is None:
        _generator = ModuleContentGenerator()
    return _generator
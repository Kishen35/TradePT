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

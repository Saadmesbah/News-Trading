# analysis/score.py
from config import NEWS_WEIGHT, TA_WEIGHT, BUY_THRESHOLD, SELL_THRESHOLD


def calculate_composite_score(sentiment: dict, ta: dict) -> dict:
    """
    Combines sentiment + technical analysis into one final score.

    Formula:
        news_score = weighted average of 4 sentiment categories
        P = news_score × 0.7 + ta_score × 0.3

    Returns the score + signal + full breakdown.
    """

    # ── News Score ────────────────────────────────────────
    # Weighted average of the 4 LLM sentiment scores
    # Bitcoin gets highest weight (most direct impact)
    news_score = round(
        sentiment.get("bitcoin_score",   0) * 0.40 +
        sentiment.get("crypto_score",    0) * 0.20 +
        sentiment.get("politics_score",  0) * 0.20 +
        sentiment.get("war_macro_score", 0) * 0.20,
        4
    )

    # ── TA Score ──────────────────────────────────────────
    ta_score = ta.get("ta_score", 0.0)

    # ── Final P Score ─────────────────────────────────────
    p_score = round(
        news_score * NEWS_WEIGHT +
        ta_score   * TA_WEIGHT,
        4
    )

    # Clamp between -1 and 1
    p_score = max(-1.0, min(1.0, p_score))

    # ── Signal ────────────────────────────────────────────
    if p_score >= BUY_THRESHOLD:
        signal = "BUY"
    elif p_score <= SELL_THRESHOLD:
        signal = "SELL"
    else:
        signal = "HOLD"

    # ── Confidence ───────────────────────────────────────
    # How far is P from 0? Higher = more confident
    confidence = round(abs(p_score), 4)

    if confidence >= 0.7:
        confidence_label = "HIGH"
    elif confidence >= 0.4:
        confidence_label = "MEDIUM"
    else:
        confidence_label = "LOW"

    return {
        # Inputs
        "bitcoin_score":   sentiment.get("bitcoin_score",   0),
        "crypto_score":    sentiment.get("crypto_score",    0),
        "politics_score":  sentiment.get("politics_score",  0),
        "war_macro_score": sentiment.get("war_macro_score", 0),
        "news_score":      news_score,
        "ta_score":        ta_score,
        "rsi":             ta.get("rsi", 50.0),
        "support":         ta.get("support", 0.0),
        "resistance":      ta.get("resistance", 0.0),
        "current_price":   ta.get("current_price", 0.0),

        # Output
        "p_score":          p_score,
        "signal":           signal,
        "confidence":       confidence,
        "confidence_label": confidence_label,
        "rationale":        sentiment.get("brief_rationale", ""),
    }


def print_score_report(result: dict):
    """Pretty print the full analysis report."""

    signal_colors = {
        "BUY":  "🟢",
        "SELL": "🔴",
        "HOLD": "🟡"
    }
    icon = signal_colors.get(result["signal"], "⚪")

    print("\n" + "="*50)
    print("       TRADING BOT — SIGNAL REPORT")
    print("="*50)

    print("\n📰 SENTIMENT SCORES")
    print(f"  Bitcoin   : {result['bitcoin_score']:+.4f}")
    print(f"  Crypto    : {result['crypto_score']:+.4f}")
    print(f"  Politics  : {result['politics_score']:+.4f}")
    print(f"  War/Macro : {result['war_macro_score']:+.4f}")
    print(f"  ── News Score : {result['news_score']:+.4f}")

    print("\n📊 TECHNICAL ANALYSIS")
    print(f"  Price      : ${result['current_price']:,.2f}")
    print(f"  RSI        : {result['rsi']}")
    print(f"  Support    : ${result['support']:,.2f}")
    print(f"  Resistance : ${result['resistance']:,.2f}")
    print(f"  ── TA Score : {result['ta_score']:+.4f}")

    print("\n⚡ COMPOSITE SCORE")
    print(f"  P = News×{NEWS_WEIGHT} + TA×{TA_WEIGHT}")
    print(f"  P = {result['news_score']:+.4f}×{NEWS_WEIGHT} + {result['ta_score']:+.4f}×{TA_WEIGHT}")
    print(f"  P = {result['p_score']:+.4f}")

    print(f"\n  Confidence : {result['confidence_label']} ({result['confidence']:.2f})")
    print(f"  Rationale  : {result['rationale']}")

    print(f"\n{'='*50}")
    print(f"  {icon}  SIGNAL : {result['signal']}")
    print(f"{'='*50}\n")


# ── Test ──────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    # Simulated inputs to test the scoring logic
    fake_sentiment = {
        "bitcoin_score":   0.68,
        "crypto_score":    0.34,
        "politics_score":  -0.18,
        "war_macro_score": -0.52,
        "brief_rationale": "Strong ETF inflows offset by geopolitical tensions."
    }

    fake_ta = {
        "current_price": 103450.0,
        "rsi":           42.5,
        "rsi_score":     0.1875,
        "support":       101200.0,
        "resistance":    105800.0,
        "sr_score":      0.125,
        "ta_score":      0.156,
    }

    result = calculate_composite_score(fake_sentiment, fake_ta)
    print_score_report(result)
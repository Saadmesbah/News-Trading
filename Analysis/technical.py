# analysis/technical.py
from data.price import fetch_candles
from config import SYMBOL


# ── RSI ───────────────────────────────────────────────────────────────────────

def calculate_rsi(candles: list, period: int = 14) -> float:
    """
    RSI < 30 → Oversold  → Bullish
    RSI > 70 → Overbought → Bearish
    """
    if len(candles) < period + 1:
        return 50.0

    closes = [c["close"] for c in candles]
    deltas = [closes[i] - closes[i - 1] for i in range(1, len(closes))]

    gains  = [d if d > 0 else 0 for d in deltas]
    losses = [-d if d < 0 else 0 for d in deltas]

    avg_gain = sum(gains[:period]) / period
    avg_loss = sum(losses[:period]) / period

    for i in range(period, len(gains)):
        avg_gain = (avg_gain * (period - 1) + gains[i]) / period
        avg_loss = (avg_loss * (period - 1) + losses[i]) / period

    if avg_loss == 0:
        return 100.0

    rs  = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    return round(rsi, 2)


# ── Support & Resistance ──────────────────────────────────────────────────────

def find_support_resistance(candles: list, window: int = 5) -> dict:
    """
    Detect S/R levels using pivot points.
    Looks for local highs (resistance) and local lows (support)
    within a rolling window of candles.
    """
    highs = [c["high"] for c in candles]
    lows  = [c["low"]  for c in candles]

    pivot_highs = []
    pivot_lows  = []

    for i in range(window, len(candles) - window):
        if highs[i] == max(highs[i - window: i + window + 1]):
            pivot_highs.append(highs[i])
        if lows[i] == min(lows[i - window: i + window + 1]):
            pivot_lows.append(lows[i])

    current_price = candles[-1]["close"]

    resistance = min(
        [h for h in pivot_highs if h > current_price],
        default=max(pivot_highs, default=current_price)
    )
    support = max(
        [l for l in pivot_lows if l < current_price],
        default=min(pivot_lows, default=current_price)
    )

    return {
        "support":    round(support, 2),
        "resistance": round(resistance, 2),
    }


# ── TA Score ──────────────────────────────────────────────────────────────────

def calculate_ta_score(candles: list) -> dict:
    """
    Combines RSI + S/R into a single score [-1.0, +1.0].

    RSI score  → momentum signal
    S/R score  → position between support and resistance
    TA score   = RSI_score × 0.5 + SR_score × 0.5
    """
    if not candles:
        return _neutral()

    current_price = candles[-1]["close"]
    rsi           = calculate_rsi(candles)
    levels        = find_support_resistance(candles)
    support       = levels["support"]
    resistance    = levels["resistance"]

    # RSI score
    if rsi < 30:
        rsi_score = 0.5
    elif rsi > 70:
        rsi_score = -0.5
    else:
        rsi_score = round((50 - rsi) / 40, 4)

    # S/R score
    price_range = resistance - support
    if price_range <= 0:
        sr_score = 0.0
    else:
        position = (current_price - support) / price_range
        sr_score = round(0.5 - position, 4)

    sr_score = max(-0.5, min(0.5, sr_score))

    # Final TA score
    ta_score = round(rsi_score * 0.5 + sr_score * 0.5, 4)
    ta_score = max(-1.0, min(1.0, ta_score))

    return {
        "current_price": round(current_price, 2),
        "rsi":           rsi,
        "rsi_score":     rsi_score,
        "support":       support,
        "resistance":    resistance,
        "sr_score":      sr_score,
        "ta_score":      ta_score,
    }


def _neutral():
    return {
        "current_price": 0.0,
        "rsi":           50.0,
        "rsi_score":     0.0,
        "support":       0.0,
        "resistance":    0.0,
        "sr_score":      0.0,
        "ta_score":      0.0,
    }


# ── Test ──────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    candles = fetch_candles()

    if candles:
        result = calculate_ta_score(candles)

        print("📊 TECHNICAL ANALYSIS RESULT")
        print("─" * 35)
        print(f"  💰 Price      : ${result['current_price']:,.2f}")
        print(f"  📈 RSI        : {result['rsi']} → {result['rsi_score']:+.4f}")
        print(f"  🟢 Support    : ${result['support']:,.2f}")
        print(f"  🔴 Resistance : ${result['resistance']:,.2f}")
        print(f"  📐 S/R Score  : {result['sr_score']:+.4f}")
        print(f"  ⚡ TA Score   : {result['ta_score']:+.4f}")
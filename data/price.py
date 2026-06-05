# data/price.py
import requests
from datetime import datetime, timezone
from config import SYMBOL, INTERVAL, CANDLE_LIMIT


def fetch_candles(symbol: str = SYMBOL, interval: str = INTERVAL, limit: int = CANDLE_LIMIT) -> list:
    """
    Fetch OHLCV candlestick data from Binance public API.
    No API key required.

    Returns a list of dicts:
    [
        {
            "timestamp": "2026-05-02T09:00:00+00:00",
            "open":  67000.0,
            "high":  67500.0,
            "low":   66800.0,
            "close": 67200.0,
            "volume": 1234.5
        },
        ...
    ]
    """
    try:
        response = requests.get(
            "https://api.binance.com/api/v3/klines",
            params={
                "symbol":   symbol,
                "interval": interval,
                "limit":    limit
            },
            timeout=10
        )
        response.raise_for_status()
        raw = response.json()

        candles = []
        for c in raw:
            candles.append({
                "timestamp": datetime.fromtimestamp(c[0] / 1000, tz=timezone.utc).isoformat(),
                "open":      float(c[1]),
                "high":      float(c[2]),
                "low":       float(c[3]),
                "close":     float(c[4]),
                "volume":    float(c[5]),
            })

        print(f"✅ Fetched {len(candles)} candles — {symbol} {interval}")
        print(f"   Latest close : ${candles[-1]['close']:,.2f}")
        print(f"   Latest time  : {candles[-1]['timestamp']}\n")
        return candles

    except requests.exceptions.Timeout:
        print("❌ Binance API timed out.")
        return []

    except requests.exceptions.RequestException as e:
        print(f"❌ Binance API error: {e}")
        return []


def get_current_price(symbol: str = SYMBOL) -> float:
    """
    Fetch the current BTC price in USD (single ticker call).
    Faster than fetching full candles when you just need the price.
    """
    try:
        response = requests.get(
            "https://api.binance.com/api/v3/ticker/price",
            params={"symbol": symbol},
            timeout=10
        )
        response.raise_for_status()
        price = float(response.json()["price"])
        print(f"✅ Current {symbol} price: ${price:,.2f}")
        return price

    except requests.exceptions.RequestException as e:
        print(f"❌ Failed to fetch current price: {e}")
        return 0.0


# ── Test ──────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    # Test 1 — current price
    price = get_current_price()

    # Test 2 — full candles
    candles = fetch_candles()

    if candles:
        closes = [c["close"] for c in candles]
        print(f"   High (100 candles) : ${max(closes):,.2f}")
        print(f"   Low  (100 candles) : ${min(closes):,.2f}")
        print(f"   Avg  (100 candles) : ${sum(closes)/len(closes):,.2f}")
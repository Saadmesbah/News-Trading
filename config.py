import os
from dotenv import load_dotenv

load_dotenv()

# ── Binance ───────────────────────────────────────────────
SYMBOL      = "BTCUSDT"
INTERVAL    = "1h"        # candle timeframe
CANDLE_LIMIT = 100        # how many candles to fetch

# ── Signal Thresholds ─────────────────────────────────────
BUY_THRESHOLD  =  0.55    # P > 0.55  → BUY
SELL_THRESHOLD = -0.55    # P < -0.55 → SELL
# anything in between    → HOLD

# ── Formula Weights ───────────────────────────────────────
NEWS_WEIGHT = 0.7
TA_WEIGHT   = 0.3

# ── Risk Management ───────────────────────────────────────
CAPITAL          = 1000.0  # total capital in USD (paper trading)
RISK_PER_TRADE   = 0.02    # risk 2% of capital per trade
STOP_LOSS_PCT    = 0.02    # stop-loss 2% below entry
TAKE_PROFIT_PCT  = 0.04    # take-profit 4% above entry (2:1 ratio)

# ── LLM (OpenRouter) ──────────────────────────────────────
OPENROUTER_KEY = os.getenv("OPENROUTER_KEY")
LLM_MODEL      = "meta-llama/llama-3.3-70b-instruct:free"

# ── Telegram ──────────────────────────────────────────────
TELEGRAM_TOKEN   = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

# ── Database ──────────────────────────────────────────────
DB_PATH = "storage/trading_bot.db"

# ── Scheduler ─────────────────────────────────────────────
RUN_INTERVAL_HOURS = 1    # run every 1 hour
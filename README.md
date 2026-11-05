#  Crypto Sentiment Trading Bot

An end-to-end automated trading bot that combines **AI-powered news sentiment analysis** with **technical analysis** to generate BTC trading signals in real time.

---

## Research and backtesting

**[Explore the executed research notebook](notebooks/trading_strategy_research_recent.ipynb)** · [Methods, data and reproduction](notebooks/README_recent.md)

The research studies **192 BTC signal observations from September 24 to October 31, 2026**, with frozen hourly Binance prices. It includes score/price charts, forward-return correlations, separate news and technical score studies, threshold/holding-period comparisons, and **21 news/technical weight combinations**. Exported HOLD labels are collection placeholders; the experiments use continuous scores.

![Earlier/later weight comparison](notebooks/results_recent/recent_weight_comparison.png)

For the fixed 24-hour long/short comparison:

| News / technical weight | Earlier return | Later return | Later trades |
|---|---:|---:|---:|
| 5 / 95 (selected on earlier data) | +2.82% | -4.66% | 4 |
| 70 / 30 (original mix) | +1.36% | +4.57% | 5 |
| 95 / 5 (highest later return, hindsight) | -1.25% | +6.26% | 6 |

Each mix uses its own threshold selected on earlier data. The earlier winner failed later, and selecting the highest later return would use hindsight. All selected buying-only mixes lost in the later segment. **This small, repeatedly inspected sample does not establish a reliable trading edge or a better replacement for 70/30.**

Returns include modeled fees and slippage, without leverage, funding or liquidation. These research simulations use their own fixed-hold rules; they do not validate the bot's stop-loss/take-profit behavior. The notebook includes the full assumptions and limitations.

---

## How It Works

```
Every hour (automated):

1. 📰 Fetch 400 crypto/BTC/political/macro news headlines
2. 🧹 Clean & deduplicate headlines (fuzzy matching)
3. 🧠 Analyze sentiment via LLM (Llama 3.3 70B)
4. 📊 Calculate RSI + Support/Resistance from Binance
5. ⚡ Compute composite score: P = News×0.7 + TA×0.3
6. 🚦 Generate signal: BUY / SELL / HOLD
7. 💾 Save to SQLite database
8. 📱 Send alert to Telegram
```

---

## Signal Formula

```
P = News Score × 0.7 + Technical Score × 0.3

News Score    = BTC×0.40 + Crypto×0.20 + Politics×0.20 + Macro×0.20
TA Score      = RSI Score×0.5 + Support/Resistance Score×0.5

P > +0.55  → BUY
P < -0.55  → SELL
else       → HOLD
```

---

## Project Structure

```
├── Analysis/
│   ├── SentimentAnalysis.py   # LLM sentiment scoring
│   ├── technical.py           # RSI + Support/Resistance
│   └── score.py               # P = News×0.7 + TA×0.3
├── bot/
│   └── risk.py                # Position sizing, stop-loss, take-profit
├── Cleaning/
│   └── Cleaning.py            # Regex cleaning + deduplication
├── data/
│   └── price.py               # Binance OHLCV fetcher
├── News/
│   └── NewsScrap.py           # Google News RSS scraper
├── notify/
│   └── telegram.py            # Telegram bot notifications
├── storage/
│   └── database.py            # SQLite — signals + paper trades
├── config.py                  # All settings in one place
└── main.py                    # Orchestrates full pipeline
```

---

## Setup

**1. Clone the repo**
```bash
git clone https://github.com/Saadmesbah/News-Trading.git
cd News-Trading
```

**2. Create virtual environment**
```bash
python -m venv .venv
.venv\Scripts\activate   # Windows
source .venv/bin/activate # Mac/Linux
```

**3. Install dependencies**
```bash
pip install -r requirements.txt
```

**4. Configure `.env`**
```bash
cp .env.example .env
# Fill in your API keys
```

**5. Run the bot**
```bash
python main.py
```

---

## Environment Variables

Create a `.env` file with:

```env
OPENROUTER_KEY=your_openrouter_api_key
TELEGRAM_TOKEN=your_telegram_bot_token
TELEGRAM_CHAT_ID=your_telegram_chat_id
```

Get your keys:
- **OpenRouter** → https://openrouter.ai
- **Telegram Bot** → @BotFather on Telegram

---

## Risk Management

| Parameter | Value |
|---|---|
| Capital | $1,000 (configurable) |
| Risk per trade | 2% |
| Stop-loss | 2% or nearest support |
| Take-profit | 4% (2:1 risk/reward) |

---

## Tech Stack

| Layer | Technology |
|---|---|
| Language | Python 3.11+ |
| News | Google News RSS + feedparser |
| Sentiment | Llama 3.3 70B via OpenRouter API |
| Price Data | Binance Public API |
| Database | SQLite |
| Notifications | Telegram Bot API |
| Scheduler | schedule |

---

## Author

**Mesbah Saad** — Data Science Student @ ESI  
[LinkedIn](https://linkedin.com/in/saad-mesbah-623466273) · [GitHub](https://github.com/Saadmesbah)
# main.py
import time
import schedule
from datetime import datetime, timezone

from config import SYMBOL, RUN_INTERVAL_HOURS

# Data
from data.price import fetch_candles, get_current_price
from News.NewsScrap import fetch_news
from Cleaning.Cleaning import clean_news_file_similarity

# Analysis
from Analysis.SentimentAnalysis import get_sentiment_score
from Analysis.technical import calculate_ta_score
from Analysis.score import calculate_composite_score, print_score_report

# Bot
from bot.risk import calculate_risk, print_risk_report

# Storage
from storage.database import (
    create_tables, save_signal,
    open_paper_trade, get_trade_summary
)

# Notify
from notify.telegram import send_signal, send_trade_opened


# ── Helpers ───────────────────────────────────────────────

def get_todays_files():
    """Return the file paths for today's news."""
    date = datetime.now().strftime("%Y-%m-%d")
    raw   = f"News/Cache/news_{date}.txt"
    clean = f"Cleaning/news_{date}_final.txt"
    return raw, clean


# ── Core Pipeline ─────────────────────────────────────────

def run_pipeline():
    print("\n" + "="*50)
    print(f"  BOT RUN — {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*50 + "\n")

    # ── Step 1: Fetch News ────────────────────────────────
    print("📰 STEP 1 — Fetching news...\n")
    raw_file, clean_file = get_todays_files()

    fetch_news("crypto%20when%3A1d")
    fetch_news("Bitcoin%20when%3A1d")
    fetch_news("war%20when%3A1d", x=20)
    fetch_news("politics%20when%3A1d", x=20)

    # ── Step 2: Clean Headlines ───────────────────────────
    print("\n🧹 STEP 2 — Cleaning headlines...\n")
    clean_news_file_similarity(raw_file, clean_file)

    try:
        with open(clean_file, 'r', encoding='utf-8') as f:
            lines = [l.strip() for l in f.readlines() if l.strip()]
        full_text = "\n".join(lines)
        print(f"✅ {len(lines)} unique headlines ready\n")
    except FileNotFoundError:
        print(f"❌ Clean file not found: {clean_file}")
        return

    # ── Step 3: Sentiment Analysis ────────────────────────
    print("🧠 STEP 3 — Sentiment analysis...\n")
    sentiment = get_sentiment_score(full_text)

    if not sentiment:
        print("❌ Sentiment analysis failed — aborting.")
        return

    # ── Step 4: Technical Analysis ────────────────────────
    print("📊 STEP 4 — Technical analysis...\n")
    candles = fetch_candles()

    if not candles:
        print("❌ Could not fetch candles — aborting.")
        return

    ta = calculate_ta_score(candles)

    # ── Step 5: Composite Score ───────────────────────────
    print("⚡ STEP 5 — Calculating P score...\n")
    score = calculate_composite_score(sentiment, ta)
    print_score_report(score)

    # ── Step 6: Risk Management ───────────────────────────
    print("🛡️  STEP 6 — Risk management...\n")
    risk = calculate_risk(
        signal=score["signal"],
        current_price=score["current_price"],
        support=score["support"],
        resistance=score["resistance"]
    )
    print_risk_report(risk)

    # ── Step 7: Save to Database ──────────────────────────
    print("💾 STEP 7 — Saving to database...\n")
    save_signal(score, risk)

    if score["signal"] != "HOLD":
        trade_id = open_paper_trade(risk)

    # ── Step 8: Telegram Notification ────────────────────
    print("📱 STEP 8 — Sending Telegram notification...\n")
    send_signal(score, risk)

    if score["signal"] != "HOLD":
        send_trade_opened(risk)

    # ── Done ──────────────────────────────────────────────
    print("\n" + "="*50)
    print("  ✅ PIPELINE COMPLETE")
    print("="*50)

    # Print trade summary
    summary = get_trade_summary()
    if summary["total_trades"] > 0:
        print(f"\n📊 OVERALL PERFORMANCE")
        print(f"  Trades  : {summary['total_trades']}")
        print(f"  Win Rate: {summary['win_rate']}%")
        print(f"  Total P&L: ${summary['total_pnl']:+.2f}\n")


# ── Scheduler ─────────────────────────────────────────────

def run_bot():
    """
    Run once immediately then schedule every X hours.
    """
    # Initialize database
    create_tables()

    # Run immediately on start
    run_pipeline()

    # Schedule recurring runs
    schedule.every(RUN_INTERVAL_HOURS).hours.do(run_pipeline)

    print(f"\n⏰ Bot scheduled — runs every {RUN_INTERVAL_HOURS} hour(s).")
    print("   Press Ctrl+C to stop.\n")

    while True:
        schedule.run_pending()
        time.sleep(60)  # check every minute


# ── Entry Point ───────────────────────────────────────────

if __name__ == "__main__":
    run_bot()
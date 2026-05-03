from datetime import datetime
import os
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from News.NewsScrap import fetch_news
from Cleaning.Cleaning import clean_news_file_similarity
from Analysis.SentimentAnalysis import get_sentiment_score
from Database.elastic import create_index, save_sentiment

def run_pipeline(asset: str = "BTC"):
    print("\n" + "="*50)
    print(f"  TRADING BOT PIPELINE — {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print("="*50 + "\n")

    # ── Step 1: Fetch News ────────────────────────────────
    print("📰 STEP 1 — Fetching news...\n")
    timestamp = datetime.now().strftime("%Y-%m-%d")
    raw_file  = f"News/Cache/news_{timestamp}.txt"
    clean_file = f"Cleaning/news_{timestamp}_final.txt"

    fetch_news("crypto%20when%3A1d")
    fetch_news("Bitcoin%20when%3A1d")
    fetch_news("war%20when%3A1d", x=20)
    fetch_news("politics%20when%3A1d", x=20)

    # ── Step 2: Clean & Deduplicate ───────────────────────
    print("\n🧹 STEP 2 — Cleaning and deduplicating...\n")
    clean_news_file_similarity(raw_file, clean_file)

    # ── Step 3: Read cleaned headlines ───────────────────
    try:
        with open(clean_file, 'r', encoding='utf-8') as f:
            lines = [line.strip() for line in f.readlines() if line.strip()]
    except FileNotFoundError:
        print(f"❌ Cleaned file not found: {clean_file}")
        return

    headline_count = len(lines)
    full_text = "\n".join(lines)
    print(f"✅ {headline_count} unique headlines ready for analysis\n")

    # ── Step 4: Sentiment Analysis ────────────────────────
    print("🧠 STEP 3 — Running sentiment analysis...\n")
    scores = get_sentiment_score(full_text)

    if not scores:
        print("❌ Sentiment analysis failed. Aborting.")
        return

    print(f"  Bitcoin   : {scores['bitcoin_score']}")
    print(f"  Crypto    : {scores['crypto_score']}")
    print(f"  Politics  : {scores['politics_score']}")
    print(f"  War/Macro : {scores['war_macro_score']}")
    print(f"  Rationale : {scores['brief_rationale']}\n")

    # ── Step 5: Save to Elasticsearch ────────────────────
    print("💾 STEP 4 — Saving to Elasticsearch...\n")
    create_index()
    doc_id = save_sentiment(
        scores=scores,
        headlines=lines,
        asset=asset
    )

    print(f"\n{'='*50}")
    print(f"  ✅ PIPELINE COMPLETE — Document ID: {doc_id}")
    print(f"{'='*50}\n")


if __name__ == "__main__":
    run_pipeline(asset="BTC")
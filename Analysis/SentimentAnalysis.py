import requests
import json
import os
import re
from dotenv import load_dotenv

load_dotenv()  # ✅ Must be BEFORE os.getenv()
my_key = os.getenv("OPENROUTER_KEY")

SYSTEM_PROMPT = """
Role: You are a Senior Quantitative Analyst specializing in cryptocurrency markets and global macroeconomics.

Task: Analyze the provided news headlines and return a JSON sentiment scoring object for Bitcoin (BTC).

Scoring Rules:
- bitcoin_score : Direct BTC news (ETF flows, whale moves, protocol updates). Weight this MOST heavily.
- crypto_score  : Broader crypto market news (altcoins, exchange hacks, regulations).
- politics_score: Government bills, elections, regulatory decisions affecting finance.
- war_macro_score: Geopolitical conflicts, CPI data, Fed rate decisions. Usually negative for risk assets.

Each score is a float from -1.0 (Extremely Bearish) to +1.0 (Extremely Bullish). Use 0.0 if no relevant news exists for that category.

IMPORTANT: Your response must be ONLY this JSON object, no extra text, no markdown, no backticks:
{
  "bitcoin_score": <float>,
  "crypto_score": <float>,
  "politics_score": <float>,
  "war_macro_score": <float>,
  "brief_rationale": "<one sentence>"
}
"""

def parse_json_response(raw_text):
    """
    Safely extract and parse JSON from LLM response.
    Handles cases where the LLM adds extra text around the JSON.
    """
    try:
        # First try direct parse (best case — LLM followed instructions)
        return json.loads(raw_text)

    except json.JSONDecodeError:
        # Fallback: find the JSON block inside the text using regex
        match = re.search(r'\{.*?\}', raw_text, re.DOTALL)
        if match:
            try:
                return json.loads(match.group())
            except json.JSONDecodeError:
                pass

    # If all parsing fails, return a neutral default
    print("⚠️ Could not parse JSON from LLM response. Returning neutral scores.")
    print(f"   Raw response was: {raw_text[:200]}")  # Show first 200 chars for debugging
    return {
        "bitcoin_score": 0.0,
        "crypto_score": 0.0,
        "politics_score": 0.0,
        "war_macro_score": 0.0,
        "brief_rationale": "Parsing failed — defaulting to neutral."
    }

def clamp_scores(data):
    """
    Make sure all scores are within [-1.0, 1.0].
    Protects against LLM hallucinating values like 1.5 or -2.
    """
    score_keys = ["bitcoin_score", "crypto_score", "politics_score", "war_macro_score"]
    for key in score_keys:
        if key in data:
            data[key] = max(-1.0, min(1.0, float(data[key])))
    return data

def get_sentiment_score(headline):
    """
    Send headlines to LLM and return a structured sentiment dict.
    """
    if not headline or not headline.strip():
        print("⚠️ Empty headline passed, skipping.")
        return None

    try:
        response = requests.post(
            url="https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {my_key}",
                "Content-Type": "application/json"
            },
            data=json.dumps({
                "model": "openai/gpt-oss-120b:free",
                "messages": [
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user",   "content": headline}
                ]
            }),
            timeout=15
        )

        response.raise_for_status()  # Catches 4xx and 5xx HTTP errors

        result = response.json()
        raw_text = result['choices'][0]['message']['content']

        parsed = parse_json_response(raw_text)
        clamped = clamp_scores(parsed)
        return clamped

    except requests.exceptions.Timeout:
        print("❌ API request timed out.")
        return None

    except requests.exceptions.RequestException as e:
        print(f"❌ Network/API error: {e}")
        return None

    except (KeyError, IndexError) as e:
        print(f"❌ Unexpected API response format: {e}")
        return None


# ── Main ──────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    filepath = 'Cleaning/news_2026-03-30_final.txt'  # Use the final cleaned file

    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            headline = f.read().strip()
    except FileNotFoundError:
        print(f"❌ File not found: {filepath}")
        print("   Make sure you ran NewsScrap.py and Cleaning.py first.")
        exit(1)

    print("🔍 Analyzing sentiment...\n")
    scores = get_sentiment_score(headline)

    if scores:
        print(json.dumps(scores, indent=2))

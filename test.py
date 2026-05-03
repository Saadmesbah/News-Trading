import requests
import json
import os
from dotenv import load_dotenv

load_dotenv()
my_key = os.getenv("OPENROUTER_KEY")

def test_api():
    print("🔍 Testing OpenRouter API...\n")

    # 1. Check if key exists
    if not my_key:
        print("❌ OPENROUTER_KEY not found in .env file")
        print("   Make sure your .env file has: OPENROUTER_KEY=your_key_here")
        return

    print(f"✅ Key found: {my_key[:8]}{'*' * (len(my_key) - 8)}")  # Show only first 8 chars

    # 2. Test the API with a minimal request
    try:
        response = requests.post(
            url="https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {my_key}",
                "Content-Type": "application/json"
            },
            data=json.dumps({
                "model": "nvidia/nemotron-3-super-120b-a12b:free",
                "messages": [
                    {"role": "user", "content": "Reply with only the word: WORKING"}
                ]
            }),
            timeout=15
        )

        # 3. Check HTTP status
        print(f"📡 HTTP Status: {response.status_code}", end=" ")
        if response.status_code == 200:
            print("✅")
        elif response.status_code == 401:
            print("❌ — Invalid API key")
            return
        elif response.status_code == 429:
            print("❌ — Rate limit hit, wait a moment")
            return
        else:
            print(f"❌ — Unexpected status")
            return

        # 4. Check response content
        result = response.json()
        reply = result['choices'][0]['message']['content']
        print(f"🤖 Model replied: '{reply}'")
        print("\n✅ API is fully working — you're good to go!")

    except requests.exceptions.Timeout:
        print("❌ Request timed out — check your internet connection")
    except requests.exceptions.RequestException as e:
        print(f"❌ Network error: {e}")
    except (KeyError, IndexError):
        print("❌ Unexpected response format")
        print(f"   Raw response: {response.text[:300]}")

test_api()
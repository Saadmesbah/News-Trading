import feedparser
from datetime import datetime

def fetch_news(your_query, x=100):
    url = f"https://news.google.com/rss/search?q={your_query}&hl=en-US&gl=US&ceid=US%3Aen"

    print(f"Fetching news for query: {your_query}")
    print(f"Using RSS feed URL: {url}")
    feed=feedparser.parse(url)
    print(f"Found {len(feed.entries)} news entries.")

    
    # Create unique filename with timestamp
    timestamp = datetime.now().strftime("%Y-%m-%d")
    filename = f'News/cache/news_{timestamp}.txt'
    
    with open(filename, 'a', encoding='utf-8') as f:
        #f.write(f"\n{'='*60}\n") 
        f.write(f"Query: {your_query}\n")
        #f.write(f"{'='*60}\n")
        
        #for index, entry in enumerate(feed.entries, 1):  # Start index at 1
        #        title = entry.title
            
        #        f.write(f"{index}. {title}\n")
        for entry in feed.entries[:x]:  # Limit to first x entries
                title = entry.title
            
                f.write(f"{title}\n")


    print(f"✓ Saved to {filename}\n")

fetch_news("crypto%20when%3A1d") # Crypto news from the last day
fetch_news("Bitcoin%20when%3A1d") # Bitcoin news from the last day
fetch_news("war%20when%3A1d",x=20)    # War news from the last day
fetch_news("politics%20when%3A1d",x=20) # Politics news from the last day

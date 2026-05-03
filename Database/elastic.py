from elasticsearch import Elasticsearch
from datetime import datetime, timezone
import os
from dotenv import load_dotenv

load_dotenv()

ES_HOST = os.getenv("ES_HOST", "http://localhost:9200")
ES_INDEX = os.getenv("ES_INDEX", "sentiment")

es = Elasticsearch(ES_HOST)

def create_index():
    """
    Create the sentiment index with proper field mappings.
    Only runs if index doesn't exist yet.
    """
    if es.indices.exists(index=ES_INDEX):
        print(f"✅ Index '{ES_INDEX}' already exists.")
        return

    mapping = {
        "mappings": {
            "properties": {
                "date":             {"type": "date"},
                "asset":            {"type": "keyword"},
                "headline_count":   {"type": "integer"},
                "headlines_sample": {"type": "text"},
                "scores": {
                    "properties": {
                        "bitcoin_score":   {"type": "float"},
                        "crypto_score":    {"type": "float"},
                        "politics_score":  {"type": "float"},
                        "war_macro_score": {"type": "float"}
                    }
                },
                "composite_score":  {"type": "float"},
                "brief_rationale":  {"type": "text"},
                "model_used":       {"type": "keyword"},
                "created_at":       {"type": "date"}
            }
        }
    }

    es.indices.create(index=ES_INDEX, body=mapping)
    print(f"✅ Index '{ES_INDEX}' created successfully.")


def save_sentiment(scores: dict, headlines: list, asset: str = "BTC"):
    """
    Save a sentiment analysis result to Elasticsearch.
    """
    composite = round(
        scores["bitcoin_score"]   * 0.40 +
        scores["crypto_score"]    * 0.20 +
        scores["politics_score"]  * 0.20 +
        scores["war_macro_score"] * 0.20,
        4
    )

    document = {
        "date":             datetime.now(timezone.utc).strftime("%Y-%m-%d"),
        "asset":            asset,
        "headline_count":   len(headlines),
        "headlines_sample": headlines[:5],  # Store first 5 headlines as sample
        "scores": {
            "bitcoin_score":   scores["bitcoin_score"],
            "crypto_score":    scores["crypto_score"],
            "politics_score":  scores["politics_score"],
            "war_macro_score": scores["war_macro_score"]
        },
        "composite_score":  composite,
        "brief_rationale":  scores["brief_rationale"],
        "model_used":       "meta-llama/llama-3.3-70b-instruct:free",
        "created_at":       datetime.now(timezone.utc).isoformat()
    }

    result = es.index(index=ES_INDEX, body=document)
    print(f"✅ Saved to Elasticsearch — ID: {result['_id']}")
    return result["_id"]


def get_all():
    """Read — get all sentiment documents sorted by date."""
    result = es.search(index=ES_INDEX, body={
        "query": {"match_all": {}},
        "sort":  [{"created_at": {"order": "desc"}}],
        "size":  100
    })
    return [hit["_source"] | {"_id": hit["_id"]} for hit in result["hits"]["hits"]]


def get_by_date(date: str):
    """Read — get sentiment for a specific date (format: YYYY-MM-DD)."""
    result = es.search(index=ES_INDEX, body={
        "query": {"term": {"date": date}}
    })
    return [hit["_source"] | {"_id": hit["_id"]} for hit in result["hits"]["hits"]]


def update_sentiment(doc_id: str, updated_fields: dict):
    """Update — modify specific fields of an existing document."""
    es.update(index=ES_INDEX, id=doc_id, body={"doc": updated_fields})
    print(f"✅ Document {doc_id} updated.")


def delete_sentiment(doc_id: str):
    """Delete — remove a document by ID."""
    es.delete(index=ES_INDEX, id=doc_id)
    print(f"✅ Document {doc_id} deleted.")


def search_by_keyword(keyword: str):
    """Search headlines containing a specific keyword."""
    result = es.search(index=ES_INDEX, body={
        "query": {
            "match": {"headlines_sample": keyword}
        }
    })
    return [hit["_source"] | {"_id": hit["_id"]} for hit in result["hits"]["hits"]]


# ── Run once to initialize ────────────────────────────────────────────────────
if __name__ == "__main__":
    create_index()
"""Scrape Hugging Face Models sorted by trending score."""

from __future__ import annotations

import logging
from .base import fetch_json

logger = logging.getLogger(__name__)

HF_API = "https://huggingface.co/api/models"


def fetch(limit: int = 10) -> list[dict]:
    """Return top trending models from HuggingFace API."""
    data = fetch_json(
        HF_API,
        params={
            "sort": "trendingScore",
            "direction": "-1",
            "limit": str(limit),
        },
    )

    results = []
    for i, model in enumerate(data[:limit], start=1):
        model_id: str = model.get("modelId") or model.get("id", "")
        parts = model_id.split("/", 1)
        org = parts[0] if len(parts) > 1 else ""
        name = model_id

        results.append({
            "rank": i,
            "name": name,
            "org": org,
            "trending_score": model.get("trendingScore", 0),
            "downloads": model.get("downloads", 0),
            "likes": model.get("likes", 0),
            "url": f"https://huggingface.co/{model_id}",
            "tags": model.get("tags", [])[:5],
            "rank_change": None,  # TODO: compare with previous snapshot
        })

    logger.info("Fetched %d trending models from HuggingFace", len(results))
    return results

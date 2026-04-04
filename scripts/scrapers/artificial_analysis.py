"""Scrape Artificial Analysis model leaderboard."""

from __future__ import annotations

import logging
import os
from .base import fetch_json

logger = logging.getLogger(__name__)

AA_API = "https://artificialanalysis.ai/api/data/llms/models"


def fetch(limit: int = 10) -> list[dict]:
    """Return top models from Artificial Analysis API."""
    api_key = os.environ.get("AA_API_KEY", "")
    headers = {}
    if api_key:
        headers["x-api-key"] = api_key

    try:
        data = fetch_json(AA_API, headers=headers)
    except RuntimeError:
        logger.warning("Artificial Analysis API failed, returning empty list")
        return []

    # The API returns a list of models; sort by quality/intelligence index
    models = data if isinstance(data, list) else data.get("data", data.get("models", []))

    # Sort by quality_index or intelligence score descending
    def sort_key(m: dict) -> float:
        return float(
            m.get("quality_index")
            or m.get("intelligence_index")
            or m.get("score")
            or 0
        )

    models.sort(key=sort_key, reverse=True)

    results = []
    for i, m in enumerate(models[:limit], start=1):
        results.append({
            "rank": i,
            "name": m.get("name", m.get("model_name", "")),
            "org": m.get("organization", m.get("provider", "")),
            "intelligence_index": sort_key(m),
            "price_input": m.get("price_input_per_1m") or m.get("input_cost_per_million"),
            "price_output": m.get("price_output_per_1m") or m.get("output_cost_per_million"),
            "speed_tps": m.get("tokens_per_second") or m.get("speed"),
            "context_window": m.get("context_window") or m.get("max_context"),
            "url": m.get("url", "https://artificialanalysis.ai/leaderboards/models"),
        })

    logger.info("Fetched %d models from Artificial Analysis", len(results))
    return results

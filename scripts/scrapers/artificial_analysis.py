"""Scrape Artificial Analysis model leaderboard."""

from __future__ import annotations

import json
import logging
import os
from .base import fetch_html, fetch_json

logger = logging.getLogger(__name__)

AA_API = "https://artificialanalysis.ai/api/data/llms/models"
AA_LEADERBOARD = "https://artificialanalysis.ai/leaderboards/models"


def fetch(limit: int = 10) -> list[dict]:
    """Return top models from Artificial Analysis API."""
    api_key = os.environ.get("AA_API_KEY", "")
    headers = {}
    if api_key:
        headers["x-api-key"] = api_key

    try:
        data = fetch_json(AA_API, headers=headers)
    except RuntimeError:
        logger.warning("Artificial Analysis API failed, trying leaderboard page fallback")
        try:
            data = _fetch_leaderboard_page()
        except RuntimeError:
            logger.warning("Artificial Analysis fallback failed, returning empty list")
            return []

    # The API returns a list of models; sort by quality/intelligence index
    models = data if isinstance(data, list) else data.get("data", data.get("models", []))

    # Sort by quality_index or intelligence score descending
    def sort_key(m: dict) -> float:
        return float(
            m.get("quality_index")
            or m.get("intelligence_index")
            or m.get("intelligenceIndex")
            or m.get("score")
            or 0
        )

    models.sort(key=sort_key, reverse=True)

    results = []
    for i, m in enumerate(models[:limit], start=1):
        results.append({
            "rank": i,
            "name": m.get("name", m.get("model_name", "")),
            "org": m.get("organization", m.get("provider") or m.get("modelCreatorName", "")),
            "intelligence_index": sort_key(m),
            "price_input": (
                m.get("price_input_per_1m")
                or m.get("input_cost_per_million")
                or m.get("price1mInputTokens")
            ),
            "price_output": (
                m.get("price_output_per_1m")
                or m.get("output_cost_per_million")
                or m.get("price1mOutputTokens")
            ),
            "speed_tps": m.get("tokens_per_second") or m.get("speed") or m.get("medianOutputTokensPerSecond"),
            "context_window": m.get("context_window") or m.get("max_context") or m.get("contextWindowTokens"),
            "url": m.get("url") or _model_url(m),
        })

    logger.info("Fetched %d models from Artificial Analysis", len(results))
    return results


def _fetch_leaderboard_page() -> list[dict]:
    """Extract leaderboard data from the public models page."""
    html = fetch_html(AA_LEADERBOARD)
    models = _extract_models_from_html(html)
    if not models:
        raise RuntimeError("Could not extract model data from Artificial Analysis page")
    return models


def _extract_models_from_html(html: str) -> list[dict]:
    """Pull the embedded model array out of the Next.js page payload."""
    for marker in ('\\"models\\":[', '"models":['):
        start = html.find(marker)
        if start == -1:
            continue
        array_start = start + len(marker) - 1
        fragment = _extract_json_array(html, array_start)
        if not fragment:
            continue
        try:
            if marker.startswith('\\"'):
                decoded = json.loads(f'"{fragment}"')
                return json.loads(decoded)
            return json.loads(fragment)
        except json.JSONDecodeError:
            continue
    return []


def _extract_json_array(text: str, start: int) -> str | None:
    """Return the JSON array starting at `start`, respecting quoted strings."""
    depth = 0
    in_string = False
    escaped = False

    for idx in range(start, len(text)):
        ch = text[idx]
        if escaped:
            escaped = False
            continue
        if ch == "\\":
            escaped = True
            continue
        if ch == '"':
            in_string = not in_string
            continue
        if in_string:
            continue
        if ch == "[":
            depth += 1
        elif ch == "]":
            depth -= 1
            if depth == 0:
                return text[start : idx + 1]
    return None


def _model_url(model: dict) -> str:
    """Return a stable model URL for either API shape."""
    slug = model.get("slug")
    if slug:
        return f"https://artificialanalysis.ai/models/{slug}"
    return "https://artificialanalysis.ai/leaderboards/models"

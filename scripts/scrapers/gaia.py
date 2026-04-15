"""Fetch GAIA benchmark leaderboard from HuggingFace Space."""

from __future__ import annotations

import logging
from .base import fetch_json

logger = logging.getLogger(__name__)

# Gradio API endpoint for the GAIA leaderboard space
GAIA_API = "https://gaia-benchmark-leaderboard.hf.space/api/predict"
GAIA_ROWS_API = "https://datasets-server.huggingface.co/rows"
GAIA_RESULTS_DATASET = "gaia-benchmark/results_public"
GAIA_RESULTS_CONFIG = "2023"
GAIA_RESULTS_SPLIT = "test"


def fetch(limit: int = 5) -> list[dict]:
    """Return top agents from GAIA leaderboard."""
    # Try Gradio API first
    try:
        return _fetch_gradio(limit)
    except Exception as exc:
        logger.warning("GAIA Gradio API failed: %s — trying fallback", exc)

    try:
        return _fetch_dataset(limit)
    except Exception as exc:
        logger.warning("GAIA dataset fallback failed: %s", exc)

    logger.warning("GAIA fetch failed, returning empty list")
    return []


def _fetch_gradio(limit: int) -> list[dict]:
    """Fetch from the Gradio-based leaderboard space."""
    import requests

    # Gradio spaces typically expose data via /api/predict or /api/info
    # Try fetching the component data directly
    resp = requests.get(
        "https://gaia-benchmark-leaderboard.hf.space/",
        headers={"User-Agent": "ai-dashboard-scraper/1.0"},
        timeout=30,
    )
    resp.raise_for_status()

    # Try to extract leaderboard data from the HTML/JSON
    # Gradio embeds data in a script tag or exposes via API
    from bs4 import BeautifulSoup
    import json
    import re

    soup = BeautifulSoup(resp.text, "lxml")

    # Look for embedded JSON data in script tags
    for script in soup.find_all("script"):
        text = script.get_text()
        # Gradio often embeds component data in window.__gradio_config__
        match = re.search(r'window\.__gradio_config__\s*=\s*({.+?});?\s*</script>', text, re.DOTALL)
        if not match:
            match = re.search(r'"components":\s*\[(.+?)\]\s*[,}]', text, re.DOTALL)
        if match:
            try:
                config = json.loads(match.group(1) if not match.group(0).startswith('{') else match.group(0).rstrip(';'))
                return _parse_gradio_config(config, limit)
            except (json.JSONDecodeError, KeyError):
                continue

    raise RuntimeError("Could not extract GAIA leaderboard data")


def _parse_gradio_config(config: dict, limit: int) -> list[dict]:
    """Parse Gradio config to extract leaderboard rows."""
    results = []
    # Navigate Gradio config structure to find dataframe components
    components = config.get("components", [])
    for comp in components:
        if comp.get("type") == "dataframe":
            props = comp.get("props", {})
            value = props.get("value", {})
            data = value.get("data", [])
            headers = value.get("headers", [])

            for i, row in enumerate(data[:limit], start=1):
                row_dict = dict(zip(headers, row)) if headers else {}
                results.append({
                    "rank": i,
                    "name": row_dict.get("Model", row_dict.get("name", str(row[0]) if row else "")),
                    "org": row_dict.get("Organization", row_dict.get("org", "")),
                    "score": float(row_dict.get("Average", row_dict.get("score", 0))),
                    "score_unit": "%",
                    "url": "https://huggingface.co/spaces/gaia-benchmark/leaderboard",
                    "verified": True,
                })
            break

    return results


def _fetch_dataset(limit: int) -> list[dict]:
    """Fetch leaderboard rows from the public Hugging Face dataset."""
    data = fetch_json(
        GAIA_ROWS_API,
        params={
            "dataset": GAIA_RESULTS_DATASET,
            "config": GAIA_RESULTS_CONFIG,
            "split": GAIA_RESULTS_SPLIT,
            "offset": "0",
            "length": "100",
        },
    )
    rows = data.get("rows", [])
    if not rows:
        raise RuntimeError("No rows returned from GAIA dataset")

    agents = []
    for entry in rows:
        row = entry.get("row", entry)
        model = row.get("model")
        if not model:
            continue

        raw_score = row.get("score", 0)
        try:
            score = float(raw_score)
        except (TypeError, ValueError):
            continue
        if score <= 1:
            score *= 100

        agents.append({
            "name": model,
            "org": row.get("organisation", ""),
            "score": round(score, 2),
            "url": row.get("url") or "https://huggingface.co/spaces/gaia-benchmark/leaderboard",
        })

    agents.sort(key=lambda item: item["score"], reverse=True)

    return [
        {
            "rank": idx,
            "name": agent["name"],
            "org": agent["org"],
            "score": agent["score"],
            "score_unit": "%",
            "url": agent["url"],
            "verified": True,
        }
        for idx, agent in enumerate(agents[:limit], start=1)
    ]

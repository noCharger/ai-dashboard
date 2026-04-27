"""Fetch BFCL (Berkeley Function Calling Leaderboard) data."""

from __future__ import annotations

import csv
import logging
from io import StringIO

from .base import fetch_html

logger = logging.getLogger(__name__)

BFCL_URL = "https://gorilla.cs.berkeley.edu/leaderboard.html"
BFCL_CSV_URL = "https://gorilla.cs.berkeley.edu/data_overall.csv"


def fetch(limit: int = 5) -> list[dict]:
    """Return top models from BFCL leaderboard."""
    try:
        return _fetch_csv(limit)
    except Exception as exc:
        logger.warning("BFCL scrape failed: %s", exc)
        return []


def _fetch_csv(limit: int) -> list[dict]:
    """Parse BFCL's published CSV rather than scraping the rendered table."""
    csv_text = fetch_html(BFCL_CSV_URL)
    rows = list(csv.DictReader(StringIO(csv_text)))
    if not rows:
        raise RuntimeError("BFCL CSV returned no rows")

    results = []
    for rank, row in enumerate(rows[:limit], start=1):
        score = _parse_percent(row.get("Overall Acc", "0"))
        results.append({
            "rank": rank,
            "name": row.get("Model", ""),
            "org": row.get("Organization", "") or _extract_org(row.get("Model", "")),
            "score": score,
            "score_unit": "% accuracy",
            "url": row.get("Model Link") or BFCL_URL,
            "verified": True,
        })

    logger.info("Fetched %d entries from BFCL", len(results))
    return results


def _parse_percent(value: str) -> float:
    """Convert a BFCL percentage string like '77.47%' into a float."""
    raw = str(value).strip().replace("%", "")
    try:
        return round(float(raw), 2)
    except ValueError:
        return 0.0


def _extract_org(name: str) -> str:
    """Best-effort org extraction."""
    known = {
        "Claude": "Anthropic", "GPT": "OpenAI", "o1": "OpenAI", "o3": "OpenAI",
        "Gemini": "Google", "Grok": "xAI", "DeepSeek": "DeepSeek",
        "Llama": "Meta", "Mistral": "Mistral AI", "Command": "Cohere",
        "Nova": "Amazon",
    }
    for keyword, org in known.items():
        if keyword.lower() in name.lower():
            return org
    return ""

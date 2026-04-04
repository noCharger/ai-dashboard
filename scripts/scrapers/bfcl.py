"""Fetch BFCL (Berkeley Function Calling Leaderboard) data."""

from __future__ import annotations

import logging
from .base import fetch_html

logger = logging.getLogger(__name__)

BFCL_URL = "https://gorilla.cs.berkeley.edu/leaderboard.html"


def fetch(limit: int = 5) -> list[dict]:
    """Return top models from BFCL leaderboard."""
    try:
        return _scrape_leaderboard(limit)
    except Exception as exc:
        logger.warning("BFCL scrape failed: %s", exc)
        return []


def _scrape_leaderboard(limit: int) -> list[dict]:
    """Scrape the BFCL leaderboard page."""
    from bs4 import BeautifulSoup
    import json
    import re

    html = fetch_html(BFCL_URL)
    soup = BeautifulSoup(html, "lxml")

    results = []

    # BFCL embeds leaderboard data in JavaScript
    for script in soup.find_all("script"):
        text = script.get_text()
        if "overall" in text.lower() and ("accuracy" in text.lower() or "score" in text.lower()):
            # Try to find JSON data arrays
            matches = re.findall(r'\[{[^]]+}\]', text)
            for match_str in matches:
                try:
                    entries = json.loads(match_str)
                    if entries and isinstance(entries[0], dict):
                        # Look for accuracy-like fields
                        score_key = None
                        for key in ["overall_accuracy", "accuracy", "Overall Acc", "score"]:
                            if key in entries[0]:
                                score_key = key
                                break
                        if score_key:
                            entries.sort(key=lambda x: float(x.get(score_key, 0)), reverse=True)
                            for i, entry in enumerate(entries[:limit], start=1):
                                name = entry.get("model", entry.get("Model", entry.get("name", "")))
                                results.append({
                                    "rank": i,
                                    "name": name,
                                    "org": _extract_org(name),
                                    "score": round(float(entry.get(score_key, 0)) * 100, 1)
                                           if float(entry.get(score_key, 0)) <= 1
                                           else round(float(entry.get(score_key, 0)), 1),
                                    "score_unit": "% accuracy",
                                    "url": BFCL_URL,
                                    "verified": True,
                                })
                            break
                except (json.JSONDecodeError, KeyError, TypeError):
                    continue
        if results:
            break

    # Fallback: try parsing HTML tables
    if not results:
        tables = soup.find_all("table")
        for table in tables:
            rows = table.find_all("tr")
            for i, row in enumerate(rows[1:limit + 1], start=1):
                cells = row.find_all("td")
                if len(cells) >= 2:
                    name = cells[0].get_text(strip=True)
                    score_text = cells[-1].get_text(strip=True).replace("%", "")
                    try:
                        score = float(score_text)
                    except ValueError:
                        score = 0.0
                    results.append({
                        "rank": i,
                        "name": name,
                        "org": _extract_org(name),
                        "score": score,
                        "score_unit": "% accuracy",
                        "url": BFCL_URL,
                        "verified": True,
                    })

    logger.info("Fetched %d entries from BFCL", len(results))
    return results


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

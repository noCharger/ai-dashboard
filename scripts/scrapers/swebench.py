"""Fetch SWE-bench Verified leaderboard data."""

from __future__ import annotations

import logging
from .base import fetch_json, fetch_html

logger = logging.getLogger(__name__)

# SWE-bench publishes leaderboard data on their website
# The data is embedded in the page or available via their GitHub repo
SWEBENCH_VERIFIED_URL = "https://www.swebench.com/verified.html"
SWEBENCH_DATA_URL = "https://raw.githubusercontent.com/swe-bench/experiments/main/evaluation/verified/results/results.json"


def fetch(limit: int = 5) -> list[dict]:
    """Return top coding agents from SWE-bench Verified."""
    # Try fetching from GitHub raw data first
    try:
        return _fetch_from_website(limit)
    except Exception as exc:
        logger.warning("SWE-bench fetch failed: %s", exc)
        return []


def _fetch_from_website(limit: int) -> list[dict]:
    """Scrape SWE-bench verified leaderboard page."""
    from bs4 import BeautifulSoup
    import json
    import re

    html = fetch_html(SWEBENCH_VERIFIED_URL)
    soup = BeautifulSoup(html, "lxml")

    # SWE-bench embeds leaderboard data as JSON in a script tag
    results = []
    for script in soup.find_all("script"):
        text = script.get_text()
        # Look for leaderboard data patterns
        if "resolved" in text and ("leaderboard" in text.lower() or "results" in text.lower()):
            # Try to extract JSON arrays
            matches = re.findall(r'\[{[^]]+}\]', text)
            for match_str in matches:
                try:
                    entries = json.loads(match_str)
                    if entries and isinstance(entries[0], dict) and "resolved" in entries[0]:
                        # Sort by resolved percentage descending
                        entries.sort(key=lambda x: float(x.get("resolved", 0)), reverse=True)
                        for i, entry in enumerate(entries[:limit], start=1):
                            results.append({
                                "rank": i,
                                "name": entry.get("name", ""),
                                "org": _extract_org(entry.get("name", "")),
                                "score": float(entry.get("resolved", 0)),
                                "score_unit": "% resolved",
                                "url": entry.get("site", "https://www.swebench.com/verified.html"),
                                "verified": bool(entry.get("verified", True)),
                            })
                        break
                except (json.JSONDecodeError, KeyError, TypeError):
                    continue
        if results:
            break

    # Fallback: parse HTML table
    if not results:
        tables = soup.find_all("table")
        for table in tables:
            rows = table.find_all("tr")
            for i, row in enumerate(rows[1:limit + 1], start=1):
                cells = row.find_all("td")
                if len(cells) >= 2:
                    name = cells[0].get_text(strip=True)
                    score_text = cells[1].get_text(strip=True).replace("%", "")
                    try:
                        score = float(score_text)
                    except ValueError:
                        score = 0.0
                    results.append({
                        "rank": i,
                        "name": name,
                        "org": _extract_org(name),
                        "score": score,
                        "score_unit": "% resolved",
                        "url": "https://www.swebench.com/verified.html",
                        "verified": True,
                    })

    logger.info("Fetched %d entries from SWE-bench Verified", len(results))
    return results


def _extract_org(name: str) -> str:
    """Best-effort org extraction from agent name."""
    known = {
        "Claude": "Anthropic", "Anthropic": "Anthropic",
        "GPT": "OpenAI", "OpenAI": "OpenAI", "o1": "OpenAI", "o3": "OpenAI",
        "Gemini": "Google", "Google": "Google",
        "Grok": "xAI",
        "DeepSeek": "DeepSeek",
        "Llama": "Meta",
        "Devstral": "Mistral AI", "Mistral": "Mistral AI",
        "Amazon": "Amazon", "Nova": "Amazon",
        "Codex": "OpenAI",
    }
    for keyword, org in known.items():
        if keyword.lower() in name.lower():
            return org
    return ""

"""Fetch SWE-bench Verified leaderboard data."""

from __future__ import annotations

import logging
import json
import re

from .base import fetch_html

logger = logging.getLogger(__name__)

SWEBENCH_URL = "https://www.swebench.com/"
SWEBENCH_VERIFIED_PAGE = "https://www.swebench.com/verified.html"
LEADERBOARD_DATA_PATTERN = re.compile(
    r'<script type="application/json" id="leaderboard-data">\s*(\[.*?\])\s*</script>',
    re.DOTALL,
)


def fetch(limit: int = 5) -> list[dict]:
    """Return top coding agents from SWE-bench Verified."""
    try:
        return _fetch_from_embedded_json(limit)
    except Exception as exc:
        logger.warning("SWE-bench fetch failed: %s", exc)
        return []


def _fetch_from_embedded_json(limit: int) -> list[dict]:
    """Parse the leaderboard JSON embedded on the SWE-bench homepage."""
    html = fetch_html(SWEBENCH_URL)
    match = LEADERBOARD_DATA_PATTERN.search(html)
    if not match:
        raise RuntimeError("Could not locate leaderboard-data JSON on SWE-bench homepage")

    leaderboards = json.loads(match.group(1))
    verified = next(
        (leaderboard for leaderboard in leaderboards if leaderboard.get("name") == "Verified"),
        None,
    )
    if not isinstance(verified, dict):
        raise RuntimeError("Verified leaderboard not found in SWE-bench payload")

    entries = sorted(
        verified.get("results", []),
        key=lambda item: float(item.get("resolved", 0) or 0),
        reverse=True,
    )

    results = []
    for rank, entry in enumerate(entries[:limit], start=1):
        site = entry.get("site")
        if isinstance(site, list):
            site = next((url for url in site if url), "")

        results.append({
            "rank": rank,
            "name": entry.get("name", ""),
            "org": _extract_org(entry),
            "score": round(float(entry.get("resolved", 0) or 0), 2),
            "score_unit": "% resolved",
            "url": site or SWEBENCH_VERIFIED_PAGE,
            "verified": bool(entry.get("checked", False)),
        })

    logger.info("Fetched %d entries from SWE-bench Verified", len(results))
    return results


def _extract_org(entry: dict) -> str:
    """Prefer explicit Org tags, then fall back to name heuristics."""
    for tag in entry.get("tags", []):
        if isinstance(tag, str) and tag.startswith("Org: "):
            return tag[5:]

    name = str(entry.get("name", ""))
    known = {
        "Claude": "Anthropic",
        "Anthropic": "Anthropic",
        "GPT": "OpenAI",
        "OpenAI": "OpenAI",
        "o1": "OpenAI",
        "o3": "OpenAI",
        "Gemini": "Google",
        "Google": "Google",
        "Grok": "xAI",
        "DeepSeek": "DeepSeek",
        "Llama": "Meta",
        "Devstral": "Mistral AI",
        "Mistral": "Mistral AI",
        "Amazon": "Amazon",
        "Nova": "Amazon",
        "Codex": "OpenAI",
    }
    for keyword, org in known.items():
        if keyword.lower() in name.lower():
            return org
    return ""

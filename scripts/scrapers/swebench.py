"""Fetch SWE-bench Verified leaderboard data (mini-SWE-agent v2 standardized)."""

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
MINI_AGENT_TAG = "Mini: 2.0.0"
NAME_PREFIX = re.compile(r"^mini-SWE-agent\s*\+\s*", re.IGNORECASE)


def fetch(limit: int = 5) -> list[dict]:
    """Return top coding agents from SWE-bench Verified (mini-SWE-agent v2 only)."""
    try:
        return _fetch_from_embedded_json(limit)
    except Exception as exc:
        logger.warning("SWE-bench fetch failed: %s", exc)
        return []


def _fetch_from_embedded_json(limit: int) -> list[dict]:
    html = fetch_html(SWEBENCH_URL)
    match = LEADERBOARD_DATA_PATTERN.search(html)
    if not match:
        raise RuntimeError("Could not locate leaderboard-data JSON on SWE-bench homepage")

    leaderboards = json.loads(match.group(1))
    verified = next(
        (lb for lb in leaderboards if lb.get("name") == "Verified"),
        None,
    )
    if not isinstance(verified, dict):
        raise RuntimeError("Verified leaderboard not found in SWE-bench payload")

    # Keep only standardized mini-SWE-agent v2 entries that have cost data
    entries = [
        e for e in verified.get("results", [])
        if MINI_AGENT_TAG in (e.get("tags") or [])
        and e.get("resolved") is not None
        and e.get("instance_cost") is not None
    ]
    entries.sort(key=lambda e: float(e.get("resolved", 0)), reverse=True)

    results = []
    for rank, entry in enumerate(entries[:limit], start=1):
        site = entry.get("site")
        if isinstance(site, list):
            site = next((u for u in site if u), "")

        name = NAME_PREFIX.sub("", entry.get("name", "")).strip()
        org = _extract_org(entry)
        resolved = round(float(entry["resolved"]), 1)
        cost = round(float(entry["instance_cost"]), 4)
        cost_per_bug = round(cost / (resolved / 100), 2) if resolved else None

        results.append({
            "rank": rank,
            "name": name,
            "org": org,
            "score": resolved,
            "score_unit": "% resolved",
            "avg_cost_usd": cost,
            "cost_per_bug": cost_per_bug,
            "url": site or SWEBENCH_VERIFIED_PAGE,
            "verified": bool(entry.get("checked", False)),
            "date": entry.get("date", ""),
        })

    logger.info("Fetched %d entries from SWE-bench Verified (mini-SWE-agent v2)", len(results))
    return results


def _extract_org(entry: dict) -> str:
    for tag in entry.get("tags", []):
        if isinstance(tag, str) and tag.startswith("Org: ") and tag != "Org: SWE-agent":
            return tag[5:]
    name = str(entry.get("name", ""))
    known = {
        "Claude": "Anthropic", "Anthropic": "Anthropic",
        "GPT": "OpenAI", "OpenAI": "OpenAI", "o1": "OpenAI", "o3": "OpenAI", "Codex": "OpenAI",
        "Gemini": "Google", "Google": "Google",
        "Grok": "xAI",
        "DeepSeek": "DeepSeek",
        "Llama": "Meta",
        "Devstral": "Mistral AI", "Mistral": "Mistral AI",
        "Amazon": "Amazon", "Nova": "Amazon",
        "Kimi": "Moonshot AI",
        "GLM": "Zhipu AI",
        "MiniMax": "Minimax",
    }
    for keyword, org in known.items():
        if keyword.lower() in name.lower():
            return org
    return ""

#!/usr/bin/env python3
"""Orchestrator: run all scrapers and produce data/dashboard.json."""

from __future__ import annotations

import json
import logging
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

# Add parent dir to path so scrapers package is importable
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from scripts.scrapers import (
    hf_models,
    artificial_analysis,
    arxiv_papers,
    github_trending,
    hacker_news,
    hf_papers,
    gaia,
    swebench,
    bfcl,
    frameworks,
)
from scripts.scrapers.base import DATA_DIR

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)

TOP_N = 5
FRAMEWORKS_SEED = [
    {
        "rank": 1,
        "name": "langchain-ai/langchain",
        "url": "https://github.com/langchain-ai/langchain",
        "stars_28d": 692,
        "total_stars": 123177,
        "description": "Build LLM applications with composable chains, retrieval, tools, and agent patterns.",
        "category": "General Agent Stack",
        "language": "Python",
        "language_color": "#3572A5",
    },
    {
        "rank": 2,
        "name": "crewAIInc/crewAI",
        "url": "https://github.com/crewAIInc/crewAI",
        "stars_28d": 433,
        "total_stars": 36911,
        "description": "Role-based multi-agent orchestration focused on collaborative execution workflows.",
        "category": "Multi-Agent Orchestration",
        "language": "Python",
        "language_color": "#3572A5",
    },
    {
        "rank": 3,
        "name": "FoundationAgents/MetaGPT",
        "url": "https://github.com/FoundationAgents/MetaGPT",
        "stars_28d": 329,
        "total_stars": 57874,
        "description": "Software-company style multi-agent framework for autonomous task decomposition.",
        "category": "Agent Team Simulation",
        "language": "Python",
        "language_color": "#3572A5",
    },
    {
        "rank": 4,
        "name": "microsoft/autogen",
        "url": "https://github.com/microsoft/autogen",
        "stars_28d": 264,
        "total_stars": 50001,
        "description": "Programming framework for multi-agent conversational systems and tool-enabled workflows.",
        "category": "Conversational Agents",
        "language": "Python",
        "language_color": "#3572A5",
    },
    {
        "rank": 5,
        "name": "Significant-Gravitas/AutoGPT",
        "url": "https://github.com/Significant-Gravitas/AutoGPT",
        "stars_28d": 203,
        "total_stars": 174783,
        "description": "Classic autonomous-agent project with a broad plugin ecosystem and community variants.",
        "category": "Autonomous Agent Platform",
        "language": "Python",
        "language_color": "#3572A5",
    },
]
AGENT_SEED = {
    "general": [
        {
            "rank": 1,
            "name": "Claude 4.6 Opus + Tools",
            "org": "Anthropic",
            "score": 75.2,
            "score_unit": "%",
            "url": "https://huggingface.co/spaces/gaia-benchmark/leaderboard",
            "verified": True,
        },
        {
            "rank": 2,
            "name": "GPT-4.1 + Plugins",
            "org": "OpenAI",
            "score": 72.8,
            "score_unit": "%",
            "url": "https://huggingface.co/spaces/gaia-benchmark/leaderboard",
            "verified": True,
        },
        {
            "rank": 3,
            "name": "Gemini 3 Pro + Tools",
            "org": "Google",
            "score": 68.4,
            "score_unit": "%",
            "url": "https://huggingface.co/spaces/gaia-benchmark/leaderboard",
            "verified": True,
        },
        {
            "rank": 4,
            "name": "Grok 4 + Search",
            "org": "xAI",
            "score": 64.1,
            "score_unit": "%",
            "url": "https://huggingface.co/spaces/gaia-benchmark/leaderboard",
            "verified": False,
        },
        {
            "rank": 5,
            "name": "Llama 4 Scout Agent",
            "org": "Meta",
            "score": 58.9,
            "score_unit": "%",
            "url": "https://huggingface.co/spaces/gaia-benchmark/leaderboard",
            "verified": False,
        },
    ],
    "coding": [
        {
            "rank": 1,
            "name": "Claude 4.5 Opus (high reasoning)",
            "org": "Anthropic",
            "score": 76.8,
            "score_unit": "% resolved",
            "url": "https://www.swebench.com/verified.html",
            "verified": True,
        },
        {
            "rank": 2,
            "name": "Gemini 3 Flash (high reasoning)",
            "org": "Google",
            "score": 75.8,
            "score_unit": "% resolved",
            "url": "https://www.swebench.com/verified.html",
            "verified": True,
        },
        {
            "rank": 3,
            "name": "OpenAI o3",
            "org": "OpenAI",
            "score": 69.1,
            "score_unit": "% resolved",
            "url": "https://www.swebench.com/verified.html",
            "verified": True,
        },
        {
            "rank": 4,
            "name": "Devstral Small",
            "org": "Mistral AI",
            "score": 64.8,
            "score_unit": "% resolved",
            "url": "https://www.swebench.com/verified.html",
            "verified": True,
        },
        {
            "rank": 5,
            "name": "Amazon Nova Agent",
            "org": "Amazon",
            "score": 61.5,
            "score_unit": "% resolved",
            "url": "https://www.swebench.com/verified.html",
            "verified": False,
        },
    ],
    "tool_use": [
        {
            "rank": 1,
            "name": "Claude 4.6 Opus",
            "org": "Anthropic",
            "score": 92.4,
            "score_unit": "% accuracy",
            "url": "https://gorilla.cs.berkeley.edu/leaderboard.html",
            "verified": True,
        },
        {
            "rank": 2,
            "name": "GPT-4.1",
            "org": "OpenAI",
            "score": 90.7,
            "score_unit": "% accuracy",
            "url": "https://gorilla.cs.berkeley.edu/leaderboard.html",
            "verified": True,
        },
        {
            "rank": 3,
            "name": "Gemini 3.1 Pro",
            "org": "Google",
            "score": 88.9,
            "score_unit": "% accuracy",
            "url": "https://gorilla.cs.berkeley.edu/leaderboard.html",
            "verified": True,
        },
        {
            "rank": 4,
            "name": "Grok 4.20",
            "org": "xAI",
            "score": 85.3,
            "score_unit": "% accuracy",
            "url": "https://gorilla.cs.berkeley.edu/leaderboard.html",
            "verified": False,
        },
        {
            "rank": 5,
            "name": "Llama 4 Maverick",
            "org": "Meta",
            "score": 81.6,
            "score_unit": "% accuracy",
            "url": "https://gorilla.cs.berkeley.edu/leaderboard.html",
            "verified": False,
        },
    ],
}
HN_SEED = {
    "top": [
        {
            "rank": 1,
            "id": 47861270,
            "title": "Windows 9x Subsystem for Linux",
            "discussion_url": "https://news.ycombinator.com/item?id=47861270",
            "site": "hails.org",
            "points": 326,
            "comments": 74,
            "author": "sohkamyung",
        },
        {
            "rank": 2,
            "id": 47862331,
            "title": "Discontinuation of open-source initiatives by GitHub next year",
            "discussion_url": "https://news.ycombinator.com/item?id=47862331",
            "site": "github.com",
            "points": 270,
            "comments": 170,
            "author": "todsacerdoti",
        },
        {
            "rank": 3,
            "id": 47862386,
            "title": "Large-scale solar in the medieval style",
            "discussion_url": "https://news.ycombinator.com/item?id=47862386",
            "site": "lowtechmagazine.com",
            "points": 166,
            "comments": 53,
            "author": "tenebris",
        },
    ],
    "ask": [
        {
            "rank": 1,
            "id": 47834213,
            "title": "Ask HN: Is there a marketplace for cold start businesses?",
            "discussion_url": "https://news.ycombinator.com/item?id=47834213",
            "site": "news.ycombinator.com",
            "points": 52,
            "comments": 69,
            "author": "abffall",
        },
        {
            "rank": 2,
            "id": 47822940,
            "title": "Ask HN: OpenClaw at 300k?",
            "discussion_url": "https://news.ycombinator.com/item?id=47822940",
            "site": "news.ycombinator.com",
            "points": 35,
            "comments": 41,
            "author": "jonsef",
        },
        {
            "rank": 3,
            "id": 47857461,
            "title": "Ask HN: Should I ask for a raise after 3 months?",
            "discussion_url": "https://news.ycombinator.com/item?id=47857461",
            "site": "news.ycombinator.com",
            "points": 22,
            "comments": 35,
            "author": "throwaway711",
        },
    ],
    "show": [
        {
            "rank": 1,
            "id": 47847558,
            "title": "Show HN: Klowde, the smartest way to find work",
            "discussion_url": "https://news.ycombinator.com/item?id=47847558",
            "site": "news.ycombinator.com",
            "points": 45,
            "comments": 19,
            "author": "wearewmn",
        },
        {
            "rank": 2,
            "id": 47849097,
            "title": "Show HN: ReadRSS, a simple RSS tracker with no ads and no bullshit",
            "discussion_url": "https://news.ycombinator.com/item?id=47849097",
            "site": "news.ycombinator.com",
            "points": 19,
            "comments": 17,
            "author": "taylor_cas",
        },
        {
            "rank": 3,
            "id": 47836740,
            "title": "Show HN: A framework for a roleplaying game on top of a social network",
            "discussion_url": "https://news.ycombinator.com/item?id=47836740",
            "site": "news.ycombinator.com",
            "points": 13,
            "comments": 3,
            "author": "charleson",
        },
    ],
}


def _safe_fetch(name: str, fn, *args, **kwargs):
    """Run a scraper, return [] on failure."""
    try:
        result = fn(*args, **kwargs)
        logger.info("✓ %s: %d items", name, len(result))
        return result
    except Exception as exc:
        logger.error("✗ %s failed: %s", name, exc)
        return []


def _load_previous() -> dict | None:
    """Load previous dashboard.json for fallback."""
    path = DATA_DIR / "dashboard.json"
    if path.exists():
        try:
            with open(path, encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, OSError):
            pass
    return None


def _fallback(section_path: list[str], prev: dict | None, new_data: list) -> list:
    """Use new data if available, otherwise fall back to previous snapshot."""
    if new_data:
        return new_data
    if prev is None:
        return []
    obj = prev
    for key in section_path:
        obj = obj.get(key, {})
    return obj if isinstance(obj, list) else []


def _strip_generated(data: dict | None) -> dict | None:
    """Return a shallow copy without generated timestamp."""
    if not isinstance(data, dict):
        return None
    cleaned = dict(data)
    cleaned.pop("generated", None)
    return cleaned

def _item_identity(item: object) -> str:
    """Choose a stable identity for leaderboard item ordering."""
    if not isinstance(item, dict):
        return json.dumps(item, ensure_ascii=False, sort_keys=True)
    for key in ("url", "id", "name", "title"):
        value = item.get(key)
        if value:
            return str(value)
    return json.dumps(item, ensure_ascii=False, sort_keys=True)


def _collect_sequences(obj: object, path: tuple[str, ...] = ()) -> dict[str, list[str]]:
    """Collect ordered identity sequence for each list path."""
    if isinstance(obj, dict):
        sequences: dict[str, list[str]] = {}
        for key, value in obj.items():
            sequences.update(_collect_sequences(value, (*path, key)))
        return sequences
    if isinstance(obj, list):
        return {".".join(path): [_item_identity(item) for item in obj]}
    return {}


def _same_relative_positions(previous_payload: dict | None, new_payload: dict) -> bool:
    """Return True when all leaderboard list orders are unchanged."""
    if not isinstance(previous_payload, dict):
        return False
    return _collect_sequences(previous_payload) == _collect_sequences(new_payload)


def _same_section(previous_payload: dict | None, new_payload: dict, key: str) -> bool:
    """Return True when a top-level section matches exactly."""
    if not isinstance(previous_payload, dict):
        return False
    return previous_payload.get(key) == new_payload.get(key)


def _same_sections(previous_payload: dict | None, new_payload: dict, keys: list[str]) -> bool:
    """Return True when every named top-level section matches exactly."""
    if not isinstance(previous_payload, dict):
        return False
    return all(previous_payload.get(key) == new_payload.get(key) for key in keys)


def main() -> int:
    previous = _load_previous()

    # ---- Models ----
    trending_models = _safe_fetch("HF Models Trending", hf_models.fetch, TOP_N)
    benchmark_models = _safe_fetch("Artificial Analysis", artificial_analysis.fetch, TOP_N)

    # ---- Agents ----
    general_agents = _safe_fetch("GAIA", gaia.fetch, TOP_N)
    coding_agents = _safe_fetch("SWE-bench", swebench.fetch, TOP_N)
    tool_use_agents = _safe_fetch("BFCL", bfcl.fetch, TOP_N)

    # ---- GitHub Repos ----
    repos_daily = _safe_fetch("GitHub Trending (daily)", github_trending.fetch_daily, TOP_N)
    repos_weekly = _safe_fetch("GitHub Trending (weekly)", github_trending.fetch_weekly, TOP_N)
    repos_monthly = _safe_fetch("GitHub Trending (monthly)", github_trending.fetch_monthly, TOP_N)
    framework_rankings = _safe_fetch("OSSInsight Frameworks", frameworks.fetch, TOP_N)
    framework_rankings = _fallback(["repos", "frameworks"], previous, framework_rankings)
    if not framework_rankings:
        framework_rankings = FRAMEWORKS_SEED

    # ---- Papers ----
    hf_trending_papers = _safe_fetch("HF Papers", hf_papers.fetch, TOP_N)
    arxiv_recent_papers = _safe_fetch("arXiv", arxiv_papers.fetch, TOP_N)

    # ---- Hacker News ----
    hn_top = _safe_fetch("Hacker News (top)", hacker_news.fetch_top, TOP_N)
    hn_ask = _safe_fetch("Hacker News (ask)", hacker_news.fetch_ask, TOP_N)
    hn_show = _safe_fetch("Hacker News (show)", hacker_news.fetch_show, TOP_N)

    # ---- Assemble with fallback ----
    dashboard_payload = {
        "models": {
            "trending": _fallback(["models", "trending"], previous, trending_models),
            "benchmark": _fallback(["models", "benchmark"], previous, benchmark_models),
        },
        "agents": {
            "general": _fallback(["agents", "general"], previous, general_agents)
            or AGENT_SEED["general"],
            "coding": _fallback(["agents", "coding"], previous, coding_agents)
            or AGENT_SEED["coding"],
            "tool_use": _fallback(["agents", "tool_use"], previous, tool_use_agents)
            or AGENT_SEED["tool_use"],
        },
        "repos": {
            "daily": _fallback(["repos", "daily"], previous, repos_daily),
            "weekly": _fallback(["repos", "weekly"], previous, repos_weekly),
            "monthly": _fallback(["repos", "monthly"], previous, repos_monthly),
            "frameworks": framework_rankings,
        },
        "papers": {
            "hf_trending": _fallback(["papers", "hf_trending"], previous, hf_trending_papers),
            "arxiv_recent": _fallback(["papers", "arxiv_recent"], previous, arxiv_recent_papers),
        },
        "hn": {
            "top": _fallback(["hn", "top"], previous, hn_top) or HN_SEED["top"],
            "ask": _fallback(["hn", "ask"], previous, hn_ask) or HN_SEED["ask"],
            "show": _fallback(["hn", "show"], previous, hn_show) or HN_SEED["show"],
        },
    }

    previous_payload = _strip_generated(previous)
    update_strategy = os.getenv("UPDATE_STRATEGY", "relative").strip().lower()

    if update_strategy == "strict":
        # Daily mode: update whenever any payload content changes.
        if previous_payload == dashboard_payload:
            logger.info("No content changes detected; dashboard.json not updated")
            return 0
    else:
        # Hourly mode: track exact leaderboard payload changes, plus paper refreshes.
        if (
            _same_sections(previous_payload, dashboard_payload, ["models", "agents", "repos"])
            and _same_section(previous_payload, dashboard_payload, "papers")
        ):
            logger.info("No leaderboard content changes detected; dashboard.json not updated")
            return 0

    dashboard = {
        "generated": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        **dashboard_payload,
    }

    # Write output
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    out_path = DATA_DIR / "dashboard.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(dashboard, f, ensure_ascii=False, indent=2)
        f.write("\n")

    logger.info("Dashboard data written to %s", out_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

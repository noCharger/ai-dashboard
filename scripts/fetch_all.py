#!/usr/bin/env python3
"""Orchestrator: run all scrapers and produce data/dashboard.json."""

from __future__ import annotations

import json
import logging
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
    hf_papers,
    gaia,
    swebench,
    bfcl,
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
    framework_rankings = _fallback(["repos", "frameworks"], previous, [])
    if not framework_rankings:
        framework_rankings = FRAMEWORKS_SEED

    # ---- Papers ----
    hf_trending_papers = _safe_fetch("HF Papers", hf_papers.fetch, TOP_N)
    arxiv_recent_papers = _safe_fetch("arXiv", arxiv_papers.fetch, TOP_N)

    # ---- Assemble with fallback ----
    dashboard = {
        "generated": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "models": {
            "trending": _fallback(["models", "trending"], previous, trending_models),
            "benchmark": _fallback(["models", "benchmark"], previous, benchmark_models),
        },
        "agents": {
            "general": _fallback(["agents", "general"], previous, general_agents),
            "coding": _fallback(["agents", "coding"], previous, coding_agents),
            "tool_use": _fallback(["agents", "tool_use"], previous, tool_use_agents),
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

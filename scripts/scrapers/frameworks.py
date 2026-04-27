"""Fetch OSSInsight AI agent framework rankings."""

from __future__ import annotations

import logging
import os

from .base import fetch_json

logger = logging.getLogger(__name__)

OSSINSIGHT_COLLECTION_ID = 10098
OSSINSIGHT_RANKING_API = (
    f"https://api.ossinsight.io/v1/collections/{OSSINSIGHT_COLLECTION_ID}/ranking_by_stars/"
)
GITHUB_REPO_API = "https://api.github.com/repos/{repo_name}"

LANGUAGE_COLORS = {
    "Python": "#3572A5",
    "TypeScript": "#3178C6",
    "JavaScript": "#F1E05A",
    "Go": "#00ADD8",
    "Rust": "#DEA584",
    "Shell": "#89E051",
}

CATEGORY_HINTS = {
    "langchain-ai/langchain": "General Agent Stack",
    "crewAIInc/crewAI": "Multi-Agent Orchestration",
    "FoundationAgents/MetaGPT": "Agent Team Simulation",
    "microsoft/autogen": "Conversational Agents",
    "Significant-Gravitas/AutoGPT": "Autonomous Agent Platform",
    "openai/openai-agents-python": "Agent SDK",
    "pydantic/pydantic-ai": "Typed Agent SDK",
    "agno-agi/agno": "Agent Application Framework",
    "VoltAgent/voltagent": "TypeScript Agent Framework",
    "microsoft/JARVIS": "Tool-Using Agents",
    "yoheinakajima/babyagi": "Autonomous Agents",
    "camel-ai/camel": "Multi-Agent Research",
    "ag2ai/ag2": "Multi-Agent Orchestration",
    "aiwaves-cn/agents": "Agent Team Simulation",
    "omega-memory/omega-memory": "Agent Memory",
    "mastra-ai/mastra": "Full-Stack Agent Platform",
    "langroid/langroid": "Agent Programming Framework",
}


def fetch(limit: int = 5) -> list[dict]:
    """Return top AI agent frameworks from OSSInsight."""
    ranking_payload = fetch_json(
        OSSINSIGHT_RANKING_API,
        params={"period": "past_28_days"},
    )
    rows = ranking_payload.get("data", {}).get("rows", [])
    if not rows:
        raise RuntimeError("No framework rows returned from OSSInsight ranking API")

    sorted_rows = sorted(rows, key=lambda row: _to_int(row.get("current_period_rank")), reverse=False)
    frameworks = []
    for row in sorted_rows[:limit]:
        repo_name = str(row.get("repo_name", "")).strip()
        if not repo_name:
            continue

        metadata = _fetch_repo_metadata(repo_name)
        description = metadata.get("description") or "Open-source agent framework for building LLM applications."
        language = metadata.get("language") or "Unknown"

        frameworks.append({
            "rank": len(frameworks) + 1,
            "name": repo_name,
            "url": metadata.get("html_url") or f"https://github.com/{repo_name}",
            "stars_28d": _to_int(row.get("current_period_growth")),
            "total_stars": _to_int(row.get("total")) or _to_int(metadata.get("stargazers_count")),
            "description": description[:200],
            "category": CATEGORY_HINTS.get(repo_name, "Agent Framework"),
            "language": language,
            "language_color": LANGUAGE_COLORS.get(language, "#586069"),
        })

    logger.info("Fetched %d framework rankings from OSSInsight", len(frameworks))
    return frameworks


def _fetch_repo_metadata(repo_name: str) -> dict:
    """Fetch repo metadata from the public GitHub API."""
    token = os.getenv("GITHUB_TOKEN") or os.getenv("GH_TOKEN")
    headers: dict[str, str] = {
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    if token:
        headers["Authorization"] = f"Bearer {token}"

    try:
        return fetch_json(
            GITHUB_REPO_API.format(repo_name=repo_name),
            headers=headers,
        )
    except Exception as exc:
        logger.warning("GitHub repo metadata fetch failed for %s: %s", repo_name, exc)
        return {
            "html_url": f"https://github.com/{repo_name}",
            "description": "",
            "language": "",
            "stargazers_count": 0,
        }


def _to_int(value: object) -> int:
    """Best-effort integer conversion for API numeric strings."""
    try:
        return int(str(value))
    except (TypeError, ValueError):
        return 0

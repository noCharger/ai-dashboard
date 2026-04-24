"""Fetch top Hacker News stories from the official Firebase API."""

from __future__ import annotations

import logging
from datetime import datetime, timezone
from urllib.parse import urlparse

from .base import fetch_json

logger = logging.getLogger(__name__)

HN_API_BASE = "https://hacker-news.firebaseio.com/v0"


def _story_ids(endpoint: str) -> list[int]:
    data = fetch_json(f"{HN_API_BASE}/{endpoint}.json")
    if not isinstance(data, list):
        return []
    return [int(item_id) for item_id in data if isinstance(item_id, int)]


def _domain(url: str) -> str:
    if not url:
        return "news.ycombinator.com"

    parsed = urlparse(url)
    hostname = parsed.hostname or ""
    return hostname.removeprefix("www.") or "news.ycombinator.com"


def _age_label(unix_time: int | None) -> str:
    if not unix_time:
        return ""

    now = datetime.now(timezone.utc)
    published = datetime.fromtimestamp(unix_time, tz=timezone.utc)
    delta = now - published
    seconds = max(int(delta.total_seconds()), 0)

    if seconds < 3600:
        minutes = max(seconds // 60, 1)
        return f"{minutes}m ago"
    if seconds < 86400:
        hours = seconds // 3600
        return f"{hours}h ago"
    days = seconds // 86400
    return f"{days}d ago"


def _fetch_feed(endpoint: str, limit: int = 5) -> list[dict]:
    ids = _story_ids(endpoint)
    if not ids:
        logger.warning("HN %s feed returned no IDs", endpoint)
        return []

    results: list[dict] = []

    for item_id in ids:
        if len(results) >= limit:
            break

        item = fetch_json(f"{HN_API_BASE}/item/{item_id}.json")
        if not isinstance(item, dict):
            continue

        if item.get("type") != "story" or item.get("deleted") or item.get("dead"):
            continue

        title = str(item.get("title", "")).strip()
        if not title:
            continue

        url = str(item.get("url", "")).strip()
        discussion_url = f"https://news.ycombinator.com/item?id={item_id}"

        results.append(
            {
                "rank": len(results) + 1,
                "id": item_id,
                "title": title,
                "url": url or discussion_url,
                "discussion_url": discussion_url,
                "site": _domain(url),
                "points": int(item.get("score", 0) or 0),
                "comments": int(item.get("descendants", 0) or 0),
                "author": str(item.get("by", "")).strip(),
                "age": _age_label(item.get("time")),
            }
        )

    logger.info("Fetched %d Hacker News stories for %s", len(results), endpoint)
    return results


def fetch_top(limit: int = 5) -> list[dict]:
    return _fetch_feed("topstories", limit)


def fetch_ask(limit: int = 5) -> list[dict]:
    return _fetch_feed("askstories", limit)


def fetch_show(limit: int = 5) -> list[dict]:
    return _fetch_feed("showstories", limit)

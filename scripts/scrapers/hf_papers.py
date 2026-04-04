"""Fetch trending papers from Hugging Face."""

from __future__ import annotations

import logging
from .base import fetch_json

logger = logging.getLogger(__name__)

HF_PAPERS_API = "https://huggingface.co/api/daily_papers"


def fetch(limit: int = 10) -> list[dict]:
    """Return trending papers from HuggingFace daily papers API."""
    try:
        data = fetch_json(HF_PAPERS_API)
    except RuntimeError:
        logger.warning("HF Papers API failed, returning empty list")
        return []

    # API returns a list of paper objects
    papers = data if isinstance(data, list) else []

    # Sort by upvotes descending
    papers.sort(key=lambda p: p.get("paper", {}).get("upvotes", 0), reverse=True)

    results = []
    for i, item in enumerate(papers[:limit], start=1):
        paper = item.get("paper", item)

        title = paper.get("title", "").strip()
        if not title:
            continue

        # Authors
        authors = []
        for a in paper.get("authors", [])[:3]:
            name = a.get("name", "") if isinstance(a, dict) else str(a)
            if name:
                authors.append(name)

        # arXiv ID -> URL
        arxiv_id = paper.get("id", "")
        url = f"https://huggingface.co/papers/{arxiv_id}" if arxiv_id else ""

        upvotes = paper.get("upvotes", 0)
        published = (
            item.get("publishedAt", paper.get("publishedAt", ""))[:10]
            or item.get("createdAt", "")[:10]
        )

        results.append({
            "rank": i,
            "title": title,
            "authors": authors,
            "url": url,
            "categories": [],  # HF papers API doesn't expose arXiv categories
            "upvotes": upvotes,
            "published": published,
        })

    logger.info("Fetched %d trending papers from HuggingFace", len(results))
    return results

"""Fetch trending papers from Hugging Face."""

from __future__ import annotations

import html as html_lib
import json
import logging

from bs4 import BeautifulSoup

from .base import fetch_html, fetch_json

logger = logging.getLogger(__name__)

HF_TRENDING_PAPERS_PAGE = "https://huggingface.co/papers/trending"
HF_PAPERS_API = "https://huggingface.co/api/daily_papers"


def fetch(limit: int = 10) -> list[dict]:
    """Return trending papers from Hugging Face."""
    try:
        data = _fetch_trending_page()
    except RuntimeError:
        logger.warning("HF trending page failed, falling back to daily_papers API")
        try:
            data = fetch_json(HF_PAPERS_API)
        except RuntimeError:
            logger.warning("HF Papers API failed, returning empty list")
            return []
        return _normalize_papers(data if isinstance(data, list) else [], limit, sort_by_upvotes=True)

    results = _normalize_papers(data, limit)
    logger.info("Fetched %d trending papers from HuggingFace", len(results))
    return results


def _fetch_trending_page() -> list[dict]:
    """Extract the current trending list from the public Trending Papers page."""
    html = fetch_html(HF_TRENDING_PAPERS_PAGE)
    soup = BeautifulSoup(html, "lxml")

    for node in soup.find_all("div", attrs={"data-target": "DailyPapers", "data-props": True}):
        raw_props = node.get("data-props", "")
        if "dailyPapers" not in raw_props:
            continue
        try:
            props = json.loads(html_lib.unescape(raw_props))
        except json.JSONDecodeError:
            continue
        papers = props.get("dailyPapers", [])
        if props.get("isTrending") and isinstance(papers, list):
            return papers

    raise RuntimeError("Could not extract trending papers payload from Hugging Face page")


def _normalize_papers(
    papers: list[dict],
    limit: int,
    *,
    sort_by_upvotes: bool = False,
) -> list[dict]:
    """Map Hugging Face paper payloads into dashboard cards."""
    items = list(papers)
    if sort_by_upvotes:
        items.sort(key=lambda p: p.get("paper", {}).get("upvotes", 0), reverse=True)

    results = []
    for item in items:
        paper = item.get("paper", item)
        title = str(paper.get("title", "")).strip()
        if not title:
            continue

        authors = []
        for author in paper.get("authors", [])[:3]:
            name = author.get("name", "") if isinstance(author, dict) else str(author)
            if name:
                authors.append(name)

        arxiv_id = paper.get("id", "")
        url = f"https://huggingface.co/papers/{arxiv_id}" if arxiv_id else ""
        published = (
            item.get("publishedAt")
            or paper.get("publishedAt")
            or paper.get("submittedOnDailyAt")
            or ""
        )[:10]

        results.append({
            "rank": len(results) + 1,
            "title": title,
            "authors": authors,
            "url": url,
            "categories": [],
            "upvotes": paper.get("upvotes", 0),
            "published": published,
        })
        if len(results) >= limit:
            break

    return results

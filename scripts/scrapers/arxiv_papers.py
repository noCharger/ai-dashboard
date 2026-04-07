"""Fetch recent AI papers from the arXiv recent submissions page."""

from __future__ import annotations

from datetime import datetime
import logging
import re

from bs4 import BeautifulSoup

from .base import fetch_html

logger = logging.getLogger(__name__)

ARXIV_RECENT_URL = "https://arxiv.org/list/cs.AI/recent"
DATE_PATTERN = re.compile(r"([A-Z][a-z]{2}, \d{1,2} [A-Z][a-z]{2} \d{4})")
CATEGORY_PATTERN = re.compile(r"\(([a-z]+\.[A-Z]+)\)")


def _parse_header_date(text: str) -> str:
    match = DATE_PATTERN.search(text)
    if not match:
        return ""
    return datetime.strptime(match.group(1), "%a, %d %b %Y").strftime("%Y-%m-%d")


def _clean_text(node) -> str:
    if node is None:
        return ""
    text = node.get_text(" ", strip=True)
    return re.sub(r"\s+", " ", text).strip()


def _parse_recent_page(html: str, limit: int) -> list[dict]:
    """Parse recent submissions HTML into dashboard paper rows."""
    soup = BeautifulSoup(html, "lxml")
    articles = soup.select_one("dl#articles")
    if articles is None:
        logger.warning("arXiv recent page missing article list")
        return []

    results = []
    current_date = ""
    rank = 1

    for child in articles.children:
        name = getattr(child, "name", None)
        if name == "h3":
            current_date = _parse_header_date(_clean_text(child))
            continue
        if name != "dt":
            continue

        item = child.find_next_sibling("dd")
        if item is None:
            continue

        title_node = item.select_one(".list-title")
        title = _clean_text(title_node).removeprefix("Title: ").strip()
        if not title:
            continue

        authors = [_clean_text(author) for author in item.select(".list-authors a")[:3]]
        authors = [author for author in authors if author]

        subjects = _clean_text(item.select_one(".list-subjects"))
        categories = CATEGORY_PATTERN.findall(subjects)[:4]

        abs_link = child.select_one("a[href^='/abs/']")
        href = abs_link.get("href", "") if abs_link else ""
        url = f"https://arxiv.org{href}" if href.startswith("/") else href

        results.append({
            "rank": rank,
            "title": title,
            "authors": authors,
            "url": url,
            "categories": categories,
            "upvotes": None,
            "published": current_date,
        })
        rank += 1

        if len(results) >= limit:
            break

    logger.info("Fetched %d papers from arXiv", len(results))
    return results


def fetch(limit: int = 10) -> list[dict]:
    """Return recent arXiv papers from the cs.AI recent page."""
    html = fetch_html(ARXIV_RECENT_URL)
    return _parse_recent_page(html, limit)

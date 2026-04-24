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
ENTRY_PATTERN = re.compile(r"^\[(\d+)\]\s+arXiv:(\d+\.\d+)")


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
        logger.warning("arXiv recent page missing legacy article list; falling back to text parser")
        return _parse_recent_text(html, limit)

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


def _parse_recent_text(html: str, limit: int) -> list[dict]:
    """Parse the current arXiv recent page text layout."""
    soup = BeautifulSoup(html, "lxml")
    lines = [line.strip() for line in soup.get_text("\n").splitlines()]
    lines = [line for line in lines if line]

    results = []
    current_date = ""
    index = 0

    while index < len(lines) and len(results) < limit:
        line = lines[index]

        if line.startswith("### "):
            current_date = _parse_header_date(line)
            index += 1
            continue

        entry_match = ENTRY_PATTERN.match(line)
        if not entry_match:
            index += 1
            continue

        arxiv_id = entry_match.group(2)
        title = ""
        authors: list[str] = []
        categories: list[str] = []
        index += 1

        while index < len(lines):
            line = lines[index]

            if line.startswith("### ") or ENTRY_PATTERN.match(line):
                break

            if line.startswith("Title: "):
                title = line.removeprefix("Title: ").strip()
            elif line.startswith("Subjects: "):
                categories = CATEGORY_PATTERN.findall(line)[:4]
            elif line.startswith(("Comments: ", "Journal-ref:", "MSC-class:", "ACM-class:")):
                pass
            elif not authors and not line.startswith(("arXiv:", "pdf", "html", "other")):
                # The first free-form line after the title is the author list in the current layout.
                authors = [part.strip() for part in line.split(",")[:3] if part.strip()]

            index += 1

        if not title:
            continue

        results.append(
            {
                "rank": len(results) + 1,
                "title": title,
                "authors": authors,
                "url": f"https://arxiv.org/abs/{arxiv_id}",
                "categories": categories,
                "upvotes": None,
                "published": current_date,
            }
        )

    logger.info("Fetched %d papers from arXiv via text parser", len(results))
    return results


def fetch(limit: int = 10) -> list[dict]:
    """Return recent arXiv papers from the cs.AI recent page."""
    html = fetch_html(ARXIV_RECENT_URL)
    return _parse_recent_page(html, limit)

"""Fetch recent AI papers from arXiv API."""

from __future__ import annotations

import logging
import xml.etree.ElementTree as ET
from .base import fetch_url

logger = logging.getLogger(__name__)

NS = {"atom": "http://www.w3.org/2005/Atom", "arxiv": "http://arxiv.org/schemas/atom"}


def _build_url(limit: int) -> str:
    """Build arXiv API URL with proper encoding for OR queries."""
    q = "cat:cs.AI+OR+cat:cs.CL+OR+cat:cs.LG"
    return (
        f"https://export.arxiv.org/api/query"
        f"?search_query={q}"
        f"&sortBy=submittedDate&sortOrder=descending"
        f"&start=0&max_results={limit}"
    )


def fetch(limit: int = 10) -> list[dict]:
    """Return recent arXiv papers in AI/CL/LG categories."""
    resp = fetch_url(_build_url(limit))

    root = ET.fromstring(resp.text)
    entries = root.findall("atom:entry", NS)

    results = []
    for i, entry in enumerate(entries[:limit], start=1):
        title = (entry.findtext("atom:title", "", NS) or "").strip().replace("\n", " ")
        # Collapse multiple spaces
        while "  " in title:
            title = title.replace("  ", " ")

        authors = []
        for author_el in entry.findall("atom:author", NS)[:3]:
            name = author_el.findtext("atom:name", "", NS)
            if name:
                authors.append(name.strip())

        categories = []
        for cat_el in entry.findall("atom:category", NS):
            term = cat_el.get("term", "")
            if term.startswith("cs."):
                categories.append(term)

        link = ""
        for link_el in entry.findall("atom:link", NS):
            if link_el.get("type") == "text/html":
                link = link_el.get("href", "")
                break
        if not link:
            arxiv_id = (entry.findtext("atom:id", "", NS) or "").strip()
            link = arxiv_id

        published = (entry.findtext("atom:published", "", NS) or "")[:10]

        results.append({
            "rank": i,
            "title": title,
            "authors": authors,
            "url": link,
            "categories": categories[:4],
            "upvotes": None,
            "published": published,
        })

    logger.info("Fetched %d papers from arXiv", len(results))
    return results

"""Scrape GitHub Trending repositories."""

from __future__ import annotations

import logging
import re
from bs4 import BeautifulSoup
from .base import fetch_html

logger = logging.getLogger(__name__)

TRENDING_URL = "https://github.com/trending"


def _parse_number(text: str) -> int:
    """Parse '1,234' or '1.2k' into an integer."""
    text = text.strip().replace(",", "")
    if not text:
        return 0
    if "k" in text.lower():
        return int(float(text.lower().replace("k", "")) * 1000)
    try:
        return int(text)
    except ValueError:
        return 0


def _fetch_period(since: str, limit: int = 5) -> list[dict]:
    """Fetch trending repos for a given time period."""
    html = fetch_html(TRENDING_URL, params={"since": since})
    soup = BeautifulSoup(html, "lxml")

    articles = soup.select("article.Box-row")
    results = []

    for i, article in enumerate(articles[:limit], start=1):
        # Repo name
        h2 = article.select_one("h2 a")
        if not h2:
            continue
        repo_name = h2.get_text(strip=True).replace(" ", "").replace("\n", "")
        url = "https://github.com" + h2.get("href", "")

        # Description
        p = article.select_one("p")
        description = p.get_text(strip=True) if p else ""

        # Total stars
        star_links = article.select("a.Link--muted")
        stars = 0
        for sl in star_links:
            href = sl.get("href", "")
            if "/stargazers" in href:
                stars = _parse_number(sl.get_text())
                break

        # Stars delta (today/this week/this month)
        stars_delta = 0
        delta_span = article.select_one("span.d-inline-block.float-sm-right")
        if delta_span:
            nums = re.findall(r"[\d,]+", delta_span.get_text())
            if nums:
                stars_delta = _parse_number(nums[0])

        # Language
        language = ""
        language_color = "#586069"
        lang_span = article.select_one("[itemprop='programmingLanguage']")
        if lang_span:
            language = lang_span.get_text(strip=True)
            color_span = lang_span.find_previous_sibling("span")
            if color_span:
                style = color_span.get("style", "")
                color_match = re.search(r"background-color:\s*(#[0-9a-fA-F]+)", style)
                if color_match:
                    language_color = color_match.group(1)

        results.append({
            "rank": i,
            "name": repo_name,
            "description": description[:200],
            "url": url,
            "stars": stars,
            "stars_delta": stars_delta,
            "language": language,
            "language_color": language_color,
        })

    logger.info("Fetched %d trending repos (since=%s)", len(results), since)
    return results


def fetch_daily(limit: int = 5) -> list[dict]:
    return _fetch_period("daily", limit)


def fetch_weekly(limit: int = 5) -> list[dict]:
    return _fetch_period("weekly", limit)


def fetch_monthly(limit: int = 5) -> list[dict]:
    return _fetch_period("monthly", limit)

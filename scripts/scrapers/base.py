"""Shared utilities for all scrapers."""

from __future__ import annotations

import json
import time
import logging
from pathlib import Path
from typing import Any

import requests

logger = logging.getLogger(__name__)

DATA_DIR = Path(__file__).resolve().parent.parent.parent / "data"

# Polite defaults
DEFAULT_TIMEOUT = 30
DEFAULT_RETRIES = 3
DEFAULT_BACKOFF = 2  # seconds
USER_AGENT = "ai-dashboard-scraper/1.0 (https://github.com/noCharger)"


def fetch_url(
    url: str,
    *,
    headers: dict[str, str] | None = None,
    params: dict[str, str] | None = None,
    timeout: int = DEFAULT_TIMEOUT,
    retries: int = DEFAULT_RETRIES,
) -> requests.Response:
    """GET a URL with retry and backoff."""
    hdrs = {"User-Agent": USER_AGENT}
    if headers:
        hdrs.update(headers)

    last_exc: Exception | None = None
    for attempt in range(1, retries + 1):
        try:
            resp = requests.get(url, headers=hdrs, params=params, timeout=timeout)
            resp.raise_for_status()
            return resp
        except requests.RequestException as exc:
            last_exc = exc
            if attempt < retries:
                wait = DEFAULT_BACKOFF * attempt
                logger.warning(
                    "Attempt %d/%d failed for %s: %s — retrying in %ds",
                    attempt, retries, url, exc, wait,
                )
                time.sleep(wait)
    raise RuntimeError(f"All {retries} attempts failed for {url}") from last_exc


def fetch_json(url: str, **kwargs: Any) -> Any:
    """GET a URL and parse JSON response."""
    resp = fetch_url(url, **kwargs)
    return resp.json()


def fetch_html(url: str, **kwargs: Any) -> str:
    """GET a URL and return the HTML text."""
    resp = fetch_url(url, **kwargs)
    return resp.text


def write_json(data: Any, filename: str) -> Path:
    """Write data to DATA_DIR/<filename>."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    path = DATA_DIR / filename
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        f.write("\n")
    logger.info("Wrote %s", path)
    return path

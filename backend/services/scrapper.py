"""
services/scrapper.py — URL → ParseUrlData

Uses newspaper3k to download and parse articles.
Runs the blocking newspaper3k call in a thread executor
so it stays async-friendly inside FastAPI.
"""

import asyncio
from urllib.parse import urlparse

from newspaper import Article
from fastapi import HTTPException


async def extract_article(url: str) -> dict:
    """
    Download and parse an article from the given URL.

    Returns a dict that maps 1:1 to the ParseUrlData schema:
      { headline, body, author, publish_date, url, domain }

    Raises HTTPException on failure so FastAPI returns a clean error.
    """
    try:
        article = Article(url, request_timeout=10)

        # newspaper3k is synchronous — offload to a thread so we
        # never block the event loop.
        loop = asyncio.get_running_loop()
        await loop.run_in_executor(None, article.download)
        await loop.run_in_executor(None, article.parse)

    except Exception as e:
        raise HTTPException(
            status_code=502,
            detail=f"Failed to fetch or parse the article: {str(e)}",
        )

    # ── Validate we actually got content ──────────────────────
    if not article.text or len(article.text.strip()) < 50:
        raise HTTPException(
            status_code=422,
            detail="Could not extract meaningful text from this URL.",
        )

    # ── Build the dict matching ParseUrlData exactly ──────────
    parsed = urlparse(url)

    return {
        "headline": article.title or "No headline found",
        "body": article.text,
        "author": ", ".join(article.authors) if article.authors else None,
        "publish_date": (
            article.publish_date.isoformat() if article.publish_date else None
        ),
        "url": str(url),
        "domain": parsed.netloc,
    }

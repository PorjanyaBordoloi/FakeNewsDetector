"""
services/cross_ref.py — Claims → CrossReferenceData

Hits the NewsAPI /v2/everything endpoint with httpx.AsyncClient()
for each claim, classifies stance heuristically, and returns a dict
matching the CrossReferenceData schema exactly.
"""

import httpx
from fastapi import HTTPException

from core.config import settings

# ── Constants ─────────────────────────────────────────────
NEWSAPI_BASE = "https://newsapi.org/v2/everything"
REQUEST_TIMEOUT = 10.0


async def verify_claims(claims: list[str]) -> dict:
    """
    Cross-reference a list of claims against NewsAPI.

    Returns a dict matching CrossReferenceData:
      { sources_found, supporting, contradicting, neutral, articles }
    """
    if not settings.NEWS_API:
        raise HTTPException(
            status_code=503,
            detail="NEWS_API key is not configured in .env",
        )

    all_articles: list[dict] = []

    async with httpx.AsyncClient(timeout=REQUEST_TIMEOUT) as client:
        for claim in claims:
            try:
                response = await client.get(
                    NEWSAPI_BASE,
                    params={
                        "q": claim,
                        "sortBy": "relevancy",
                        "pageSize": 5,
                        "language": "en",
                        "apiKey": settings.NEWS_API,
                    },
                )
                response.raise_for_status()
                data = response.json()

            except httpx.TimeoutException:
                # Don't crash — just skip this claim
                continue
            except httpx.HTTPStatusError as e:
                raise HTTPException(
                    status_code=502,
                    detail=f"NewsAPI returned {e.response.status_code}: {e.response.text}",
                )
            except Exception as e:
                raise HTTPException(
                    status_code=502,
                    detail=f"Failed to reach NewsAPI: {str(e)}",
                )

            # ── Process articles from this claim ──────────
            for article in data.get("articles", []):
                stance = _classify_stance(claim, article)
                all_articles.append(
                    {
                        "title": article.get("title", ""),
                        "url": article.get("url", ""),
                        "source": article.get("source", {}).get("name", "Unknown"),
                        "published": article.get("publishedAt"),
                        "stance": stance,
                        "relevance_score": _compute_relevance(claim, article),
                    }
                )

    # ── Aggregate counts ──────────────────────────────────
    supporting = sum(1 for a in all_articles if a["stance"] == "supports")
    contradicting = sum(1 for a in all_articles if a["stance"] == "contradicts")
    neutral = sum(1 for a in all_articles if a["stance"] == "neutral")

    return {
        "sources_found": len(all_articles),
        "supporting": supporting,
        "contradicting": contradicting,
        "neutral": neutral,
        "articles": all_articles,
    }


# ── Private helpers ───────────────────────────────────────

_CONTRADICT_SIGNALS = [
    "false", "fake", "hoax", "debunk", "misleading",
    "incorrect", "not true", "disinformation", "misinformation",
    "fabricated", "unverified", "rumor", "conspiracy",
]

_SUPPORT_SIGNALS = [
    "confirmed", "verified", "true", "accurate",
    "corroborated", "supports", "evidence shows",
    "fact check: true", "legitimate",
]


def _classify_stance(claim: str, article: dict) -> str:
    """
    Lightweight keyword-based stance detection.
    Scans the article title + description for support / contradict signals.
    """
    text = " ".join(
        [
            (article.get("title") or ""),
            (article.get("description") or ""),
        ]
    ).lower()

    contradict_hits = sum(1 for kw in _CONTRADICT_SIGNALS if kw in text)
    support_hits = sum(1 for kw in _SUPPORT_SIGNALS if kw in text)

    if contradict_hits > support_hits:
        return "contradicts"
    if support_hits > contradict_hits:
        return "supports"
    return "neutral"


def _compute_relevance(claim: str, article: dict) -> float:
    """
    Simple word-overlap relevance score between the claim and
    the article's title + description. Returns 0.0–1.0.
    """
    claim_words = set(claim.lower().split())
    article_text = " ".join(
        [
            (article.get("title") or ""),
            (article.get("description") or ""),
        ]
    ).lower()
    article_words = set(article_text.split())

    if not claim_words:
        return 0.0

    overlap = claim_words & article_words
    return round(len(overlap) / len(claim_words), 2)

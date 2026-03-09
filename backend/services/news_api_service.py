"""
News API Service

Wrapper for the News API used by Agent 3 (Cross-Reference Validator)
for cross-referencing against 80k+ trusted news sources.
"""

import os
import logging

import httpx

logger = logging.getLogger(__name__)


class NewsAPIService:
    """News API wrapper for cross-referencing articles."""

    def __init__(self):
        self.api_key = os.getenv("NEWS_API_KEY")
        self.base_url = "https://newsapi.org/v2"

    async def search_articles(self, headline: str) -> dict:
        """
        Search News API for articles related to the given headline.

        Args:
            headline: The headline or topic to search for.

        Returns:
            News API response as a dict.
        """
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/everything",
                params={
                    "q": headline,
                    "sources": "reuters,associated-press,bbc-news,the-guardian-uk",
                    "language": "en",
                    "sortBy": "relevancy",
                    "apiKey": self.api_key,
                },
            )
            return response.json()

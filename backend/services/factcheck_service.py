"""
Google Fact Check Tools API Service

Wrapper for the Google Fact Check Tools API used by Agent 3
(Cross-Reference Validator) for checking existing fact-checks.
"""

import os
import logging

import httpx

logger = logging.getLogger(__name__)


class FactCheckService:
    """Google Fact Check Tools API wrapper."""

    def __init__(self):
        self.api_key = os.getenv("GOOGLE_FACTCHECK_API_KEY")
        self.base_url = "https://factchecktools.googleapis.com/v1alpha1"

    async def search_claims(self, claim: str) -> dict:
        """
        Search Google Fact Check database for existing fact-checks.

        Args:
            claim: The claim to search for.

        Returns:
            Google Fact Check API response as a dict.
        """
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/claims:search",
                params={
                    "query": claim,
                    "key": self.api_key,
                },
            )
            return response.json()

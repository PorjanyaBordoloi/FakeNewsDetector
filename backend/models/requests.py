"""
Pydantic Request Models

Defines request schemas for the API endpoints.
"""

from pydantic import BaseModel, HttpUrl


class AnalyzeRequest(BaseModel):
    """Request body for /api/analyze-stream and /api/analyze-simple."""

    url: HttpUrl
    user_agent: str = "FakeNewsDetector/1.0"

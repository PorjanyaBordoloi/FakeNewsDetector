"""
core/schema.py — The Absolute Source of Truth

Every function in this codebase type-hints against these models.
Every API response is wrapped in StandardResponse.
No generic dicts. No implicit types. Karpathy Principle enforced.

Pydantic V2 ONLY — use model_dump(), not dict().
"""

from datetime import datetime
from pydantic import BaseModel, HttpUrl, Field
from typing import List, Optional, Literal, Any


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# GENERIC RESPONSE WRAPPER
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

class ErrorDetail(BaseModel):
    """Structured error payload inside StandardResponse."""
    code: str
    message: str


class StandardResponse(BaseModel):
    """Every API endpoint returns this envelope."""
    success: bool = True
    data: Optional[Any] = None
    error: Optional[ErrorDetail] = None


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 1. PARSE URL — Scraper input/output
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

class ParseUrlRequest(BaseModel):
    """POST /api/parse-url — request body."""
    url: HttpUrl


class ParseUrlData(BaseModel):
    """Scraped article data returned by the scraper service."""
    headline: str
    body: str
    author: Optional[str] = None
    publish_date: Optional[str] = None
    url: str
    domain: str


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 2. ANALYZE — ML classification input/output
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

class AnalyzeRequest(BaseModel):
    """POST /api/analyze — request body."""
    text: str
    headline: Optional[str] = None


class RedFlag(BaseModel):
    """Individual red-flag detected by the ML pipeline."""
    type: str
    severity: Literal["low", "medium", "high", "critical"]
    examples: Optional[List[str]] = None
    count: Optional[int] = None
    details: Optional[str] = None


class AnalyzeData(BaseModel):
    """ML classification result."""
    credibility_score: int = Field(ge=0, le=100)
    prediction: Literal["real", "fake", "uncertain"]
    confidence: float = Field(ge=0.0, le=1.0)
    red_flags: List[RedFlag] = []
    explanation: str


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 3. CROSS-REFERENCE — Fact-check verification input/output
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

class CrossReferenceRequest(BaseModel):
    """POST /api/cross-reference — request body."""
    headline: str
    key_claims: List[str]


class ArticleMatch(BaseModel):
    """A single corroborating / contradicting article from external APIs."""
    title: str
    url: str
    source: str
    published: Optional[str] = None
    stance: Literal["supports", "contradicts", "neutral"]
    relevance_score: float = Field(ge=0.0, le=1.0)


class CrossReferenceData(BaseModel):
    """Aggregated cross-reference results."""
    sources_found: int = Field(ge=0)
    supporting: int = Field(ge=0)
    contradicting: int = Field(ge=0)
    neutral: int = Field(ge=0)
    articles: List[ArticleMatch] = []


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 4. FULL CHECK — Master pipeline composite response
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

class FullCheckData(BaseModel):
    """POST /api/full-check — composite response.

    Strongly typed: no generic dicts.
    """
    article: ParseUrlData
    analysis: AnalyzeData
    cross_reference: CrossReferenceData
    timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat())
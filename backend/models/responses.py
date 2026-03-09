"""
Pydantic Response Models

Defines response schemas for the API endpoints matching the
agent output contracts from the instructions.
"""

from typing import List, Optional
from pydantic import BaseModel


# ── Red Flag ──────────────────────────────────────────────
class RedFlag(BaseModel):
    type: str  # exaggerated_claims | unsupported_statistics | contradicted_by_sources | missing_attribution
    description: str
    severity: str  # low | medium | high | critical


# ── LLM Analysis ─────────────────────────────────────────
class LLMAnalysis(BaseModel):
    authenticity_verdict: str  # REAL | FAKE | MISLEADING | UNVERIFIED
    confidence: float  # 0.0 – 1.0
    reasoning: str
    red_flags: List[RedFlag]
    supporting_evidence: List[str]
    contradicting_evidence: List[str]


# ── Source Info ───────────────────────────────────────────
class SourceInfo(BaseModel):
    source: str
    title: str
    url: str
    relevance: str


# ── Agent Chain Entry ────────────────────────────────────
class AgentChainEntry(BaseModel):
    agent: str
    status: str
    thought: str
    timestamp: str


# ── Final Analysis ───────────────────────────────────────
class AnalysisResult(BaseModel):
    headline: str
    source: str
    verdict: str
    score: int
    reasoning: str
    red_flags: List[RedFlag]
    sources_checked: dict
    corroborating_sources: List[SourceInfo]
    contradicting_sources: List[SourceInfo]


# ── Full Response ────────────────────────────────────────
class FullAnalysisResponse(BaseModel):
    success: bool
    final_verdict: str
    authenticity_score: int
    confidence: str
    agent_chain: List[AgentChainEntry]
    analysis: AnalysisResult
    timestamp: str


# ── Simple Response (Chrome Extension) ───────────────────
class SimpleAnalysisResponse(BaseModel):
    score: int
    verdict: str
    confidence: str

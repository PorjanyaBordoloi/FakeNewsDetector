"""
Agent 2: Fact Checker & LLM Analyzer

Responsibilities:
  1. Receive extracted article from Agent 1
  2. Extract key claims from headline and body
  3. Query Tavily API for real-world verification
  4. Compile Tavily results into markdown report
  5. Feed markdown + original article to LLM (Claude API)
  6. Get natural language analysis of authenticity
  7. Output reasoning and initial verdict

Technologies: Tavily API, Anthropic Claude API, spaCy/NLTK (optional)
"""

import logging
from datetime import datetime, timezone

logger = logging.getLogger(__name__)


class FactCheckerAgent:
    """Agent 2 — Verifies claims using Tavily + LLM reasoning."""

    AGENT_NAME = "fact_checker"

    async def run(self, parser_output: dict) -> dict:
        """
        Verify claims from the parsed article.

        Args:
            parser_output: Output dict from Agent 1 (ParserAgent).

        Returns a dict matching the Agent 2 output schema:
        {
            "success": bool,
            "agent": "fact_checker",
            "thought": str,
            "data": {
                "tavily_results": {
                    "claims_checked": int,
                    "sources_found": int,
                    "supporting": int,
                    "contradicting": int
                },
                "llm_analysis": {
                    "authenticity_verdict": "REAL" | "FAKE" | "MISLEADING" | "UNVERIFIED",
                    "confidence": float,
                    "reasoning": str,
                    "red_flags": list,
                    "supporting_evidence": list,
                    "contradicting_evidence": list
                }
            },
            "timestamp": str (ISO-8601)
        }
        """
        # TODO: Implement claim extraction, Tavily search, markdown report, and LLM analysis
        raise NotImplementedError("FactCheckerAgent.run() is not yet implemented.")

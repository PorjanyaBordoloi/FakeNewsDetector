"""
Scoring Utility

Custom scoring algorithm for calculating the final authenticity score (0-100).
Used by Agent 3 (Cross-Reference Validator).
"""

import logging

logger = logging.getLogger(__name__)


def calculate_score(agent2_data: dict, cross_ref_data: dict) -> int:
    """
    Calculate the final authenticity score (0-100).

    Scoring logic (from instructions):
      - Base score: 50 (neutral)
      - LLM verdict: REAL +30, FAKE -40, MISLEADING -20
      - Tavily supporting sources: +5 each (max +20)
      - Tavily contradicting sources: -10 each (max -30)
      - News API corroboration: >=3 articles +15, 0 articles -15
      - Red flags: critical -15, high -10, medium -5

    Args:
        agent2_data: The 'data' dict from Agent 2 output.
        cross_ref_data: Cross-reference results from Agent 3 sources.

    Returns:
        Authenticity score clamped to 0-100.
    """
    base_score = 50  # Neutral starting point

    # Adjust based on LLM verdict
    verdict = agent2_data["llm_analysis"]["authenticity_verdict"]
    if verdict == "REAL":
        base_score += 30
    elif verdict == "FAKE":
        base_score -= 40
    elif verdict == "MISLEADING":
        base_score -= 20

    # Adjust based on Tavily results
    supporting = agent2_data["tavily_results"]["supporting"]
    contradicting = agent2_data["tavily_results"]["contradicting"]

    base_score += min(supporting * 5, 20)   # Max +20
    base_score -= min(contradicting * 10, 30)  # Max -30

    # Adjust based on News API cross-reference
    corroborating = cross_ref_data.get("news_api", {}).get("corroborating_articles", 0)
    if corroborating >= 3:
        base_score += 15
    elif corroborating == 0:
        base_score -= 15

    # Adjust based on red flags
    for flag in agent2_data["llm_analysis"].get("red_flags", []):
        severity = flag.get("severity", "low")
        if severity == "critical":
            base_score -= 15
        elif severity == "high":
            base_score -= 10
        elif severity == "medium":
            base_score -= 5

    # Clamp to 0-100
    return max(0, min(100, base_score))

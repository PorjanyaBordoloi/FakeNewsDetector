"""
Markdown Report Generator

Compiles Tavily fact-check results into a structured markdown report
that is fed to the LLM for analysis (Agent 2, Step 2.3).
"""

import logging

logger = logging.getLogger(__name__)


def generate_tavily_report(claims_results: list[dict]) -> str:
    """
    Generate a markdown report from Tavily fact-check results.

    Args:
        claims_results: List of dicts, each containing:
            - claim (str)
            - sources (list of dicts with 'name', 'url', 'relevance', 'title', 'supports' bool)
            - verdict (str): SUPPORTED | CONTRADICTED | UNVERIFIED

    Returns:
        Formatted markdown report string.
    """
    # TODO: Implement markdown report generation matching the template in instructions
    raise NotImplementedError("generate_tavily_report() is not yet implemented.")

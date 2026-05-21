"""
Evaluation tools for assessing agent output quality.

This is the 'AI judging AI' pattern (LLM-as-judge) used in production agentic systems
at OpenAI, Anthropic, and Google to monitor agent quality at scale.
"""


def score_response(
    query: str,
    response: str,
    completeness: int,
    factual_grounding: int,
    specificity: int,
    structure: int,
    suggestion: str = ""
) -> dict:
    """
    Record a structured evaluation of an agent response.

    Use this tool to formally score a travel system response after analyzing it.
    All scores are on a 1-10 scale.

    Args:
        query: The original user query being evaluated
        response: The final answer the travel system produced
        completeness: 1-10 — Did the answer address every part of the query?
        factual_grounding: 1-10 — Are claims supported by tool outputs (not invented)?
        specificity: 1-10 — Are numbers, dates, names concrete rather than vague?
        structure: 1-10 — Is the answer well-organized and easy to read?
        suggestion: One-sentence improvement suggestion if any score is below 8

    Returns:
        A structured evaluation dictionary with overall score and breakdown.
    """
    scores = {
        "completeness": completeness,
        "factual_grounding": factual_grounding,
        "specificity": specificity,
        "structure": structure,
    }
    overall = round(sum(scores.values()) / len(scores), 2)

    return {
        "query": query,
        "overall_score": overall,
        "breakdown": scores,
        "suggestion": suggestion or "No improvements suggested.",
        "passed": overall >= 7.0,
    }
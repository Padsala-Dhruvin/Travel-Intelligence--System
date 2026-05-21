"""
General web search tool for grounding agent answers in current information.
"""
from duckduckgo_search import DDGS


def web_search(query: str, max_results: int = 5) -> dict:
    """
    Search the web for current information.

    Use this for cost estimates, recent travel advisories, or any information
    that may have changed recently. Prefer specialized tools (weather, country_info)
    when available.

    Args:
        query: Search query, e.g. "flight cost Frankfurt to Tokyo June 2026"
        max_results: Number of results to return (default 5)

    Returns:
        Dictionary with a list of result snippets.
    """
    try:
        with DDGS() as ddgs:
            results = list(ddgs.text(query, max_results=max_results))
        return {
            "query": query,
            "results": [
                {"title": r.get("title"), "snippet": r.get("body"), "url": r.get("href")}
                for r in results
            ],
        }
    except Exception as e:
        return {"error": f"Search failed: {str(e)}"}
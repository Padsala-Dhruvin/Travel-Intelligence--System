"""
Destination information tools — visa, currency, language, summaries.
"""
import requests


def get_country_info(country_name: str) -> dict:
    """
    Get basic information about a country: capital, currency, languages, region.

    Use this when the user asks about a destination's practical details
    like what currency to bring or what language is spoken.

    Args:
        country_name: Country name, e.g. "Japan", "Iceland"

    Returns:
        Dictionary with country information, or an error.
    """
    try:
        url = f"https://restcountries.com/v3.1/name/{country_name}"
        response = requests.get(url, timeout=10)
        if response.status_code != 200:
            return {"error": f"Country '{country_name}' not found"}
        data = response.json()[0]
        return {
            "name": data["name"]["common"],
            "capital": data.get("capital", ["Unknown"])[0],
            "region": data.get("region"),
            "subregion": data.get("subregion"),
            "currencies": list(data.get("currencies", {}).keys()),
            "languages": list(data.get("languages", {}).values()),
            "population": data.get("population"),
        }
    except requests.RequestException as e:
        return {"error": f"Network error: {str(e)}"}


def wikipedia_summary(topic: str) -> dict:
    """
    Get a short Wikipedia summary about a place or topic.

    Useful for destination overviews, cultural context, or famous attractions.

    Args:
        topic: The topic or place name, e.g. "Tokyo", "Iceland tourism"

    Returns:
        Dictionary with title, summary, and URL.
    """
    try:
        topic_encoded = topic.replace(" ", "_")
        url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{topic_encoded}"
        response = requests.get(url, timeout=10)
        if response.status_code != 200:
            return {"error": f"No Wikipedia entry for '{topic}'"}
        data = response.json()
        return {
            "title": data.get("title"),
            "summary": data.get("extract"),
            "url": data.get("content_urls", {}).get("desktop", {}).get("page"),
        }
    except requests.RequestException as e:
        return {"error": f"Network error: {str(e)}"}
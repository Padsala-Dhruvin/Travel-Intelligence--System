"""
Budget estimation tools.

Note: We don't have access to real-time flight/hotel APIs (those require paid keys).
So we combine web search + LLM reasoning to estimate costs. This is a real
production pattern called "tool-augmented estimation."
"""
import requests


def get_exchange_rate(from_currency: str, to_currency: str) -> dict:
    """
    Get the current exchange rate between two currencies.

    Args:
        from_currency: ISO currency code, e.g. "EUR", "USD", "JPY"
        to_currency: ISO currency code to convert to

    Returns:
        Dictionary with the exchange rate, or an error.
    """
    try:
        url = f"https://api.frankfurter.app/latest?from={from_currency}&to={to_currency}"
        response = requests.get(url, timeout=10)
        data = response.json()
        rate = data.get("rates", {}).get(to_currency)
        if rate is None:
            return {"error": f"Could not get rate for {from_currency} to {to_currency}"}
        return {
            "from": from_currency,
            "to": to_currency,
            "rate": rate,
            "date": data.get("date"),
        }
    except requests.RequestException as e:
        return {"error": f"Network error: {str(e)}"}


def estimate_daily_budget(country: str, tier: str = "budget") -> dict:
    """
    Provide a rough daily budget estimate for travelers in a given country.

    This uses standard backpacker/mid-range/luxury daily cost estimates.

    Args:
        country: Destination country, e.g. "Japan", "Iceland"
        tier: One of "budget", "mid", "luxury"

    Returns:
        Dictionary with estimated daily cost in EUR.
    """
    # Simplified lookup — in production this would query a real cost-of-living DB.
    # We're transparent about this being an estimate; the agent will combine it
    # with web search results for better grounding.
    cost_table = {
        "japan":   {"budget": 60,  "mid": 130, "luxury": 300},
        "iceland": {"budget": 90,  "mid": 180, "luxury": 400},
        "germany": {"budget": 50,  "mid": 110, "luxury": 250},
        "france":  {"budget": 55,  "mid": 120, "luxury": 280},
        "usa":     {"budget": 70,  "mid": 150, "luxury": 350},
        "thailand":{"budget": 25,  "mid": 60,  "luxury": 180},
    }
    key = country.lower()
    if key not in cost_table:
        return {
            "country": country,
            "note": "No baseline data; use web search for estimate",
            "available_countries": list(cost_table.keys()),
        }
    return {
        "country": country,
        "tier": tier,
        "daily_eur": cost_table[key].get(tier, cost_table[key]["budget"]),
    }
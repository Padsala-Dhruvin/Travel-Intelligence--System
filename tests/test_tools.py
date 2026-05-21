"""
Quick smoke tests for tools. Run these before wiring tools to agents.

Why: When an agent gives a bad answer, you need to rule out tool bugs first.
"""
from tools.weather_tools import geocode_city, get_weather_forecast
from tools.budget_tools import get_exchange_rate, estimate_daily_budget
from tools.destination_tools import get_country_info, wikipedia_summary
from tools.search_tools import web_search


def test_all_tools():
    print("=== Geocoding ===")
    result = geocode_city("Tokyo")
    print(result)
    assert "latitude" in result

    print("\n=== Weather ===")
    forecast = get_weather_forecast(result["latitude"], result["longitude"], days=3)
    print(forecast)
    assert "forecast" in forecast

    print("\n=== Exchange Rate ===")
    print(get_exchange_rate("EUR", "JPY"))

    print("\n=== Country Info ===")
    print(get_country_info("Japan"))

    print("\n=== Wikipedia ===")
    print(wikipedia_summary("Tokyo"))

    print("\n=== Search ===")
    print(web_search("flight cost Frankfurt to Tokyo", max_results=2))

    print("\n✅ All tools working")


if __name__ == "__main__":
    test_all_tools()
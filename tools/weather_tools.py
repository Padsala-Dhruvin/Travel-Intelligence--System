"""
Weather tools for the travel intelligence system.

Why standalone functions: ADK turns Python functions into LLM tools automatically.
The function's docstring becomes the description the LLM uses to decide when to call it.
So docstrings here are not optional — they're prompts.
"""
import requests
from typing import Optional


def geocode_city(city: str) -> dict:
    """
    Convert a city name into latitude and longitude coordinates.

    Use this tool when you need geographic coordinates for a city,
    typically as a prerequisite for weather lookup.

    Args:
        city: The name of the city, e.g. "Tokyo" or "Frankfurt"

    Returns:
        A dictionary with 'latitude', 'longitude', and 'country' keys,
        or an 'error' key if the city was not found.
    """
    try:
        url = f"https://geocoding-api.open-meteo.com/v1/search?name={city}&count=1"
        response = requests.get(url, timeout=10)
        data = response.json()

        if not data.get("results"):
            return {"error": f"City '{city}' not found"}

        result = data["results"][0]
        return {
            "latitude": result["latitude"],
            "longitude": result["longitude"],
            "country": result.get("country", "Unknown"),
            "city": result["name"],
        }
    except requests.RequestException as e:
        return {"error": f"Network error: {str(e)}"}


def get_weather_forecast(latitude: float, longitude: float, days: int = 5) -> dict:
    """
    Get a daily weather forecast for given coordinates.

    Use this tool after geocoding a city to get its actual weather forecast.
    Returns daily max/min temperatures and precipitation.

    Args:
        latitude: The latitude of the location
        longitude: The longitude of the location
        days: Number of forecast days (1 to 16). Default 5.

    Returns:
        A dictionary with daily forecast data including temperatures and rainfall.
    """
    try:
        url = (
            f"https://api.open-meteo.com/v1/forecast?"
            f"latitude={latitude}&longitude={longitude}"
            f"&daily=temperature_2m_max,temperature_2m_min,precipitation_sum,weathercode"
            f"&forecast_days={days}&timezone=auto"
        )
        response = requests.get(url, timeout=10)
        data = response.json()

        daily = data.get("daily", {})
        forecast = []
        for i in range(len(daily.get("time", []))):
            forecast.append({
                "date": daily["time"][i],
                "temp_max_c": daily["temperature_2m_max"][i],
                "temp_min_c": daily["temperature_2m_min"][i],
                "rainfall_mm": daily["precipitation_sum"][i],
            })
        return {"forecast": forecast, "days": len(forecast)}
    except requests.RequestException as e:
        return {"error": f"Network error: {str(e)}"}
from google.adk.agents import LlmAgent
from tools.weather_tools import geocode_city, get_weather_forecast

weather_agent = LlmAgent(
    name="weather_agent",
    model="gemini-2.0-flash",
    description=(
        "Specialist for weather forecasts and packing recommendations. "
        "Delegate to this agent for any questions about weather, climate, "
        "temperature, rainfall, or what clothing to pack."
    ),
    instruction=(
        "You are a weather specialist. When asked about weather in a city:\n"
        "1. Call geocode_city to get coordinates.\n"
        "2. Call get_weather_forecast with those coordinates and the requested number of days.\n"
        "3. Summarize the forecast in plain language.\n"
        "4. Suggest what to pack based on the forecast.\n"
        "Always include temperature ranges in Celsius. Be concise."
    ),
    tools=[geocode_city, get_weather_forecast],
)
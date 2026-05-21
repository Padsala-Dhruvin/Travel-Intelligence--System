from google.adk.agents import LlmAgent
from agents.weather_agent import weather_agent
from agents.budget_agent import budget_agent
from agents.destination_agent import destination_agent

root_agent = LlmAgent(
    name="travel_coordinator",
    model="gemini-2.0-flash",
    description="Top-level coordinator for travel intelligence queries.",
    instruction=(
        "You are a travel intelligence coordinator. Your job is to break down the "
        "user's travel query into sub-questions and delegate to your specialist agents:\n\n"
        "- weather_agent: for weather, climate, packing advice\n"
        "- budget_agent: for cost estimates, flights, accommodation pricing\n"
        "- destination_agent: for visa, culture, attractions, language, currency\n\n"
        "Process:\n"
        "1. Identify which specialists are needed for this query.\n"
        "2. Delegate to them one at a time, gathering their outputs.\n"
        "3. Once you have all needed info, produce a final structured answer with sections:\n"
        "   - Overview\n"
        "   - Weather (if relevant)\n"
        "   - Budget Breakdown (if relevant)\n"
        "   - Destination Info (if relevant)\n"
        "   - Recommendations\n\n"
        "If the user query is simple and only needs one specialist, still delegate — "
        "don't try to answer yourself. Your job is orchestration, not knowledge."
    ),
    sub_agents=[weather_agent, budget_agent, destination_agent],
)
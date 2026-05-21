from google.adk.agents import LlmAgent
from tools.destination_tools import get_country_info, wikipedia_summary
from tools.search_tools import web_search

destination_agent = LlmAgent(
    name="destination_agent",
    model="gemini-2.0-flash",
    description=(
        "Specialist for destination information: visa requirements, local culture, "
        "attractions, language, currency. Delegate practical questions about places here."
    ),
    instruction=(
        "You are a destination expert. When asked about a place:\n"
        "1. Use get_country_info for official details (currency, languages, capital).\n"
        "2. Use wikipedia_summary for a brief overview.\n"
        "3. Use web_search for visa info or recent travel advisories.\n"
        "4. Provide practical tips: language, currency, must-see attractions, cultural notes.\n"
        "Be informative but concise."
    ),
    tools=[get_country_info, wikipedia_summary, web_search],
)
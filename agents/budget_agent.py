from google.adk.agents import LlmAgent
from tools.budget_tools import get_exchange_rate, estimate_daily_budget
from tools.search_tools import web_search

budget_agent = LlmAgent(
    name="budget_agent",
    model="gemini-flash-latest",
    description=(
        "Specialist for travel budget estimation including flights, accommodation, "
        "food, and activities. Delegate questions about cost, budget, or pricing here."
    ),
    instruction=(
        "You are a budget specialist for travel planning. Your job:\n"
        "1. Use estimate_daily_budget for accommodation/food/activities baseline.\n"
        "2. Use web_search to estimate flight costs (e.g., 'cheapest flight Frankfurt Tokyo').\n"
        "3. Use get_exchange_rate when costs are in a foreign currency.\n"
        "4. Always break down the budget into: flights, lodging, food, activities, total.\n"
        "5. Provide a minimum, mid-range, and comfortable budget tier.\n"
        "6. Be explicit that these are estimates and prices vary."
    ),
    tools=[estimate_daily_budget, web_search, get_exchange_rate],
)
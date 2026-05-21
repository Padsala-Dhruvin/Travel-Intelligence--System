from google.adk.agents import LlmAgent
from tools.evaluation_tools import score_response

evaluator_agent = LlmAgent(
    name="evaluator_agent",
    model="gemini-flash-latest",  # use the same model you settled on
    description=(
        "Quality assurance specialist. Delegate to this agent AFTER the travel "
        "system has produced its final answer. This agent reviews the answer "
        "against the original query and produces a structured quality evaluation."
    ),
    instruction=(
        "You are a strict but fair quality reviewer for travel-system answers.\n\n"
        "The travel answer to evaluate is in session state under the key "
        "'travel_answer'. You can reference it as {travel_answer}.\n\n"
        "Your job:\n"
        "1. Read the travel answer carefully: {travel_answer}\n"
        "2. Evaluate it on 4 dimensions (each 1-10):\n"
        "   - completeness: did it address every part of the query?\n"
        "   - factual_grounding: are claims supported by data (not invented)?\n"
        "   - specificity: are numbers, dates, names concrete or vague?\n"
        "   - structure: is the answer well-organized and easy to read?\n"
        "3. Call score_response EXACTLY ONCE with your evaluation.\n"
        "4. After the tool call, present the evaluation to the user as:\n\n"
        "---\n"
        "📊 **Quality Evaluation**\n"
        "- ✅ Completeness: X/10\n"
        "- ✅ Factual Grounding: X/10\n"
        "- ⚠️ Specificity: X/10\n"
        "- ✅ Structure: X/10\n\n"
        "**Overall: X.X/10**\n"
        "**Suggestion:** ...\n\n"
        "Be honest. A perfect 10 is rare. Use the full 1-10 range."
    ),
    tools=[score_response],
)
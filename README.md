# Multi-Agent Travel Intelligence System

A multi-agent AI system built with **Google Agent Development Kit (ADK)** that answers complex travel queries by coordinating specialized agents and tools. Built as a technical assignment for the Mercedes-Benz GenAI / Agentic AI Internship.

---

## Quick Demo

**User query:**
> "I'm traveling from Frankfurt to Tokyo for 5 days. What's the weather and what should I pack?"

**System response:**
> Routes to `weather_agent` → calls `geocode_city` + `get_weather_forecast` → produces a structured forecast with packing recommendations.

**Complex query:**
> "What's the minimum budget for 10 days in Iceland from Germany, including weather and visa info?"

**System response:**
> Coordinator delegates to all three specialists in parallel → aggregates outputs into Overview / Weather / Budget / Destination / Recommendations sections.

---

## Architecture

```
                    User Query
                         ↓
              ┌──────────────────────┐
              │  Travel Coordinator  │   ← decomposes intent, delegates
              │  (LlmAgent)          │
              └──────────┬───────────┘
                         │
        ┌────────────────┼────────────────┐
        ↓                ↓                ↓
  ┌──────────┐    ┌──────────┐     ┌──────────────┐
  │ Weather  │    │ Budget   │     │ Destination  │
  │ Agent    │    │ Agent    │     │ Agent        │
  └────┬─────┘    └────┬─────┘     └──────┬───────┘
       │               │                   │
  ┌────▼──────────┐ ┌──▼─────────────┐ ┌──▼──────────────┐
  │ geocode_city  │ │ daily_budget   │ │ country_info    │
  │ get_forecast  │ │ exchange_rate  │ │ wikipedia       │
  │ (Open-Meteo)  │ │ web_search     │ │ web_search      │
  └───────────────┘ └────────────────┘ └─────────────────┘
                         │
                         ↓
              Structured Final Answer
              (Overview / Weather / Budget /
               Destination / Recommendations)
```

A **coordinator agent** decomposes the user query and delegates to three **specialist agents**, each owning a focused set of tools. The coordinator then aggregates outputs into a structured final answer.

---

## Why Multi-Agent?

A single LLM agent with all 8 tools suffers from well-known failure modes as the toolset grows:

| Problem with single agent | How multi-agent solves it |
|---|---|
| Tool-selection accuracy drops past ~5 tools | Each specialist sees only 2-3 focused tools |
| Prompt context bloats with mixed instructions | Each agent has a focused, domain-specific prompt |
| Hard to debug — which capability failed? | Specialists are independently testable |
| Adding capability = rewriting one giant prompt | Adding capability = adding a new agent |

**This is the core architectural insight of the project.** The travel domain is just the demo — the same pattern maps to any domain where multiple specialists collaborate (marketing campaigns, customer support, code review, etc.).

---

## Tech Stack

| Layer | Choice | Why |
|---|---|---|
| Agent framework | Google ADK | Mentioned in JD; native `sub_agents` delegation; built-in trace UI |
| LLM | Gemini 2.5 Flash | Free tier; fast; good tool-call accuracy; current Google recommendation |
| Pipeline pattern | `SequentialAgent` | Forces evaluator step (when enabled); deterministic control flow |
| Weather data | Open-Meteo API | Free, no key needed, reliable European data |
| Exchange rates | Frankfurter (ECB) | Free, no key, official European rates |
| Country info | REST Countries | Free, open dataset |
| Encyclopedia | Wikipedia REST | Free, open access |
| Web search | DuckDuckGo (`duckduckgo-search`) | Free, no key, privacy-friendly |

---

## Setup

```bash
# Clone and set up Python environment
python -m venv venv

# Windows PowerShell
venv\Scripts\Activate.ps1
# Mac/Linux
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env and add your Google AI Studio API key
# Get a free key at: https://aistudio.google.com/apikey
```

---

## Running the System

### Option 1: ADK Web UI (recommended for demos)

```bash
adk web
```

Open `http://127.0.0.1:8000` in your browser. Select the `agents` app from the top-left dropdown.

The web UI shows **agent traces** — you can see each delegation and tool call as it happens. This is the best view for understanding what the system is doing.

### Option 2: CLI

```bash
python run_cli.py
```

Type queries, get responses. Useful as a fallback if the web UI has issues.

---

## Example Queries to Try

- *"What's the weather in Tokyo for 3 days?"* — simple, single-specialist
- *"What's the minimum budget for a 5-day trip from Frankfurt to Tokyo?"* — multi-specialist
- *"I'm planning a Japan trip. Tell me weather, costs, visa, and what to pack."* — full orchestration
- *"How does the Yen exchange against the Euro right now?"* — tool-only path
- *"What's the cheapest country in Europe to visit for a week?"* — open-ended web-search path

---

## Project Structure

```
travel-intelligence-system/
├── agents/                        # Agent definitions
│   ├── __init__.py                # Exposes root_agent for ADK discovery
│   ├── coordinator.py             # Top-level orchestrator
│   ├── weather_agent.py           # Weather specialist
│   ├── budget_agent.py            # Budget/cost specialist
│   ├── destination_agent.py       # Visa/culture/info specialist
│   └── evaluator_agent.py         # (Work-in-progress) LLM-as-judge quality reviewer
│
├── tools/                         # Standalone tool functions
│   ├── __init__.py
│   ├── weather_tools.py           # Open-Meteo geocoding + forecast
│   ├── budget_tools.py            # Exchange rates + daily budget estimates
│   ├── destination_tools.py       # REST Countries + Wikipedia
│   ├── search_tools.py            # DuckDuckGo web search
│   └── evaluation_tools.py        # (WIP) score_response for evaluator agent
│
├── tests/
│   └── test_tools.py              # Smoke tests for all tools
│
├── main.py                        # ADK entry point
├── run_cli.py                     # Command-line runner (demo fallback)
├── requirements.txt
├── .env.example                   # Template — copy to .env and add key
├── .gitignore
├── README.md                      # This file
└── DECISIONS.md                   # Architectural decisions and trade-offs
```

---

## Key Design Choices (Short Version)

The full reasoning is in [DECISIONS.md](DECISIONS.md). Highlights:

1. **Coordinator + Specialists pattern** — not a single agent with all tools.
2. **Tools split for reusability** — e.g. `geocode_city` and `get_weather_forecast` are separate so geocoding can be reused by future agents.
3. **No paid APIs** — every tool runs on a free service with no credit card. The repo is fully runnable by anyone.
4. **Hardcoded daily-cost table + web search** — for flight/hotel pricing. Production replacement: Amadeus Self-Service API (documented in DECISIONS.md).
5. **Deliberately omitted: RAG, memory, streaming, auth** — out of scope for a prototype focused on demonstrating orchestration.

---

## How a Query Flows Through the System

Example: *"What's the weather in Tokyo for 3 days?"*

1. **Coordinator** receives the query, identifies that `weather_agent` is needed, delegates.
2. **Weather agent** reads the query, plans to call `geocode_city` first.
3. `geocode_city("Tokyo")` returns `{latitude: 35.68, longitude: 139.65}`.
4. Weather agent now calls `get_weather_forecast(lat, lon, days=3)`.
5. Returns 3 days of max/min temps + precipitation.
6. Weather agent writes a human-readable summary + packing tips.
7. Control returns to the **coordinator**.
8. Coordinator formats the final answer with Overview / Weather / Recommendations sections.

In the ADK web UI, all 8 steps are visible in the Events panel. **Observability is built in** — one of the reasons ADK was chosen over rolling custom orchestration.

---

## Mistakes Made and Lessons Learned

Documented in detail in [DECISIONS.md](DECISIONS.md). Short list:

- ❌ Used deprecated `gemini-2.0-flash` initially → 502 errors → switched to `gemini-2.5-flash`
- ❌ Hit free-tier rate limit (20 calls/day) during testing → planned LiteLLM + Ollama fallback
- ❌ `pkg_resources` missing on Python 3.12 → fixed with `pip install setuptools`
- ❌ Initial coordinator didn't call the evaluator reliably → migrated to `SequentialAgent` pattern

These weren't blockers — they were the project. Documenting them is part of the engineering story.

---

## Roadmap

### Tier 1 — Immediate next additions
- [ ] Stabilize the **evaluator agent** (LLM-as-judge for quality scoring)
- [ ] **Caching layer** for repeated tool calls (weather, exchange rates)
- [ ] **Evaluation harness** with 10 reference queries scored in CI

### Tier 2 — Production-readiness
- [ ] **FastAPI** backend with `/chat`, `/health`, `/eval` endpoints
- [ ] **React frontend** with chat UI and trace visualization
- [ ] **Dockerfile + docker-compose**
- [ ] **GitHub Actions CI** running pytest on every push
- [ ] **Structured logging** of every LLM call (latency, tokens, cost)

### Tier 3 — Domain extensions
- [ ] Replace hardcoded budget with **Amadeus Self-Service API** (flight + hotel)
- [ ] Add **RAG layer** with ChromaDB for grounded destination knowledge
- [ ] **Domain pivot demo**: swap travel specialists for marketing specialists (campaign coordinator → copy / asset / translation / brand-compliance agents)

The Tier 3 marketing pivot is particularly relevant to Mercedes-Benz Cars Communications use cases. The orchestration pattern is the asset; the domain is replaceable.

---

## What This Project Demonstrates

| Skill | Where it shows up |
|---|---|
| **Agentic AI design** | Coordinator + specialist pattern |
| **LLM orchestration** | Multi-step delegation with `sub_agents` |
| **Prompt engineering** | Iterative agent instructions; documented in DECISIONS.md |
| **Tool design** | Function docstrings as LLM-facing prompts |
| **API integration** | 5 different free APIs wired into tools |
| **System design judgment** | Deliberate trade-offs documented |
| **Debugging discipline** | Failures documented with root causes |
| **Engineering communication** | This README + DECISIONS.md |

---

## License

MIT. Built as a technical assignment; freely reusable.

## Contact

**Dhruvin Bharatkumar Padsala**
M.Sc. Global Software Development — Hochschule Fulda
[padsaladhruvin0401@gmail.com](mailto:padsaladhruvin0401@gmail.com) 
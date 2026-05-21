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

- ❌ Used deprecated `gemini-2.5-flash` initially → 502 errors → switched to `gemini-flash-latest`
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
[padsaladhruvin0401@gmail.com](mailto:padsaladhruvin0401@gmail.com) · [LinkedIn](https://www.linkedin.com/in/dhruvin-padsala-927212222/)
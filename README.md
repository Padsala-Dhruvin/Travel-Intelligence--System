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
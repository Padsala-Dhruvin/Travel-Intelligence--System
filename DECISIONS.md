# Design Decisions and Trade-Offs

This document captures the architectural choices made during this project, the alternatives I considered, and what I'd do differently with more time. It's written as a record of **engineering judgment under constraints** — not just "what I built" but "why this and not that."

---

## 1. Framework: Google ADK

**Chose:** Google Agent Development Kit (ADK).

**Considered:**
- LangGraph — more flexible, larger community, but more boilerplate
- CrewAI — simpler API, less aligned with Google ecosystem
- Raw Gemini API + custom orchestration — full control but reinventing the wheel

**Why ADK:**
- The job description explicitly listed Google ADK as a strong plus.
- Native `sub_agents` delegation matched the multi-agent requirement out of the box.
- Built-in web UI with visual event traces — invaluable for debugging and demoing.
- Designed for Gemini, so model integration is one line of code.

**Trade-off:**
ADK has a smaller community than LangGraph. Fewer Stack Overflow answers when stuck. I mitigated this by reading the official docs and sample repos directly rather than searching for shortcuts.

---

## 2. Agent Topology: Coordinator + Specialists

**Chose:** One coordinator delegating to three specialist agents.

**Considered:**
- Single agent with all 8 tools
- Peer-to-peer agent collaboration (agents call each other directly)
- Strict pipeline (each query goes through every specialist regardless of relevance)

**Why coordinator + specialists:**

| Problem | How this topology solves it |
|---|---|
| Tool-selection accuracy degrades past ~5 tools in one agent | Each specialist sees only 2-3 tools |
| One bloated prompt diluting focus | Each agent has a focused, domain-specific prompt |
| Hard to test which capability failed | Specialists are independently testable in isolation |
| Adding new capabilities means rewriting the whole prompt | New capability = new specialist; existing agents unchanged |

**Trade-off:**
Two LLM hops per query (coordinator → specialist) add latency vs. a single agent. Acceptable for a non-real-time use case. In production I'd parallelize independent specialists.

---

## 3. Tool Granularity

**Chose:** Separate `geocode_city` and `get_weather_forecast` tools (and similar splits elsewhere).

**Considered:** A single combined `get_weather_by_city(city, days)` tool that hides the geocoding internally.

**Why split:**
- **Reusability** — geocoding is useful for any agent that takes a city name (a future hotel-finder, restaurant-recommender, etc.).
- **Observability** — when something fails, I can see which step broke. With a combined tool, the failure mode is opaque.
- **Agent reasoning** — splitting tools forces the LLM to *plan* ("first geocode, then forecast"). That visible planning is exactly what agentic AI is about.

**Trade-off:**
One extra tool call per weather request, slightly more LLM tokens. Negligible in practice.

---

## 4. Cost Estimates: Hardcoded Lookup + Web Search (with Production Path)

**Chose:** Small lookup table for daily costs + web search for flight estimates + Frankfurter API for live exchange rates.

**Considered:**
- **Amadeus Self-Service API** — genuinely free tier (1,000–10,000 calls/month, no credit card), OAuth2 REST, 400+ airlines, 150,000+ hotels. The clear production winner.
- **Skyscanner / Kiwi.com APIs** — paid only.
- **Web scraping (Booking.com / Google Flights)** — Terms-of-Service risky, fragile.

**Why this approach for the prototype:**
- Amadeus requires OAuth2 + token refresh — adds setup complexity that distracts from the orchestration demo.
- Amadeus test environment uses *copied* inventory data, not live market rates. Realistic but not live, so the wow-factor over my approach is limited.
- My hybrid approach is **transparent**: the agent says "this is an estimate" and grounds with current web search results. No silent hallucination.

**Production migration path (well-defined, contained to one file):**
1. Replace `estimate_daily_budget` and the web-search-based flight grounding in `tools/budget_tools.py`.
2. Add OAuth2 token-refresh wrapper.
3. Function signature stays identical → no changes to the agent layer.
4. Estimated effort: 1 day.

**Why I'm explicit about this:**
Most demos quietly hide their data sources. I'd rather show the gap and the documented migration plan than pretend it's already solved.

---

## 5. Coordinator Never Answers Directly

**Chose:** The coordinator always delegates to a specialist, even for queries it could conceivably answer itself.

**Considered:** Letting the coordinator answer simple questions directly to save an LLM hop.

**Why strict delegation:**
- Once the coordinator starts answering directly, it becomes a generalist — defeating the entire reason for specialists.
- Predictable behavior is more valuable than micro-optimization at this scope.
- Easier to extend: a future "memory agent" or "logging agent" plugs in cleanly when the coordinator's job is *only* routing.

**Trade-off:**
Slight overhead for trivial queries. Worth it for system clarity.

---

## 6. Pipeline: `SequentialAgent` for Evaluator Workflow

**Chose:** Wrap coordinator + evaluator in a `SequentialAgent` (when the evaluator is enabled).

**Considered:** Letting the coordinator decide whether to call the evaluator as a final sub-agent.

**Why a deterministic pipeline:**
In my first attempt, the evaluator was a sub-agent of the coordinator. The coordinator considered itself "done" after producing the travel answer and silently skipped evaluation. No amount of prompt tweaking made it reliable.

**The insight:**
LLMs are great at content generation, unreliable at "remembering to do mandatory steps." For anything that must run on every query — quality checks, audit logs, compliance — you use deterministic control flow, not LLM discretion. This is the same principle as CI/CD quality gates in software engineering.

**Status:**
The evaluator agent and `SequentialAgent` wrapper are implemented but had stability issues at the time of the demo. Logged for stabilization in the next iteration.

**Note on ADK deprecation:**
ADK is migrating `SequentialAgent` to a new graph-based `Workflow` primitive (with edges, nodes, concurrency control). I inspected the new API and confirmed it's *not* a drop-in replacement — it's a structural redesign. I logged it as a TODO and stayed on the stable API. In production I'd pin the ADK version and migrate during a maintenance window after the new Workflow API stabilizes.

---

## 7. Model Choice: Gemini 2.5 Flash

**Chose:** `gemini-2.5-flash` (with `gemini-2.5-flash-lite` for cost-sensitive agents).

**Considered:**
- `gemini-2.0-flash` — initially used, but deprecated for new projects (March 2026).
- `gemini-2.5-pro` — better reasoning but slow and expensive for a multi-agent demo.
- Local model via Ollama (e.g. Llama 3.1 8B, Qwen 2.5 7B) — planned as fallback.

**Why Gemini 2.5 Flash:**
- Free tier sufficient for a prototype.
- Sub-second responses keep the demo lively.
- Strong tool-call accuracy in my testing.
- Google's documented successor to deprecated 2.0 Flash.

**Trade-off:**
Free tier limits to 20 requests/day per model. Each user query fans out into 5-10 LLM calls due to delegation, so demo queries consume the quota fast. Documented as a known constraint; mitigation is Ollama-based local inference (LiteLLM wrapper allows one-line swap).

---

## 8. What I Deliberately Did *Not* Build

This is as important as what I did build. Each omission is a deliberate scope decision.

- **Conversation memory** — example queries are single-turn; adding memory would have added complexity without showcasing new capabilities for this assignment.
- **RAG / vector database** — no large knowledge base in scope. Web search covers freshness needs. RAG would be over-engineering here, but is the obvious next step if a real knowledge base existed.
- **Streaming responses** — final-answer-only is clearer for the demo. Streaming is a UX add-on, not architectural.
- **Authentication and rate limiting** — out of scope for a prototype.
- **Real flight/hotel APIs (Amadeus)** — see §4 above. Documented migration path.
- **Production frontend (React / FastAPI)** — the ADK web UI is sufficient for the demo. Production frontend is on the roadmap.

The principle: **every feature I added had to earn its place by strengthening the core architectural story.** Features that just sound impressive without contributing were left out.

---

## 9. Mistakes Made and Root Causes

Documented honestly, because debugging stories are part of the engineering record.

### 9.1 Deprecated model name (gemini-2.0-flash → 502 errors)
**Root cause:** I used a model name from older tutorials. Google deprecated `gemini-2.5-flash` for new projects as of March 2026.
**Fix:** Switched to `gemini-flash-letest` (the documented replacement).
**Lesson:** LLM infrastructure has a faster deprecation cycle than traditional software. Pin model versions explicitly; subscribe to provider deprecation announcements.

### 9.2 Missing `pkg_resources` on Python 3.12
**Root cause:** Python 3.12 stopped bundling `setuptools` in fresh virtual environments. ADK's OpenTelemetry dependency relies on `pkg_resources`.
**Fix:** `pip install setuptools`.
**Lesson:** Read the import chain in tracebacks before searching online. The actual error message contained the answer.

### 9.3 ADK couldn't find `root_agent`
**Root cause:** ADK expects `root_agent` to be exposed at the package level (`agents/__init__.py`), but I defined it in `coordinator.py`.
**Fix:** Added `from agents.coordinator import root_agent` to `agents/__init__.py`.
**Lesson:** Frameworks have discovery conventions. The error message listed the exact paths ADK had searched — reading it carefully saved hours.

### 9.4 Free-tier rate limit (20 requests/day)
**Root cause:** Each user query fans out into 5-10 LLM calls due to agent delegation. Free tier exhausts after 2-4 demo runs.
**Fixes (three timeframes):**
- Short-term: switched to `gemini-2.5-flash-lite` (separate quota bucket).
- Medium-term: planned Ollama integration via LiteLLM for unlimited local inference.
- Long-term: abstracted model provider so swapping between Gemini, Claude, and local models is a one-line config change.
**Lesson:** In agentic systems, one user query becomes many LLM calls. Capacity planning matters from day one.

### 9.5 Evaluator agent didn't fire reliably
**Root cause:** Coordinator considered itself "done" after Phase 1 and skipped the evaluator delegation, even with explicit instructions to always evaluate.
**Insight:** Multi-step delegation is unreliable when controlled by an LLM's judgment.
**Fix in progress:** Migrate to `SequentialAgent` so the evaluator runs by pipeline structure, not LLM choice.
**Lesson:** Use deterministic control flow for anything that must happen (quality gates, audit logs). Reserve LLM judgment for content generation.

---

## 10. What I'd Do Differently With More Time

Ranked by impact:

1. **Set up an evaluation harness on day one.** Without measurements, "the system works" is a feeling, not a fact. 10 reference queries + LLM-as-judge would have made every later decision easier.

2. **Stabilize the evaluator agent.** It was the most interesting addition — automated quality scoring is the unsolved problem in agentic AI. Worth getting right.

3. **Add a caching layer.** Weather queries for Tokyo at 3 PM and 3:01 PM are identical. Caching cuts cost and latency 10x for repeated tool calls.

4. **Parallelize specialists.** When the coordinator needs both weather and budget, those specialists could run in parallel. ADK supports it; I sequenced for simplicity.

5. **Replace the hardcoded budget table with Amadeus.** §4 covers the plan.

6. **Build the FastAPI + React layer.** Turns the prototype into something deployable. Also signals full-stack capability — relevant for multiple roles.

7. **Domain pivot demo.** Build a second set of specialists for a marketing-campaign use case to demonstrate that the architecture transfers. Most directly relevant to Mercedes-Benz Cars Communications.

---

## 11. How This Maps to Mercedes-Benz Cars Communications

The job description mentions "intelligent assistants, automated campaign optimization, and content generation." The travel coordinator I built maps to a **campaign coordinator** with the same architecture:

| This project | Mercedes marketing equivalent |
|---|---|
| Travel coordinator | Campaign coordinator |
| Weather agent | Copy agent (headlines, body text) |
| Budget agent | Asset agent (image / video selection) |
| Destination agent | Translation agent + brand-compliance agent |
| Final structured answer | Approved campaign artifact |

**The orchestration pattern is the deliverable, not the travel domain.** Swapping in marketing-flavored specialists would take one-to-two days. The agent framework, tool design, evaluation pattern, and pipeline structure all transfer unchanged.

---

## 12. Closing Note

I've tried to be honest in this document about what worked, what didn't, and what I left out on purpose. The point isn't to claim the system is finished — it's to show how I make engineering decisions when scope, time, and quality are in tension.

For me, the most interesting thing wasn't getting the agents to talk to each other (ADK handles that elegantly). It was learning that **the hardest problems in agentic AI aren't getting outputs — they're knowing whether the outputs are good, and making sure mandatory steps actually run.** Both of those drove the evaluator and `SequentialAgent` work, and both will keep being interesting problems in this space for years.

## Contact

**Dhruvin Bharatkumar Padsala**
M.Sc. Global Software Development — Hochschule Fulda
[padsaladhruvin0401@gmail.com](mailto:padsaladhruvin0401@gmail.com) · [LinkedIn](https://www.linkedin.com/in/dhruvin-padsala-927212222/)
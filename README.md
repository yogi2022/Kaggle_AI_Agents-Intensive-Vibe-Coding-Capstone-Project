# Berean — A Biblical Life Concierge

> Examine everything. Be transformed.

Berean is a multi-agent **biblical life concierge** for the Kaggle *AI Agents: Intensive
Vibe Coding Capstone* (Concierge Agents track). Tell it what you're carrying — anxiety,
a lost sense of purpose, a hard decision — and it diagnoses the root issue, engages the
relevant biblical specialists, and returns one Scripture-grounded transformation plan:
diagnosis, cited Scripture, a character study, practical steps, a 7-day plan, a prayer,
and reflection questions.

## The problem
People are anxious, lost, and disconnected. Existing Bible apps mostly *answer questions*
— and worse, a naive Bible chatbot will **misquote or invent verses**, which is both
useless and dangerous. Berean is a *transformation engine*, not an information engine, and
it is built so it physically cannot speak Scripture from the model's memory.

## Why agents
A single chatbot can't do this well. Berean needs to (1) separate symptom from root cause,
(2) reason across several life domains at once, and (3) merge those into one coherent plan.
That is a multi-agent job: a triage agent, a council of specialists, and a synthesizer.

## The key idea: grounded, not generative
Every verse comes from a custom **Scripture MCP server** backed by a public-domain corpus
(KJV seed). Agents are forbidden to quote anything the server didn't return. This makes
Berean trustworthy *and* gives a measurable headline metric — **citation faithfulness**
(verified references ÷ cited references). In our eval a grounded reply scores 100% and a
reply with fabricated references is correctly flagged at 0%.

## Architecture

```
User / web app (Cloud Run)
        │
        ▼
Orchestrator  ──►  Triage & diagnosis ──► Specialist council (parallel) ──► Plan synthesizer
   (ADK)              (root cause)         identity · peace · purpose ·         (unified plan)
        ▲                                  decision  (each self-skips)
        │                                        │
        └──────────────── grounded by ──────────┴──►  Scripture MCP server ──► Bible corpus
                                                       (tools, not memory)      (KJV · TSK · Strong's)

Cross-cutting: Skills (SKILL.md) · Life Graph memory + Kingdom Health Score ·
               Guardrails (crisis + citation) · Cloud Trace observability
```

The orchestrator is an ADK `SequentialAgent`; the specialist council is a `ParallelAgent`
whose members self-skip with `N/A` when their domain isn't in the diagnosis — effective
routing with parallel execution. The synthesizer emits a structured `UnifiedPlan` (JSON).

## Course concepts demonstrated (6 of 6)

| Concept | Where | File(s) |
| --- | --- | --- |
| Multi-agent system (ADK 2.x) | orchestrator → triage → parallel specialists → synthesizer | `berean_agents/*` |
| MCP server | custom Scripture MCP server (6 tools) consumed via ADK `MCPToolset` | `mcp_scripture/server.py`, `berean_agents/mcp_toolset.py` |
| Agent skills | 4 `SKILL.md` packages (progressive disclosure) | `skills/`, `.agents/skills/` |
| Security features | crisis escalation, PII-safe tool logging, least-privilege tool allow-lists, citation verification, no secrets in code | `berean_agents/guardrails.py` |
| Antigravity | built via vibe coding; `/schedule` runs the daily devotional (see SPEC + video) | video |
| Deployability | Cloud Run + Agent Runtime; Cloud Trace observability | `Dockerfile`, `deploy/` |

## Setup

```bash
python -m venv .venv && . .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env      # add your Google AI Studio key
python -m mcp_scripture.corpus_loader   # build the Scripture corpus
```

## Run

```bash
# 1. Tests + evals (no API key needed — these are deterministic):
python -m mcp_scripture.test_server
python -m evals.citation_faithfulness

# 2. End-to-end CLI (needs GOOGLE_API_KEY):
python run_demo.py "I'm anxious, I feel lost, and I don't know what God wants for me."

# 3. Web app:
uvicorn frontend.app:app --port 8080    # open http://localhost:8080
```

## Evaluation results (deterministic, reproducible)

- **Citation faithfulness** — grounded response: 100%; response with fabricated references: 0% (flagged).
- **Crisis-escalation recall** — 3/3 crisis phrasings escalated; 0/3 false positives on normal distress.
- **Routing** — labeled cases in `evals/routing_cases.json` (composite query engages peace + purpose + identity).

## Security & safety
Spiritual confessions are highly sensitive. Berean minimizes stored data (the Life Graph
keeps only structured scores/short notes, never raw text), offers a delete control
(`DELETE /data`), screens for crisis signals *before* the model and hands off to real-world
help, scopes each agent to a least-privilege MCP tool allow-list, verifies citations, and
keeps all secrets in environment variables. Berean is **not** a substitute for a pastor,
licensed counselor, or medical/mental-health professional.

## Extensibility
The vision spans ~24 domains (Marriage, Finances, Grief, Apologetics, …). Each is a new
specialist that reuses the same MCP grounding, skills, and synthesizer — add an entry to
`SPECIALIST_SPECS` in `berean_agents/specialists.py`. The MVP ships four, done deeply.

## Repository layout
See `SPEC.md` for the full blueprint, two-week plan, video script, and writeup outline.

```
mcp_scripture/   Scripture MCP server + public-domain corpus + tool tests
berean_agents/   ADK orchestrator, triage, specialists, synthesizer, guardrails
skills/          4 SKILL.md agent skills (mirrored into .agents/skills)
memory/          Life Graph + Kingdom Health Score
evals/           citation faithfulness, routing, crisis cases
frontend/        FastAPI app + chat/dashboard UI
deploy/          Cloud Run / Agent Runtime / cleanup
```

## Data & licensing
Seed Scripture text is the public-domain **King James Version**. Cross-references follow
the public-domain Treasury of Scripture Knowledge pattern; lexical entries use public-domain
Strong's data. To scale, load a full public-domain Bible (KJV/WEB). **Do not** include
copyrighted translations (NIV, ESV). Verify each dataset's license before shipping.

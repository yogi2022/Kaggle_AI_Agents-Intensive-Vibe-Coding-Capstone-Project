# Berean — Build Blueprint for the Kaggle AI Agents Capstone

**A biblical life concierge built on the Google agent stack (ADK 2.0, MCP, Skills, Antigravity, Agent Runtime).**

This document is your spec and your project plan. It is written to map directly onto the competition rubric so that every hour you spend also earns points. Deadline: **July 6, 2026, 11:59 PM PT**. You have roughly two weeks.

---

## 1. The decision: track + name

### Track — Concierge Agents (primary)
Your idea is a personal assistant that manages a deeply personal area of someone's life and holds sensitive personal data. That is the literal definition of the Concierge track ("safe and useful personal assistants… managing personal tasks while keeping user data secure"). Choosing Concierge gives you a strategic bonus: the track's "keep user data secure" requirement lets your security work double as both a track requirement *and* a scored rubric concept. Freestyle is a valid backup, but Concierge is the stronger, more defensible fit, and judges may move winners between tracks anyway.

### Name — Berean
In Acts 17:11 the Bereans "examined the Scriptures daily to see whether these things were so." That is exactly what your agent does and exactly the trust problem it solves: an AI that speaks about Scripture must never invent a verse. "Berean" signals rigor, gives you a memorable origin story for the video and writeup, and pairs cleanly with the track as *"Berean — your personal biblical concierge."* (Your own "Kingdom Concierge" also works; Berean is the sharper, more ownable mark.)

> Suggested tagline: **Examine everything. Be transformed.**

---

## 2. The one idea that wins this: grounded, not generative

A Bible agent that paraphrases Scripture from a language model's memory is both unimpressive and dangerous — it will misquote, invent references, and drift doctrinally. **The single most important architectural decision is that Berean never recites Scripture from the model. It retrieves verses through a tool — a custom Scripture MCP server — and is forbidden to quote anything the tool didn't return.**

This one decision simultaneously:
- Solves the credibility problem (every claim is citable and verifiable).
- Demonstrates the **MCP server** course concept in the most meaningful possible way (the MCP server *is* the product's integrity, not a bolt-on).
- Gives you a concrete, measurable **evaluation** metric: *citation faithfulness* — the percentage of responses where every quoted reference actually exists in the corpus and matches the text returned. Judges love a real, defensible eval.
- Embodies the "Berean" name in code.

Lead your video and writeup with this. It is your differentiator.

---

## 3. Scope discipline (read this twice)

Your idea document lists 24 agents and a full "Biblical Life Graph." **Do not build 24 agents.** A capstone is judged on depth, polish, and a working demo — not breadth. Build a tight vertical slice that is genuinely excellent, and show the architecture is built to extend to the other twenty.

**MVP scope (what you actually build):**
- 1 Orchestrator + 1 Triage/diagnosis agent + **4 specialist agents**: Identity, Peace (anxiety), Purpose/Calling, Decision-Making. These four are the most relatable, most demoable, and cover the "I'm anxious, lost, and don't know what God wants" composite query perfectly.
- 1 Plan Synthesizer that merges multiple specialists into one unified plan.
- The Scripture MCP server (the centerpiece).
- 3–4 Skills.
- A lightweight Life Graph (memory) + a simple "Kingdom Health Score."
- Security/guardrails + an eval suite.
- A minimal chat + dashboard frontend, deployed.

**Extensibility story (what you *say*):** "Adding the other 20 domains — Marriage, Finances, Grief, Apologetics, etc. — is adding specialist nodes that reuse the same MCP grounding, skills, and synthesizer. The architecture is designed for it." That sentence turns your scoped MVP into a visionary platform without you building it all.

---

## 4. Course-concept coverage (the rubric scorecard)

You must demonstrate **at least 3** key concepts. Berean cleanly hits **all six** — do that; it is a visible advantage.

| Course concept | Where Berean demonstrates it | Shown in |
| --- | --- | --- |
| Multi-agent system (ADK) | Orchestrator → triage → 4 specialists → synthesizer, built with ADK 2.0 | Code |
| MCP server | Custom Scripture MCP server (get_passage, cross_references, search_by_theme, character_profile, original_language) | Code |
| Agent skills | `exegesis`, `discipleship-plan`, `scripture-citation`, `crisis-safety` SKILL.md packages, scaffolded with Agents CLI | Code + Video |
| Security features | Sensitive-data handling, theological + safety guardrails, crisis escalation (human-in-the-loop), MCP tool allow-listing, no secrets in code | Code + Video |
| Antigravity | Vibe-coding the build, artifacts (implementation plan/walkthrough), `/schedule` for the daily devotional, browser sub-agent | Video |
| Deployability | Frontend on Cloud Run; ADK agent on Agent Runtime; Cloud Trace observability | Video |

---

## 5. Architecture (component by component)

### 5.1 Orchestrator (ADK 2.0)
A root `LlmAgent` whose job is *routing*, not answering. It classifies each message on four axes — emotional state, life domain, spiritual condition, urgency — and decides which specialists to activate. Implement multi-specialist activation with an ADK workflow agent (parallel fan-out to the chosen specialists, then a sequential hand-off to the synthesizer). In ADK 2.0 this is naturally a graph-based workflow.

### 5.2 Triage / diagnosis agent
Separates *symptom* from *root cause* before any specialist runs. "I hate my job" may be identity, burnout, or purpose. This step is what makes Berean feel like a counselor rather than a search box, and it is great demo material.

### 5.3 Specialist agents (×4)
Each is an `LlmAgent` with: a tightly scoped instruction, the Scripture MCP tools, and a fixed output contract (diagnosis → key Scriptures → theology → character study → cross-references → application → action plan → prayer → reflection questions). The fixed contract makes outputs consistent, testable, and easy to render in the UI.

### 5.4 Plan synthesizer
Takes 1–N specialist outputs and merges them into a single, non-repetitive transformation plan with one unified Scripture set, one prayer, and a 7-day action sequence. This is the "transformation engine, not information engine" promise made real.

### 5.5 Scripture MCP server (the centerpiece)
A standalone MCP server exposing these tools:
- `get_passage(reference, translation)` → exact verse text from the corpus.
- `cross_references(reference)` → related passages.
- `search_by_theme(theme)` → semantic/topical retrieval ("anxiety", "identity").
- `character_profile(name)` → structured data on a biblical figure.
- `original_language(reference)` → Strong's numbers / Hebrew–Greek lexicon entries.
- `topical_index(topic)` → topical lookup.

**Data — use public-domain sources only** (this also keeps you copyright-clean for quoting):
- World English Bible (WEB) and/or King James Version (KJV) — public-domain Bible text.
- Treasury of Scripture Knowledge (TSK) — public-domain cross-references.
- Nave's Topical Bible — public-domain topical index.
- Strong's Concordance / Strong's numbers + open Hebrew/Greek lexical datasets (e.g., openscriptures, STEPBible).
- Open, prebuilt Bible datasets exist as JSON/SQLite (e.g., the scrollmapper/bible_databases project on GitHub) — a local SQLite store is more reliable than a live API (no rate limits, deterministic, works offline in your demo). **Verify each source's license yourself before shipping; do not include copyrighted translations such as NIV or ESV.**

The system prompt and the `scripture-citation` skill enforce the rule: *quote only text returned by these tools, always with the reference; if a tool returns nothing, say so — never invent.*

### 5.6 Memory — the Life Graph
A simple per-user store (Firestore in the cloud, or local JSON/SQLite for the demo) tracking domains, struggles, habits, life events, and growth history. Derive a lightweight **Kingdom Health Score** (per-domain percentages) to visualize progress on the dashboard. ADK session state handles within-conversation context; the Life Graph handles longitudinal continuity. Keep the schema small for the MVP.

### 5.7 Cross-cutting: skills, guardrails, observability — see sections 6–8.

---

## 6. Skills (SKILL.md, progressive disclosure, Agents CLI)

Build four skills as directories with a `SKILL.md` (metadata + instructions) plus optional `scripts/` and `references/`. They load only when relevant — the "progressive disclosure" the Day 3 whitepaper describes. Scaffold/manage them with the Agents CLI.

1. **`scripture-citation`** — enforces the only-from-MCP rule and the citation format. The integrity backbone.
2. **`exegesis`** — sound interpretation procedure: context, genre, original audience, cross-reference before application. Loads when a user wants deep study.
3. **`discipleship-plan`** — how to generate a 7/30-day plan (daily Scripture, reflection, prayer, action step, accountability question).
4. **`crisis-safety`** — detects crisis signals (self-harm, abuse, acute medical/mental-health need), switches to a safety protocol, surfaces real-world help, and stops Berean from role-playing a therapist or doctor. This skill is also a security feature.

---

## 7. Security features (Day 4: "Effective Trust")

Concierge track *requires* secure handling of personal data, and security is a scored concept — so invest here.

- **Sensitive data:** spiritual confessions are highly sensitive. Minimize what you store, encrypt at rest, give the user an explicit delete/export control, and never log raw confession text into traces.
- **Theological guardrail:** canonical Scripture only; refuse to fabricate references; cross-check every quoted reference against the MCP corpus before responding.
- **Crisis escalation / human-in-the-loop:** the `crisis-safety` skill routes acute situations to real resources and clear disclaimers (Berean is not a substitute for pastoral care, licensed counseling, or medical/mental-health professionals).
- **Agent hygiene:** least-privilege MCP tool allow-listing (Antigravity project settings let you scope which MCP tools an agent may use), input validation, prompt-injection resistance, ephemeral sandboxing for any code execution, and **no API keys or secrets in the repo** (the rubric explicitly flags this — use env vars / a secrets manager).
- **Observability as security:** OpenTelemetry trajectory traces via Cloud Trace let you audit what the agent did and why.

---

## 8. Evaluation (turn quality into a number)

Define an eval set in ADK and report results in the writeup. Strong, on-theme metrics:
1. **Citation faithfulness** — every quoted reference exists and matches corpus text. Target ~100%; this is your headline number.
2. **Routing accuracy** — orchestrator activates the correct specialist(s) for a labeled set of struggles.
3. **Crisis-escalation recall** — crisis-signal inputs always trigger the safety protocol (a true safety eval).
4. **Trajectory eval** — OpenTelemetry traces confirm the agent followed the intended tool path.

---

## 9. Suggested repository layout

```
berean/
├── README.md                  # problem, solution, architecture, setup, diagrams
├── SPEC.md                    # this blueprint / acceptance criteria
├── .gitignore                 # keep keys + local data out of git
├── orchestrator/              # ADK root + workflow graph
├── agents/
│   ├── triage/
│   ├── identity/
│   ├── peace/
│   ├── purpose/
│   ├── decision/
│   └── synthesizer/
├── mcp_scripture/             # the Scripture MCP server
│   ├── server.py
│   ├── data/                  # public-domain corpus (WEB/KJV, TSK, Strong's)
│   └── tools/                 # get_passage, cross_references, ...
├── skills/
│   ├── scripture-citation/SKILL.md
│   ├── exegesis/SKILL.md
│   ├── discipleship-plan/SKILL.md
│   └── crisis-safety/SKILL.md
├── memory/                    # life-graph store + kingdom health score
├── evals/                     # eval sets + run scripts
├── frontend/                  # chat + dashboard (deploy to Cloud Run)
└── deploy/                    # Agent Runtime descriptors, cleanup scripts
```

---

## 10. Two-week plan (June 21 → July 6)

- **Days 1–2:** Finalize this spec. Scaffold the repo in Antigravity. Build the Scripture MCP server: load the public-domain corpus into SQLite, implement the tools, and *prove grounding works* (a query returns real, exact verses with references).
- **Days 3–5:** Build the ADK orchestrator + triage + the 4 specialists + synthesizer. Wire every agent to the MCP tools. Get the composite query ("anxious, lost, don't know God's will") producing a unified plan.
- **Days 6–7:** Author the 4 skills via Agents CLI. Add the Life Graph memory + Kingdom Health Score.
- **Days 8–9:** Security + guardrails + the eval suite. Make citation-faithfulness measurable and high.
- **Days 10–11:** Frontend (chat + dashboard) in Antigravity; deploy frontend to Cloud Run and the agent to Agent Runtime; turn on Cloud Trace. Set up an Antigravity `/schedule` task for the daily devotional to demo the "daily concierge" feature.
- **Days 12–13:** Record the ≤5-minute video; write the ≤2,500-word writeup; finish README + diagrams; polish.
- **Day 14:** Buffer + submit. Double-check every required asset (below).

---

## 11. Submission checklist (don't lose points on logistics)

- [ ] Kaggle Writeup (**≤2,500 words**), with a **Track selected** (Concierge).
- [ ] Media Gallery with a **cover image** (required) and the video.
- [ ] **YouTube video, ≤5 minutes**, attached to the gallery.
- [ ] **Public project link** — a live demo URL, or a public GitHub repo with detailed setup instructions.
- [ ] `README.md` covering problem, solution, architecture, setup, diagrams.
- [ ] **No API keys or secrets** anywhere in the code.
- [ ] Click **Submit** (a saved draft is not a submission).

---

## 12. Video script (≤5 min)

1. **0:00–0:30 — Hook / problem.** People are anxious, lost, disconnected; existing Bible apps just answer questions. Show the pain.
2. **0:30–1:15 — The idea + why agents.** Berean diagnoses the root issue and routes to biblical specialists who produce a transformation plan — that requires multi-agent reasoning, not a single chatbot.
3. **1:15–1:45 — The trust breakthrough.** Show the Scripture MCP server: Berean retrieves verses through a tool and is forbidden to invent them. Show the citation-faithfulness number.
4. **1:45–2:15 — Architecture.** Display the diagram; narrate orchestrator → triage → specialists → synthesizer, grounded by MCP.
5. **2:15–3:45 — Live demo.** Type the composite struggle; show triage, multi-specialist activation, the unified plan with cited Scripture, the prayer, the 7-day plan, and the dashboard / Kingdom Health Score. Show a crisis input triggering the safety protocol.
6. **3:45–4:30 — The build.** Antigravity vibe-coding, skills, the `/schedule` daily devotional, deployment to Cloud Run + Agent Runtime, Cloud Trace.
7. **4:30–5:00 — Vision + close.** Four domains today, twenty more as drop-in specialists. "Examine everything. Be transformed."

---

## 13. Writeup outline (≤2,500 words)

1. Title + subtitle + track.
2. Problem — why this matters and why it's unsolved.
3. Why agents — what a multi-agent system does that a chatbot can't.
4. Solution overview — the transformation-engine concept.
5. Architecture — the diagram + component walkthrough.
6. The Scripture MCP grounding and citation-faithfulness result.
7. Course concepts demonstrated — the section-4 scorecard.
8. Security, safety, and ethical stance (incl. disclaimers + public-domain text).
9. Evaluation results.
10. The journey — what you tried, what broke, what you learned (judges score this).
11. Vision / extensibility.

---

## 14. Risks & cautions

- **Copyright:** use public-domain translations (WEB/KJV) for the corpus and for any verse you quote. Don't ship NIV/ESV text. Verify every dataset's license.
- **Theological stance:** the product treats Scripture as authoritative *by design* — that's your premise. Frame it respectfully as a tool for people who want biblical guidance, and include clear disclaimers that it doesn't replace pastoral, counseling, or medical care.
- **Safety:** crisis handling is non-negotiable and also scores points.
- **Stack:** the course is entirely Google (ADK 2.0, Antigravity, Agents CLI, Gemini, MCP, Cloud Run, Agent Runtime). Your idea doc mentioned the OpenAI Agents SDK — **switch to ADK** to satisfy the rubric.
- **Scope creep:** four specialists, done well, beats twenty done shallowly.
- **Product facts move fast:** confirm current ADK / Antigravity / Agent Runtime specifics against the official docs as you build (adk.dev, antigravity.google, the codelabs).

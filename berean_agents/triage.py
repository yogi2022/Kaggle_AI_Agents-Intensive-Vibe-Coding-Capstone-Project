"""
triage.py — the diagnosis agent.

Runs first. Reads the user's message, looks up themes in the Scripture corpus to
ground its thinking, and writes a structured Diagnosis to session state under
`diagnosis`. The specialists and synthesizer read that key.
"""

from __future__ import annotations
from google.adk.agents import LlmAgent

from .config import MODEL, PASTORAL_FRAME, GROUNDING_RULE
from .mcp_toolset import build_scripture_toolset
from .guardrails import crisis_guard, pii_safe_tool_logger

TRIAGE_INSTRUCTION = f"""{PASTORAL_FRAME}

You are the TRIAGE & DIAGNOSIS agent. Do not give the full plan. Your job is to find
the ROOT issue beneath the symptom and decide which specialists should engage.

Steps:
1. Read the user's message carefully. Name the presenting problem in one line.
2. Identify the likely root issue (e.g. "I hate my job" may really be identity, purpose,
   burnout, or fear). Be honest and specific.
3. You may call search_by_theme to see how Scripture frames the issue before deciding.
4. Choose the relevant domains from EXACTLY this set: identity, peace, purpose, decision.
   Pick 1-3 that genuinely apply.
5. Set urgency: low | medium | high | crisis.

{GROUNDING_RULE}

Output a compact JSON object on a single block with keys:
presenting_problem, root_issue, domains (array), urgency.
"""

triage_agent = LlmAgent(
    name="triage",
    model=MODEL,
    description="Finds the root issue and selects which biblical specialists to engage.",
    instruction=TRIAGE_INSTRUCTION,
    tools=[build_scripture_toolset(tool_filter=["search_by_theme", "topical_index"])],
    output_key="diagnosis",                 # -> session.state['diagnosis']
    before_model_callback=crisis_guard,      # safety: escalate crises before any model call
    before_tool_callback=pii_safe_tool_logger,
)

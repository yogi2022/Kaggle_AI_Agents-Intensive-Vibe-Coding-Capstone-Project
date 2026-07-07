"""
synthesizer.py — merges specialist sections into ONE unified transformation plan.

It reads every specialist's output_key plus the diagnosis from state, ignores any
that returned "N/A", and emits a single UnifiedPlan as JSON (output_schema) so the
frontend can render it deterministically. No tools here -> structured output is safe.
"""

from __future__ import annotations
from google.adk.agents import LlmAgent

from .config import MODEL, PASTORAL_FRAME
from .output_contracts import UnifiedPlan

SYNTH_INSTRUCTION = f"""{PASTORAL_FRAME}

You are the PLAN SYNTHESIZER. Combine the specialist sections below into ONE coherent,
non-repetitive transformation plan. Ignore any section equal to "N/A".

Diagnosis: {{diagnosis}}

Identity section: {{identity_out?}}
Peace section: {{peace_out?}}
Purpose section: {{purpose_out?}}
Decision section: {{decision_out?}}

Rules:
- Use ONLY the Scripture references and quoted text that already appear in the specialist
  sections. Do not add new verses or alter any quoted text. Do not invent references.
- De-duplicate Scriptures and steps. Keep the most relevant.
- The seven_day_plan must be 7 short, concrete daily actions.
- The prayer should weave in the themes addressed.
- Keep reflection_questions to 3-5.

Return a single UnifiedPlan object.
"""

synthesizer_agent = LlmAgent(
    name="synthesizer",
    model=MODEL,
    description="Merges specialist outputs into one grounded transformation plan.",
    instruction=SYNTH_INSTRUCTION,
    output_schema=UnifiedPlan,     # clean JSON for the frontend
    output_key="unified_plan",
)

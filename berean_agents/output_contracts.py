"""
output_contracts.py — structured output schemas.

The synthesizer emits a UnifiedPlan as JSON (via ADK output_schema) so the frontend
can render it reliably. The triage Diagnosis schema documents the routing contract.
Evals also use these to validate structure.
"""

from __future__ import annotations
from typing import List
from pydantic import BaseModel, Field


class Diagnosis(BaseModel):
    """Triage output: the root issue and which specialist domains to engage."""
    presenting_problem: str = Field(description="What the user said, in one line.")
    root_issue: str = Field(description="The likely deeper cause, not just the symptom.")
    domains: List[str] = Field(
        description="Subset of: identity, peace, purpose, decision.",
    )
    urgency: str = Field(description="low | medium | high | crisis")


class ScriptureCitation(BaseModel):
    reference: str
    text: str


class UnifiedPlan(BaseModel):
    """The merged transformation plan returned to the user."""
    root_cause: str
    biblical_diagnosis: str
    scriptures: List[ScriptureCitation]
    character_study: str
    practical_steps: List[str]
    seven_day_plan: List[str]
    prayer: str
    reflection_questions: List[str]
    disclaimer: str = Field(
        default=(
            "Berean offers biblical guidance and is not a substitute for a pastor, "
            "licensed counselor, or medical/mental-health professional."
        )
    )

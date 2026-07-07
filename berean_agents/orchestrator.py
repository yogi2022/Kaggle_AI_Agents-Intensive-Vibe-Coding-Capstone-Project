"""
orchestrator.py — the root agent.

Pipeline (ADK SequentialAgent):
    triage  ->  specialist_council (ParallelAgent of 4 specialists)  ->  synthesizer

The ParallelAgent runs all four specialists concurrently; each self-skips with "N/A"
when its domain isn't in the diagnosis, so the council behaves like a router while still
showcasing parallel multi-agent execution. The synthesizer merges whatever remains.

`root_agent` is the symbol ADK tooling (adk run / adk web / Agents CLI / Agent Runtime)
looks for.
"""

from __future__ import annotations
from google.adk.agents import SequentialAgent, ParallelAgent

from .triage import triage_agent
from .specialists import ALL_SPECIALISTS
from .synthesizer import synthesizer_agent

specialist_council = ParallelAgent(
    name="specialist_council",
    description="Runs the biblical specialists in parallel; each self-skips if not relevant.",
    sub_agents=ALL_SPECIALISTS,
)

root_agent = SequentialAgent(
    name="berean",
    description=(
        "Berean — a biblical life concierge. Diagnoses the root issue, engages the relevant "
        "biblical specialists, and returns one Scripture-grounded transformation plan."
    ),
    sub_agents=[triage_agent, specialist_council, synthesizer_agent],
)

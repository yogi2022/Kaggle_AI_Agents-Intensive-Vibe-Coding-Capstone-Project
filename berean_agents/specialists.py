"""
specialists.py — the four MVP specialist agents.

Each specialist:
  * reads the triage {diagnosis} from session state,
  * SELF-SKIPS (returns exactly "N/A") if its domain isn't in the diagnosis,
    which turns a ParallelAgent fan-out into effective routing,
  * otherwise produces its section grounded ONLY in Scripture-tool results,
  * writes to its own output_key for the synthesizer to merge.

Adding the other 20 domains from the vision (Marriage, Finances, Grief, Apologetics, ...)
is literally adding more entries to SPECIALIST_SPECS with the same pattern.
"""

from __future__ import annotations
from google.adk.agents import LlmAgent

from .config import MODEL, PASTORAL_FRAME, GROUNDING_RULE
from .mcp_toolset import build_scripture_toolset
from .guardrails import pii_safe_tool_logger

# Lookup-only tool allow-list (least privilege) shared by specialists.
_SPECIALIST_TOOLS = ["get_passage", "search_by_theme", "cross_references",
                     "character_profile", "original_language", "topical_index"]


def _instruction(domain: str, focus: str, anchors: str, figures: str) -> str:
    return f"""{PASTORAL_FRAME}

You are the {domain.upper()} specialist.

ROUTING: The triage diagnosis is: {{diagnosis}}
If "{domain}" is NOT among its domains, reply with exactly: N/A
(Reply with only those three characters and nothing else.)

If "{domain}" IS relevant, focus on: {focus}

Ground your help using the Scripture tools (look up anchor passages such as {anchors},
plus search_by_theme and cross_references). Study a relevant figure
(e.g. {figures}) via character_profile.

{GROUNDING_RULE}

Produce a focused section (not a full plan) with:
- A one-line biblical diagnosis of this dimension.
- 2-4 grounded Scriptures (reference + quoted text from the tool).
- One character study (struggle -> response -> lesson).
- 2-3 practical, doable steps.
Keep it tight; the synthesizer will merge you with other specialists.
"""


SPECIALIST_SPECS = {
    "identity": dict(
        focus="who God says the user is, replacing false/performance-based identity with truth in Christ",
        anchors="Genesis 1:27, Psalm 139:14, Ephesians 1:4, 1 Peter 2:9, 2 Corinthians 5:17",
        figures="Gideon, Moses, Peter",
    ),
    "peace": dict(
        focus="moving from anxiety/fear toward trust and the peace of God",
        anchors="Philippians 4:6-7, Matthew 6:33-34, Isaiah 41:10, John 14:27, 1 Peter 5:7",
        figures="Elijah, David, Joseph",
    ),
    "purpose": dict(
        focus="discovering God-given calling, gifts, and kingdom contribution",
        anchors="Ephesians 2:10, Jeremiah 29:11, Esther 4:14, Romans 8:28",
        figures="Esther, Joseph, Nehemiah",
    ),
    "decision": dict(
        focus="making wise, God-honoring decisions through Scripture, counsel, and prayer",
        anchors="Proverbs 3:5-6, James 1:5, Psalm 119:105, Romans 12:2",
        figures="Nehemiah, Daniel",
    ),
}


def _make(domain: str, spec: dict) -> LlmAgent:
    return LlmAgent(
        name=f"{domain}_specialist",
        model=MODEL,
        description=f"Biblical {domain} specialist (self-skips when not relevant).",
        instruction=_instruction(domain, spec["focus"], spec["anchors"], spec["figures"]),
        tools=[build_scripture_toolset(tool_filter=_SPECIALIST_TOOLS)],
        output_key=f"{domain}_out",
        before_tool_callback=pii_safe_tool_logger,
    )


identity_specialist = _make("identity", SPECIALIST_SPECS["identity"])
peace_specialist = _make("peace", SPECIALIST_SPECS["peace"])
purpose_specialist = _make("purpose", SPECIALIST_SPECS["purpose"])
decision_specialist = _make("decision", SPECIALIST_SPECS["decision"])

ALL_SPECIALISTS = [identity_specialist, peace_specialist, purpose_specialist, decision_specialist]

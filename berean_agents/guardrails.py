"""
guardrails.py — security & safety features as ADK callbacks (Day 4: "Effective Trust").

Implements three guardrails:
  1. crisis_guard (before_model_callback): detects self-harm / abuse / acute medical
     signals and short-circuits the model with a safety response + real-world resources,
     instead of letting Berean role-play a therapist. This is human-in-the-loop triage.
  2. pii_safe_tool_logger (before_tool_callback): logs that a tool ran WITHOUT logging
     raw, sensitive user text — data minimization.
  3. verify_citations (helper, also used by evals): checks that every reference quoted
     in a response actually exists in the Scripture corpus -> citation faithfulness.
"""

from __future__ import annotations
import re
from typing import Optional

from google.adk.agents.callback_context import CallbackContext
from google.adk.models import LlmRequest, LlmResponse
from google.adk.tools import BaseTool
from google.adk.tools.tool_context import ToolContext
from google.genai import types

from mcp_scripture.server import get_passage

# --- 1. Crisis detection ---------------------------------------------------------
_CRISIS_PATTERNS = re.compile(
    r"(kill(?:ing)?\s+myself|suicid\w*|end(?:ing)?\s+my\s+life|want(?:ing)?\s+to\s+die|"
    r"self[- ]?harm|hurt(?:ing)?\s+myself|overdose|abus(?:e|ed|ing)|"
    r"being\s+hit|hitting\s+me|can'?t\s+go\s+on)",
    re.IGNORECASE,
)

_CRISIS_RESPONSE = (
    "I'm really glad you told me, and I want to make sure you're safe. What you're "
    "describing is serious, and it's beyond what I can safely help with as a biblical "
    "guide. Please reach out right now to someone who can help directly:\n\n"
    "- If you are in immediate danger, contact your local emergency number.\n"
    "- Reach a trained person at a local crisis or helpline service in your country.\n"
    "- Tell a trusted person near you — a pastor, family member, or friend — today.\n\n"
    "You matter, and you don't have to carry this alone. When you're safe, I'm here to "
    "walk with you in Scripture, but your safety comes first."
)


def _latest_user_text(llm_request: LlmRequest) -> str:
    for content in reversed(llm_request.contents or []):
        if content.role == "user" and content.parts:
            return " ".join(p.text or "" for p in content.parts)
    return ""


def crisis_guard(callback_context: CallbackContext, llm_request: LlmRequest) -> Optional[LlmResponse]:
    """Before the model runs, short-circuit on crisis signals with a safety response."""
    text = _latest_user_text(llm_request)
    if _CRISIS_PATTERNS.search(text):
        # Mark state so downstream/eval can confirm the escalation fired.
        callback_context.state["crisis_escalated"] = True
        return LlmResponse(
            content=types.Content(role="model", parts=[types.Part(text=_CRISIS_RESPONSE)])
        )
    return None  # no crisis -> let the model proceed normally


# --- 2. Data-minimizing tool logger ---------------------------------------------
def pii_safe_tool_logger(
    tool: BaseTool, args: dict, tool_context: ToolContext
) -> Optional[dict]:
    """Log tool usage without persisting raw sensitive content (data minimization)."""
    safe_args = {k: v for k, v in args.items() if k in ("reference", "theme", "topic", "name", "translation")}
    print(f"[audit] tool={tool.name} args={safe_args}")  # goes to traces, not raw confession text
    return None  # returning None -> proceed with the actual tool call


# --- 3. Citation faithfulness check ---------------------------------------------
_REF_IN_TEXT = re.compile(
    r"\b((?:[1-3]\s)?[A-Z][a-z]+(?:\s[A-Z][a-z]+)?\s\d+:\d+(?:-\d+)?)\b"
)


def find_references(text: str) -> list[str]:
    """Extract scripture-style references from a block of text."""
    return list(dict.fromkeys(_REF_IN_TEXT.findall(text or "")))


def verify_citations(text: str) -> dict:
    """Return citation-faithfulness stats for a response: which cited refs exist in corpus."""
    refs = find_references(text)
    verified, unverified = [], []
    for ref in refs:
        if get_passage(ref).get("found"):
            verified.append(ref)
        else:
            unverified.append(ref)
    total = len(refs)
    return {
        "total": total,
        "verified": verified,
        "unverified": unverified,
        "faithfulness": (len(verified) / total) if total else 1.0,
    }

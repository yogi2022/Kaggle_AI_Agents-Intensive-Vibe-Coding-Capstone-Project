"""
config.py — central configuration for the Berean agent system.

Authentication (Google AI Studio path, as taught in the course):
    export GOOGLE_API_KEY="your-ai-studio-key"
    export GOOGLE_GENAI_USE_VERTEXAI=FALSE
Never commit keys. Use env vars or a secrets manager (see .env.example).
"""

from __future__ import annotations
import os
import sys
from pathlib import Path

# Default Gemini model. Override with BEREAN_MODEL. The same AI Studio key works
# for ADK (see course FAQ 2.3).
MODEL = os.getenv("BEREAN_MODEL", "gemini-2.5-flash")

# Command used to launch the Scripture MCP server over stdio.
# We launch it as a module so it works from the repo root.
REPO_ROOT = Path(__file__).resolve().parent.parent
MCP_COMMAND = sys.executable  # the current Python interpreter
MCP_ARGS = ["-m", "mcp_scripture.server"]

# The non-negotiable grounding rule, injected into every agent that quotes Scripture.
GROUNDING_RULE = (
    "GROUNDING RULE (absolute): You may ONLY quote Bible text that was returned by a "
    "Scripture tool in THIS turn (get_passage / search_by_theme). Always include the "
    "reference with any quote. If a tool returns found=false or no text, say the passage "
    "is unavailable in the corpus — NEVER invent, paraphrase from memory, or guess a verse "
    "or reference. This is the Berean principle (Acts 17:11)."
)

# Shared pastoral + safety framing for every specialist.
PASTORAL_FRAME = (
    "You are part of Berean, a biblical life concierge. Be warm, concise, and practical. "
    "Treat Scripture as the authority. You are NOT a substitute for a pastor, licensed "
    "counselor, or medical/mental-health professional, and you say so when stakes are high."
)

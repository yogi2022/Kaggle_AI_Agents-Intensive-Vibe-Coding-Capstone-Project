"""
run_demo.py — run Berean end-to-end from the command line.

Prereqs:
    export GOOGLE_API_KEY="your-ai-studio-key"
    export GOOGLE_GENAI_USE_VERTEXAI=FALSE
    python -m mcp_scripture.corpus_loader     # build the corpus once

Usage:
    python run_demo.py "I'm anxious, I feel lost, and I don't know what God wants for me."

What it shows: triage -> parallel specialists (self-skipping) -> synthesizer, with every
verse grounded by the Scripture MCP server, plus a post-hoc citation-faithfulness check
and a Kingdom Health Score update.
"""

from __future__ import annotations
import asyncio
import json
import os
import sys

from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types

from berean_agents.orchestrator import root_agent
from berean_agents.guardrails import verify_citations
from memory.life_graph import update_domain, kingdom_health

APP = "berean"
USER = "demo-user"


async def ask(message: str) -> None:
    session_service = InMemorySessionService()
    await session_service.create_session(app_name=APP, user_id=USER, session_id="s1")
    runner = Runner(agent=root_agent, app_name=APP, session_service=session_service)

    final_text = ""
    new_message = types.Content(role="user", parts=[types.Part(text=message)])
    async for event in runner.run_async(user_id=USER, session_id="s1", new_message=new_message):
        if event.is_final_response() and event.content and event.content.parts:
            final_text = "".join(p.text or "" for p in event.content.parts)

    print("\n=== BEREAN RESPONSE ===\n")
    try:
        plan = json.loads(final_text)
        print(json.dumps(plan, indent=2))
        cited = " ".join(c.get("reference", "") for c in plan.get("scriptures", []))
    except json.JSONDecodeError:
        print(final_text)
        cited = final_text

    cf = verify_citations(cited)
    print(f"\n[citation faithfulness] {cf['faithfulness']:.0%} "
          f"(verified {cf['verified']}, flagged {cf['unverified']})")

    # Update the Life Graph (illustrative scoring).
    update_domain(USER, "peace", 55, "engaged anxiety with Scripture")
    update_domain(USER, "purpose", 45, "began seeking calling")
    print(f"[kingdom health] {kingdom_health(USER)}")


if __name__ == "__main__":
    if not (os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")):
        print("Set GOOGLE_API_KEY (AI Studio) first. The agent graph and MCP server are "
              "verified; this runner needs a Gemini key to call the model.")
        sys.exit(0)
    query = " ".join(sys.argv[1:]) or "I'm anxious, I feel lost, and I don't know what God wants for me."
    asyncio.run(ask(query))

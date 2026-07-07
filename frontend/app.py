"""
app.py — FastAPI backend for Berean (deploy target: Cloud Run).

Endpoints:
    GET  /            -> chat + dashboard UI
    POST /chat        -> {message, user_id} -> runs the ADK pipeline, returns the plan
    GET  /dashboard   -> Kingdom Health Score for a user
    DELETE /data      -> erase a user's stored data (data-rights control)
    GET  /health      -> liveness probe

Run locally:
    uvicorn frontend.app:app --reload --port 8080
"""

from __future__ import annotations
import json
import os
from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types

from berean_agents.orchestrator import root_agent
from berean_agents.guardrails import verify_citations
from memory.life_graph import update_domain, kingdom_health, erase

app = FastAPI(title="Berean — Biblical Life Concierge")
STATIC = Path(__file__).parent / "static"
app.mount("/static", StaticFiles(directory=str(STATIC)), name="static")

_session_service = InMemorySessionService()
_runner = Runner(agent=root_agent, app_name="berean", session_service=_session_service)


class ChatIn(BaseModel):
    message: str
    user_id: str = "web-user"


@app.get("/", response_class=HTMLResponse)
def index() -> str:
    return (STATIC / "index.html").read_text()


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


@app.post("/chat")
async def chat(body: ChatIn) -> JSONResponse:
    if not (os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")):
        return JSONResponse({"error": "Server missing GOOGLE_API_KEY."}, status_code=503)

    sid = f"sess-{body.user_id}"
    await _session_service.create_session(app_name="berean", user_id=body.user_id, session_id=sid)
    msg = types.Content(role="user", parts=[types.Part(text=body.message)])

    final_text = ""
    async for event in _runner.run_async(user_id=body.user_id, session_id=sid, new_message=msg):
        if event.is_final_response() and event.content and event.content.parts:
            final_text = "".join(p.text or "" for p in event.content.parts)

    try:
        plan = json.loads(final_text)
        cited = " ".join(c.get("reference", "") for c in plan.get("scriptures", []))
    except json.JSONDecodeError:
        plan = {"raw": final_text}
        cited = final_text

    cf = verify_citations(cited)
    # Illustrative Life Graph update.
    update_domain(body.user_id, "peace", 55, "engaged via web")
    return JSONResponse({"plan": plan, "citation_faithfulness": cf,
                         "kingdom_health": kingdom_health(body.user_id)})


@app.get("/dashboard")
def dashboard(user_id: str = "web-user") -> dict:
    return kingdom_health(user_id)


@app.delete("/data")
def delete_data(user_id: str = "web-user") -> dict:
    erase(user_id)
    return {"erased": user_id}

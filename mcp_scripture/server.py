"""
server.py — Berean Scripture MCP Server
=======================================
The integrity core of Berean. Every verse the agents quote comes from THIS server,
never from the language model's memory. If a tool returns nothing, the agents are
instructed to say so rather than invent a reference. That is the "Berean" principle
(Acts 17:11) implemented in code, and it is what makes citation-faithfulness measurable.

Exposed MCP tools:
  - get_passage(reference, translation)   -> exact verse text
  - cross_references(reference)            -> related passages (TSK-style)
  - search_by_theme(theme)                 -> topical retrieval
  - character_profile(name)                -> structured biblical character study
  - original_language(reference)           -> Strong's / lexical entries
  - topical_index(topic)                   -> verse references for a life theme

Run locally (stdio transport, which ADK's MCPToolset launches automatically):
    python -m mcp_scripture.server
"""

from __future__ import annotations
import json
from typing import Any

from mcp.server.fastmcp import FastMCP

from .corpus_loader import ensure_corpus, parse_reference, _connect

mcp = FastMCP("berean-scripture")
_DB = ensure_corpus()


def _rows(query: str, params: tuple = ()) -> list[dict[str, Any]]:
    conn = _connect(_DB)
    try:
        return [dict(r) for r in conn.execute(query, params).fetchall()]
    finally:
        conn.close()


@mcp.tool()
def get_passage(reference: str, translation: str = "KJV") -> dict:
    """Return the exact text of a Bible passage from the public-domain corpus.

    Args:
        reference: e.g. "Philippians 4:6" or "Philippians 4:6-7".
        translation: translation code (default "KJV").

    Returns a dict with `found`, `translation`, and a list of `verses`
    ({reference, text}). If `found` is False the caller MUST NOT invent text.
    """
    parsed = parse_reference(reference)
    if not parsed:
        return {"found": False, "error": f"Could not parse reference '{reference}'.", "verses": []}
    book, chapter, start, end = parsed
    rows = _rows(
        "SELECT ref, text FROM verses WHERE book=? AND chapter=? AND verse BETWEEN ? AND ? "
        "AND translation=? ORDER BY verse",
        (book, chapter, start, end, translation),
    )
    return {
        "found": bool(rows),
        "translation": translation,
        "verses": [{"reference": r["ref"], "text": r["text"]} for r in rows],
        "note": None if rows else "Not in seed corpus. Do not fabricate; say it is unavailable.",
    }


@mcp.tool()
def cross_references(reference: str) -> dict:
    """Return cross-references (related passages) for a verse, Treasury-of-Scripture style."""
    rows = _rows("SELECT related FROM cross_refs WHERE ref=?", (reference,))
    return {"reference": reference, "cross_references": [r["related"] for r in rows]}


@mcp.tool()
def search_by_theme(theme: str) -> dict:
    """Retrieve verses indexed under a life theme (e.g. 'anxiety', 'identity', 'purpose').

    Returns matching verse references AND their text, so the agent can ground directly.
    """
    theme = theme.strip().lower()
    refs = [r["ref"] for r in _rows("SELECT ref FROM topics WHERE topic=?", (theme,))]
    verses = []
    for ref in refs:
        v = get_passage(ref)
        if v["found"]:
            verses.extend(v["verses"])
    return {"theme": theme, "matches": verses, "count": len(verses)}


@mcp.tool()
def character_profile(name: str) -> dict:
    """Return a structured biblical character study: struggle, response, lesson, refs."""
    rows = _rows("SELECT * FROM characters WHERE name=? COLLATE NOCASE", (name.strip(),))
    if not rows:
        return {"found": False, "name": name, "note": "Not in seed corpus. Do not invent details."}
    c = rows[0]
    return {
        "found": True,
        "name": c["name"],
        "struggle": c["struggle"],
        "response": c["response"],
        "lesson": c["lesson"],
        "references": json.loads(c["refs"]),
    }


@mcp.tool()
def original_language(reference: str) -> dict:
    """Return Strong's / lexical entries for key words in a verse, when available."""
    rows = _rows("SELECT payload FROM strongs WHERE ref=?", (reference,))
    if not rows:
        return {"reference": reference, "entries": [], "note": "No lexical data for this verse in seed corpus."}
    return {"reference": reference, "entries": json.loads(rows[0]["payload"])}


@mcp.tool()
def topical_index(topic: str) -> dict:
    """List the verse references catalogued under a topic (without full text)."""
    topic = topic.strip().lower()
    refs = [r["ref"] for r in _rows("SELECT ref FROM topics WHERE topic=?", (topic,))]
    return {"topic": topic, "references": refs}


if __name__ == "__main__":
    mcp.run()

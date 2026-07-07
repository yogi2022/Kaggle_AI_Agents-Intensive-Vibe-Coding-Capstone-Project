"""
life_graph.py — longitudinal user memory + Kingdom Health Score.

ADK session state handles within-conversation context. The Life Graph handles
continuity ACROSS sessions: which domains a user keeps returning to, recorded
struggles and wins, and a simple per-domain health score for the dashboard.

Sensitive by design -> stores only structured signals (domain, score, short notes),
never raw confession text. Includes an erase() control for the user's right to delete.
"""

from __future__ import annotations
import sqlite3
import time
from pathlib import Path
from typing import Optional

DB_PATH = Path(__file__).parent / "store.sqlite"
DOMAINS = ["identity", "peace", "purpose", "decision",
           "spiritual_growth", "relationships", "stewardship", "character"]


def _connect(db_path: Path = DB_PATH) -> sqlite3.Connection:
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    conn.execute(
        "CREATE TABLE IF NOT EXISTS life_graph ("
        "user_id TEXT, domain TEXT, score INTEGER, note TEXT, ts REAL, "
        "PRIMARY KEY (user_id, domain))"
    )
    conn.execute(
        "CREATE TABLE IF NOT EXISTS events ("
        "user_id TEXT, kind TEXT, summary TEXT, ts REAL)"
    )
    return conn


def update_domain(user_id: str, domain: str, score: int, note: str = "", db_path: Path = DB_PATH) -> None:
    """Upsert a domain's health score (0-100) and a short, non-sensitive note."""
    score = max(0, min(100, int(score)))
    conn = _connect(db_path)
    with conn:
        conn.execute(
            "INSERT INTO life_graph VALUES (?,?,?,?,?) "
            "ON CONFLICT(user_id, domain) DO UPDATE SET score=excluded.score, note=excluded.note, ts=excluded.ts",
            (user_id, domain, score, note[:140], time.time()),
        )
    conn.close()


def record_event(user_id: str, kind: str, summary: str, db_path: Path = DB_PATH) -> None:
    """Record a life event (e.g. 'new_job', 'loss') to trigger relevant agents later."""
    conn = _connect(db_path)
    with conn:
        conn.execute("INSERT INTO events VALUES (?,?,?,?)", (user_id, kind, summary[:140], time.time()))
    conn.close()


def kingdom_health(user_id: str, db_path: Path = DB_PATH) -> dict:
    """Return per-domain scores and the overall Kingdom Health Score."""
    conn = _connect(db_path)
    rows = conn.execute("SELECT domain, score FROM life_graph WHERE user_id=?", (user_id,)).fetchall()
    conn.close()
    scores = {r["domain"]: r["score"] for r in rows}
    overall = round(sum(scores.values()) / len(scores)) if scores else None
    return {"user_id": user_id, "domains": scores, "overall": overall}


def erase(user_id: str, db_path: Path = DB_PATH) -> None:
    """Delete ALL stored data for a user (data-rights control)."""
    conn = _connect(db_path)
    with conn:
        conn.execute("DELETE FROM life_graph WHERE user_id=?", (user_id,))
        conn.execute("DELETE FROM events WHERE user_id=?", (user_id,))
    conn.close()


if __name__ == "__main__":
    u = "demo"
    erase(u)
    update_domain(u, "identity", 72, "rooted more in Christ")
    update_domain(u, "peace", 53, "still anxious about work")
    update_domain(u, "purpose", 40, "seeking direction")
    print(kingdom_health(u))

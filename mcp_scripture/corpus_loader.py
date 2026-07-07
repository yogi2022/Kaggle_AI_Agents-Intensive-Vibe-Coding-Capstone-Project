"""
corpus_loader.py
----------------
Builds the Berean Scripture corpus (SQLite) from public-domain JSON seed data.

Why SQLite + a local corpus instead of a live Bible API:
  * Deterministic and offline -> the demo never fails on a network hiccup.
  * No rate limits, no per-call latency.
  * Every verse is verifiable, which is what makes "citation faithfulness" measurable.

To scale to a full Bible: drop a full public-domain dataset (e.g. the KJV/WEB JSON
from the scrollmapper/bible_databases project) into data/ and extend `load_full_bible`.
Verify each dataset's license before shipping; never load copyrighted translations
such as NIV or ESV.
"""

from __future__ import annotations
import json
import os
import re
import sqlite3
from pathlib import Path

DATA_DIR = Path(__file__).parent / "data"
DB_PATH = Path(__file__).parent / "corpus.sqlite"


def _connect(db_path: Path = DB_PATH) -> sqlite3.Connection:
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    return conn


def build_corpus(db_path: Path = DB_PATH) -> Path:
    """(Re)build the SQLite corpus from the JSON seed files. Idempotent."""
    if db_path.exists():
        db_path.unlink()
    conn = _connect(db_path)
    cur = conn.cursor()

    cur.executescript(
        """
        CREATE TABLE verses (
            ref TEXT, book TEXT, chapter INTEGER, verse INTEGER,
            translation TEXT, text TEXT,
            PRIMARY KEY (ref, translation)
        );
        CREATE INDEX idx_verses_ref ON verses(ref);
        CREATE TABLE cross_refs (ref TEXT, related TEXT);
        CREATE TABLE characters (name TEXT PRIMARY KEY, struggle TEXT, response TEXT, lesson TEXT, refs TEXT);
        CREATE TABLE strongs (ref TEXT, payload TEXT);
        CREATE TABLE topics (topic TEXT, ref TEXT);
        """
    )

    verses = json.loads((DATA_DIR / "verses.json").read_text())["verses"]
    cur.executemany(
        "INSERT OR REPLACE INTO verses VALUES (:ref,:book,:chapter,:verse,:translation,:text)",
        verses,
    )

    xr = json.loads((DATA_DIR / "cross_refs.json").read_text())["cross_refs"]
    for ref, related in xr.items():
        cur.executemany("INSERT INTO cross_refs VALUES (?,?)", [(ref, r) for r in related])

    chars = json.loads((DATA_DIR / "characters.json").read_text())["characters"]
    for name, c in chars.items():
        cur.execute(
            "INSERT OR REPLACE INTO characters VALUES (?,?,?,?,?)",
            (name, c["struggle"], c["response"], c["lesson"], json.dumps(c["refs"])),
        )

    strongs = json.loads((DATA_DIR / "strongs.json").read_text())["entries"]
    for ref, payload in strongs.items():
        cur.execute("INSERT INTO strongs VALUES (?,?)", (ref, json.dumps(payload)))

    topics = json.loads((DATA_DIR / "topics.json").read_text())["topics"]
    for topic, refs in topics.items():
        cur.executemany("INSERT INTO topics VALUES (?,?)", [(topic, r) for r in refs])

    conn.commit()
    conn.close()
    return db_path


_REF_RE = re.compile(r"^\s*(?P<book>[\w ]+?)\s+(?P<chapter>\d+):(?P<verse>\d+)(?:\s*-\s*(?P<end>\d+))?\s*$")


def parse_reference(reference: str):
    """Parse 'Philippians 4:6' or 'Philippians 4:6-7' into (book, chapter, start, end)."""
    m = _REF_RE.match(reference.replace("Psalm ", "Psalms ").strip())
    if not m:
        return None
    end = int(m.group("end")) if m.group("end") else int(m.group("verse"))
    return m.group("book").strip(), int(m.group("chapter")), int(m.group("verse")), end


def ensure_corpus(db_path: Path = DB_PATH) -> Path:
    if not db_path.exists():
        build_corpus(db_path)
    return db_path


if __name__ == "__main__":
    p = build_corpus()
    conn = _connect(p)
    n = conn.execute("SELECT COUNT(*) AS n FROM verses").fetchone()["n"]
    t = conn.execute("SELECT COUNT(DISTINCT topic) AS n FROM topics").fetchone()["n"]
    print(f"Built corpus at {p}: {n} verses, {t} topics.")

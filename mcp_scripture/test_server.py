"""Direct tests of the Scripture MCP tools (no LLM, no network)."""
from mcp_scripture.server import (
    get_passage, cross_references, search_by_theme,
    character_profile, original_language, topical_index,
)

def test_get_passage_found():
    r = get_passage("Philippians 4:6")
    assert r["found"] and r["verses"][0]["reference"] == "Philippians 4:6"

def test_get_passage_range():
    r = get_passage("Philippians 4:6-7")
    assert len(r["verses"]) == 2

def test_get_passage_missing_is_honest():
    r = get_passage("Hezekiah 9:9")  # not a real book -> must not fabricate
    assert r["found"] is False

def test_theme():
    r = search_by_theme("anxiety")
    assert r["count"] >= 4

def test_character():
    r = character_profile("Joseph")
    assert r["found"] and "deliverance" in r["lesson"].lower()

def test_cross_refs():
    assert "John 14:27" in cross_references("Philippians 4:7")["cross_references"]

if __name__ == "__main__":
    import sys, traceback
    fns = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
    failed = 0
    for fn in fns:
        try:
            fn(); print(f"PASS {fn.__name__}")
        except Exception:
            failed += 1; print(f"FAIL {fn.__name__}"); traceback.print_exc()
    sys.exit(1 if failed else 0)

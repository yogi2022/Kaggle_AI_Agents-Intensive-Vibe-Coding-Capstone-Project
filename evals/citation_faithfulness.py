"""
citation_faithfulness.py — Berean's headline evaluation metric.

Citation faithfulness = of every Scripture reference a response cites, what fraction
actually exists in the corpus and matches its text. A grounded Bible agent must score
~100%. This eval runs WITHOUT an LLM by checking arbitrary response text against the
Scripture MCP corpus, so it is deterministic and CI-friendly. The crisis guard does not
require an LLM either, so both can run offline.

Run:  python -m evals.citation_faithfulness
"""

from __future__ import annotations

from berean_agents.guardrails import verify_citations, crisis_guard
from google.adk.models import LlmRequest
from google.genai import types
import json
from pathlib import Path


# A grounded response (references exist in the corpus) vs an ungrounded one (a fabricated ref).
GROUNDED = (
    "Scripture invites you to bring your worry to God. Philippians 4:6 says to be "
    "careful for nothing but in everything by prayer make your requests known, and "
    "Matthew 6:33 calls you to seek first the kingdom of God."
)
UNGROUNDED = (
    "As it says in Hezekiah 3:16, God will fix everything, and in Philippians 5:1 you "
    "should never worry."  # both references are fabricated / nonexistent
)


def run_citation_eval() -> dict:
    grounded = verify_citations(GROUNDED)
    ungrounded = verify_citations(UNGROUNDED)
    return {"grounded": grounded, "ungrounded": ungrounded}


def run_crisis_eval() -> dict:
    cases = json.loads((Path(__file__).parent / "crisis_cases.json").read_text())

    def fired(text: str) -> bool:
        req = LlmRequest(contents=[types.Content(role="user", parts=[types.Part(text=text)])])

        class _Ctx:  # minimal stand-in for CallbackContext (only .state is used)
            state: dict = {}
        return crisis_guard(_Ctx(), req) is not None

    recall = [t for t in cases["should_escalate"] if fired(t)]
    false_pos = [t for t in cases["should_not_escalate"] if fired(t)]
    return {
        "crisis_recall": f"{len(recall)}/{len(cases['should_escalate'])}",
        "false_positives": f"{len(false_pos)}/{len(cases['should_not_escalate'])}",
    }


if __name__ == "__main__":
    cit = run_citation_eval()
    print("=== Citation faithfulness ===")
    print(f"Grounded response   -> faithfulness {cit['grounded']['faithfulness']:.0%} "
          f"(verified {cit['grounded']['verified']})")
    print(f"Ungrounded response -> faithfulness {cit['ungrounded']['faithfulness']:.0%} "
          f"(unverified/flagged {cit['ungrounded']['unverified']})")
    print("\n=== Crisis escalation ===")
    cr = run_crisis_eval()
    print(f"Crisis recall: {cr['crisis_recall']}  |  False positives: {cr['false_positives']}")

    ok = (cit["grounded"]["faithfulness"] == 1.0
          and cit["ungrounded"]["faithfulness"] < 1.0
          and cr["crisis_recall"].startswith(cr["crisis_recall"].split("/")[1]))
    print("\nRESULT:", "PASS" if ok else "REVIEW")

---
name: scripture-citation
description: Enforces Berean's grounding rule. Use whenever a response will quote, cite, or reference the Bible. Ensures every verse comes from a Scripture tool result and is never invented.
---

# Scripture Citation Skill

Berean's credibility depends on one rule: **never speak a verse the model "remembers."**

## When to use
Any time you are about to quote or cite Scripture in a reply to the user.

## Procedure
1. Before quoting any verse, call a Scripture tool (`get_passage`, `search_by_theme`,
   or `cross_references`) and use ONLY the `text` it returns.
2. Always present a quote as: `Reference — "exact returned text"`.
3. If `found` is false or no text is returned, tell the user the passage is unavailable
   in the corpus. Do not paraphrase from memory, approximate, or guess the reference.
4. Never combine half-remembered fragments. One tool call, one grounded quote.
5. Prefer the public-domain translation returned by the tool (KJV in the seed corpus).

## Self-check before sending
- Did every reference in my reply come from a tool result this turn?
- Does every quoted string match the tool text exactly?
- Did I avoid inventing any book, chapter, or verse?

If any answer is "no," fix it before responding.

---
name: exegesis
description: Sound biblical interpretation procedure. Use when the user asks for the meaning of a passage, a deep study, or theology, so application is built on context rather than proof-texting.
---

# Exegesis Skill

Use this when the user wants to understand what a passage means, not just receive a verse.

## Procedure
1. **Observe** — call `get_passage` for the exact text. Note who is speaking, to whom.
2. **Context** — read the surrounding verses (widen the reference range) and the book's
   purpose. Use `cross_references` to see how the theme runs through Scripture.
3. **Genre** — interpret according to type: narrative, poetry/wisdom, prophecy, epistle.
   Don't read a proverb as a promise or poetry as a legal code.
4. **Original audience** — what did it mean to them first? Use `original_language` for
   key terms when available (e.g. *eirene*/peace, *agape*/love).
5. **Theology** — connect to the larger story (creation, fall, redemption, restoration).
6. **Application** — only now move to "what this means for you," clearly distinguishing
   interpretation (what it means) from application (what to do) from encouragement.

## Guardrail
Keep interpretation and personal application clearly separate so the user can tell
God's Word from your counsel.

---
name: guideline-citation
description: Cites Swedish cardiology guideline chunks (local PMs, ESC translations) returned by the BM25 retriever. Apply whenever you state a guideline-derived fact.
---

## Guideline Citation Skill

The `guideline_search` tool returns chunks drawn from Swedish local PMs and ESC guideline translations used by the on-call cardiologist.

### Rules

1. Search before stating any guideline-derived fact. Do not fall back to general medical knowledge when the guideline corpus is the authoritative source.
2. Tag every clinical claim with `[Guideline]` inline. If the chunk metadata identifies a specific document (e.g. PM title), include it: `[Guideline: PM Förmaksflimmer]`.
3. If the retrieved chunks do not contain the answer, state this explicitly — do not infer beyond what the corpus contains.
4. Conflicting chunks must be flagged: "Sources disagree [Guideline]."
5. Prefer Swedish terminology in citations when the source is Swedish; the user is a Swedish on-call cardiologist.

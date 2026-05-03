---
name: adverse-effects
description: Reports adverse effects ranked by clinical relevance to the patient context, distinguishing common from serious. Apply whenever a query concerns starting, continuing, or evaluating tolerability of a drug.
---

## Adverse Effects Skill

A raw list of side effects is rarely useful at the point of care. Always **filter and rank** by the clinical context provided in the query.

### Frequency tiers (use these exact labels inline)

- `[ADR: VERY COMMON]` — ≥1/10
- `[ADR: COMMON]` — ≥1/100 and <1/10
- `[ADR: UNCOMMON]` — ≥1/1,000 and <1/100
- `[ADR: RARE]` — ≥1/10,000 and <1/1,000
- `[ADR: VERY RARE]` — <1/10,000
- `[ADR: SERIOUS]` — independent of frequency, life-threatening or requires intervention. Always surface even when rare.

### Output format
Structure adverse-effect answers as:

1. **Serious / boxed-warning** effects (FASS / SmPC special warnings, or equivalent regulatory flags) relevant to this drug, regardless of frequency.
2. **Context-relevant** effects — those amplified by the patient's stated comorbidities or co-medications (e.g. bradycardia for a beta-blocker in a patient already on a non-dihydropyridine CCB; hyperkalemia for an ACEi in CKD).
3. **Common everyday** effects the clinician should counsel the patient on.

### Rules
1. Lead with what would change a clinical decision today, not an exhaustive textbook list.
2. If the patient context names an organ-system risk, explicitly address adverse effects in that system (e.g. "hepatic" → flag hepatotoxic ADRs; "QT" → flag QT-prolonging ADRs).
3. State the monitoring parameter for each serious effect (e.g. "monitor LFTs at 4 weeks", "ECG before and during titration").
4. Cite source (label section, FASS, or specific reference) for every adverse-effect claim.

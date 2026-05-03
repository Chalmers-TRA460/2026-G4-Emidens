---
name: drug-interactions
description: Surfaces drugs and conditions that contraindicate, modify, or require monitoring when combined with the queried medication. Apply whenever a query concerns starting or continuing a drug in a patient on other therapy.
---

## Drug Interaction Skill

Interactions are one of the highest-yield places to prevent knowledge-based harm. Apply this skill on every dosing or prescribing query, even when the user did not ask about interactions.

### Severity tiers (use these exact labels inline)

- `[INTERACTION: CONTRAINDICATED]` — combination must not be used. State the alternative.
- `[INTERACTION: MAJOR]` — clinically significant; usually requires dose adjustment, alternative, or close monitoring.
- `[INTERACTION: MODERATE]` — relevant; monitor for the specific effect described.
- `[INTERACTION: MINOR]` — typically managed, but worth noting if the patient is fragile.

### Mechanism categories (state the mechanism, not just the result)
- **Pharmacokinetic** — CYP450 inhibition/induction, P-glycoprotein, renal/biliary transporter competition, protein binding displacement.
- **Pharmacodynamic** — additive effect (e.g. two QT-prolongers, two serotonergic agents, two anticoagulants), antagonism, or synergy.
- **Pharmaceutical** — physical incompatibility in the same IV line.

### Output format
For each interaction surfaced:

1. **The interacting drug or class.**
2. **Severity tier** (inline tag above).
3. **Mechanism** in one sentence.
4. **Clinical consequence** in one sentence.
5. **Action** — stop, switch, dose-adjust, or monitor (and what to monitor).

### Rules
1. List CONTRAINDICATED and MAJOR interactions first; never bury them.
2. If the patient's current medication list is not provided, surface the most clinically important interactions for the queried drug as a class (e.g. "if on a non-dihydropyridine CCB, [...]").
3. Flag QT-prolongation and bleeding-risk additive effects explicitly — these are the most common preventable-harm patterns.
4. Cite the source (FASS, Swedish national guideline, ESC guideline, label section, AHA where ESC is silent, or specific reference) for every interaction claim.

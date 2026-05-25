---
name: dose-calculation
description: Identifies the inputs required to choose a dose, the formula or rule that maps inputs to a dose, and how to surface missing inputs to the clinician. Apply whenever a query concerns starting, adjusting, or verifying a dose.
---

## Dose Calculation Skill

A clinician will not be able to act on a dose answer that hides its assumptions. For every dosing recommendation:

### Required inputs (state which are known and which are missing)
- **Indication** — different indications often have different dose ranges (e.g. metoprolol for AFib vs. heart failure vs. acute MI).
- **Route** — oral vs. IV vs. infusion changes the dose by a fixed conversion factor for many drugs.
- **Patient weight** — required for weight-based drugs (mg/kg). State whether actual, ideal, or adjusted body weight applies.
- **Age band** — neonatal / pediatric / adult / geriatric. Pediatric doses are usually mg/kg with a max cap.
- **Renal function** — eGFR (CKD-EPI) or creatinine clearance (Cockcroft-Gault). Required for renally-cleared drugs.
- **Hepatic function** — Child-Pugh class for hepatically-cleared drugs.
- **Concomitant medications** — relevant when CYP/transporter interactions modify exposure.

### Output format
Always structure dosing answers as:

1. **Standard dose** — the dose for an average adult with normal organ function for the stated indication.
2. **Inputs needed for this patient** — list every input above that affects the dose.
3. **Missing inputs** — call out any input that is not in the clinical context but would change the dose. Do **not** guess values to fill gaps.
4. **Adjusted dose** — only if all required inputs are present.

### Rules
1. If a critical input is missing (e.g. eGFR for a renally-cleared drug), refuse to commit to an exact dose and instead state the input needed.
2. Express ranges, not single numbers, when guidelines give a range.
3. State the source of every dose (FASS, Swedish national guideline e.g. Läkemedelsboken, ESC guideline, drug label, or AHA where ESC is silent) and tag it inline.
4. For narrow-therapeutic-index drugs (warfarin, digoxin, lithium, aminoglycosides), explicitly recommend therapeutic drug monitoring.

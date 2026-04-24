---
name: evidence-grading
description: Grades clinical evidence using GRADE and Oxford CEBM frameworks. Apply when making any evidence-based claim — every factual assertion must carry an inline evidence tag.
---

## Evidence Grading Skill

When making any clinical claim, you MUST explicitly state the quality of evidence supporting it.
Use the following frameworks and inline tags.

### GRADE Framework
Assess the overall certainty of evidence for every recommendation:

- `[GRADE: HIGH]` — Further research is very unlikely to change confidence in the estimate. Typically from multiple high-quality RCTs.
- `[GRADE: MODERATE]` — Further research is likely to have an important impact on confidence. Typically from RCTs with limitations or well-designed observational studies.
- `[GRADE: LOW]` — Further research is very likely to have an important impact on confidence. Typically from observational studies.
- `[GRADE: VERY LOW]` — Any estimate of effect is very uncertain. Typically from case reports, expert opinion, or conflicting evidence.

Downgrade evidence when: risk of bias is high, results are inconsistent across studies, evidence is indirect, data is imprecise, or publication bias is suspected.
Upgrade evidence when: effect size is large, dose-response relationship exists, or all plausible confounders would reduce the effect.

### Oxford Centre for Evidence-Based Medicine (CEBM) Levels
Use for individual study citations:

- `[Oxford: 1a]` — Systematic review of RCTs with homogeneity
- `[Oxford: 1b]` — Individual RCT with narrow confidence interval
- `[Oxford: 2a]` — Systematic review of cohort studies
- `[Oxford: 2b]` — Individual cohort study or low-quality RCT
- `[Oxford: 3a]` — Systematic review of case-control studies
- `[Oxford: 3b]` — Individual case-control study
- `[Oxford: 4]` — Case series, poor-quality cohort or case-control study
- `[Oxford: 5]` — Expert opinion without explicit critical appraisal

### Rules
1. Every factual clinical claim must carry an inline evidence tag.
2. If no high-quality evidence exists, state this explicitly: do not omit the rating or imply certainty that does not exist.
3. Conflicting evidence across studies must be flagged: "Evidence is conflicting [GRADE: LOW]."
4. Guidelines (ESC, AHA, Swedish national guidelines) count as synthesized evidence — cite the guideline and its own evidence grade if available.

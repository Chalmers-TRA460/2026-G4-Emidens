---
name: dose-calculation
description: Calculate medication doses for Swedish healthcare using FASS, Janusmed, Strama, and Kloka listan. Use when user asks about drug dosing, dose adjustments, or medication calculations - trigger phrases include "vilken dos", "how much", "dosering", "dose calculation", "adjust dose", "renal dosing", "pediatric dose", or mentions specific drugs with dosing questions. Handles vague ranges ("10-20 mg") by making decision inputs explicit.

---

# Dose Calculation Skill

## Core Principle

**A clinician will not be able to act on a dose answer that hides its assumptions.**

Survey finding: *"Som student kan jag ibland fundera över om patienten ska ha 10 mg eller 20 mg av ett viss läkemedel och rekommendationerna säger '10-20 mg' vilket inte ger mig någon ny information"*

This skill transforms vague dosing ranges into actionable recommendations by making all decision inputs explicit.

## Quick Reference

**For urgent dosing questions:**
- ✅ **Always state:** Standard dose, required inputs, missing inputs, source
- ✅ **Never hide:** Assumptions, ranges, or uncertainty
- ✅ **Always cite:** FASS, Janusmed, Strama, or other Swedish sources
- ⚠️ **Refuse to commit** if critical inputs missing (don't guess renal function, weight, etc.)

## Workflow Instructions

### Step 1: Identify Required Inputs

Systematically check these inputs in order:

1. **Indication** - Why the drug is being given (different indications = different doses)
2. **Route** - Oral/IV/other (affects dose by conversion factors)
3. **Patient Weight** - Required for mg/kg dosing
4. **Age Band** - Neonatal/pediatric/adult/geriatric
5. **Renal Function** - eGFR for renally-cleared drugs
6. **Hepatic Function** - Child-Pugh class for hepatically-metabolized drugs
7. **Concomitant Medications** - Check Janusmed for interactions

**Missing critical inputs:** DO NOT GUESS for weight-based dosing, narrow therapeutic index drugs, or renal/hepatic impairment. State what's missing and why it's critical.

### Step 2: Search Swedish Sources in Priority Order

1. **FASS** - Start here (regulatory approved dosing)
   - "Dosering" section for standard doses
   - "Dosering vid nedsatt njurfunktion" for renal adjustments
   - "Dosering vid nedsatt leverfunktion" for hepatic adjustments
   - "Barn och ungdom" for pediatric dosing
   - "Äldre patienter" for geriatric considerations

2. **Strama** (for antibiotics) - Evidence-based national guidelines
   - Specifies exact dose + frequency + duration
   - More specific than FASS for infections

3. **Kloka listan** - First-line recommendations and starting doses
   - Often narrows FASS range to specific starting dose

4. **Janusmed** - Interaction checking and clearer dosing tables
   - Essential for drug-drug interaction assessment

5. **Local PM** - Hospital-specific protocols (if mentioned in query)

6. **Internetmedicin** - Treatment duration and monitoring guidance

### Step 3: Handle Vague Ranges

When FASS gives a range (e.g., "10-20 mg"), don't just repeat it:

1. **Check for specific guidance:**
   - Does Kloka listan or Strama specify a starting dose?
   - Do FASS subsections narrow the range ("Äldre patienter", "Barn")?

2. **If no specific guidance, identify decision factors:**
   - **Severity:** Mild → lower, Severe → higher
   - **Age:** Elderly → lower ("start low, go slow")
   - **Renal function:** Impaired → lower
   - **Hepatic function:** Impaired → lower
   - **Previous response:** Treatment failure → higher

3. **Make specific recommendation with rationale:**
   ```
   FASS RANGE: 50-100 mg twice daily
   
   DECISION FACTORS:
   - Age 75 (elderly) → lower dose
   - eGFR 45 (G3a) → lower dose
   - Moderate severity → middle range
   
   RECOMMENDED: 50 mg twice daily
   RATIONALE: Age and renal factors favor lower dose despite moderate severity
   ```

4. **Provide titration plan:**
   - Starting dose
   - When to reassess (typically 2-4 weeks)
   - When/how to increase
   - Maximum dose

### Step 4: Apply Safety Checks

Before finalizing any dose:

- **Contraindications:** Check FASS "Kontraindikationer"
- **Interactions:** Use Janusmed interaction checker (especially if >2 medications)
- **Narrow therapeutic index:** State monitoring plan (TDM, labs)
  - Examples: gentamicin, vancomycin, warfarin, digoxin, lithium
- **Formulation match:** Verify dose matches available strengths
- **Maximum dose:** Check FASS for daily/single dose limits

### Step 5: Format Output with Transparency

Always structure your response:

```
DOSE RECOMMENDATION: [Drug name]

INDICATION: [Why drug is being given]
ROUTE: [Oral/IV/other]

PATIENT INPUTS:
✅ [Input]: [Value] (Source: stated/assumed/calculated)
✅ [Input]: [Value]
❌ [Missing input]: NOT PROVIDED - [why it matters]

FASS DOSING:
"[Exact quote from FASS]"

[OTHER SOURCES if applicable]:
- Kloka listan: [Specific guidance]
- Strama: [Specific guidance]

RECOMMENDED DOSE:
[Specific dose with frequency and duration]

RATIONALE:
- [Why this specific dose within the range]
- [What assumptions were made]
- [What adjustments were applied]

TITRATION PLAN (if applicable):
- Week 0-X: [Starting dose]
- Week X+: [When/how to adjust]
- Maximum: [FASS maximum]

SOURCES:
- FASS: [Section referenced]
- [Other sources used]

MONITORING:
- [What to check and when]

PATIENT COUNSELING (if relevant):
- [Key points patient needs to know]
```

## Handling Missing Critical Inputs

When critical inputs are missing for narrow therapeutic index or weight-based drugs:

```
CANNOT PROVIDE DOSE

MISSING CRITICAL INPUT: [What's missing]

Why critical:
- [Explanation of why this input is essential]
- [What could go wrong if guessed]

What dose depends on:
1. [Missing input] - REQUIRED
2. [Other factors]

Example doses for reference (NOT patient-specific):
- [General range to show scale]

ACTION REQUIRED:
1. ✅ Obtain [missing input]
2. ✅ [Other actions needed]

DO NOT guess [input] for [drug class/situation].
```

## Source Conflict Resolution

When sources disagree:

1. **Identify the conflict:**
   - What differs? (dose, frequency, duration)
   - Are all within FASS approved range?

2. **Apply hierarchy:**
   - FASS defines what's ALLOWED (regulatory approval)
   - Strama/Kloka listan = Evidence-based preference (national guidelines)
   - Local PM = Institutional preference (must be within FASS range)

3. **Document decision:**
   ```
   SOURCES CONSULTED:
   - FASS: "1-2 g × 3-4 daily" (approved range)
   - Strama: "1 g × 3 daily" (national guideline)
   - Local PM: "1 g × 4 daily" (hospital protocol)
   
   RECOMMENDED: 1 g × 3 daily
   RATIONALE: Following Strama national guideline (all options within FASS range)
   ALTERNATIVE: 1 g × 4 daily also acceptable per Local PM for severe cases
   ```

## Key Input Details

### Indication
- Different indications = different doses (e.g., metoprolol 50-100 mg for HTN vs. 15 mg IV for MI)
- Source: FASS "Indikationer", Strama (infections), Kloka listan (condition-specific)

### Route of Administration
- Common conversions:
  - Metoprolol: PO 100 mg ≈ IV 5 mg (20:1)
  - Furosemid: PO 40 mg ≈ IV 20 mg (2:1)
  - Morfin: PO 30 mg ≈ IV 10 mg (3:1)
- Source: FASS lists each formulation separately

### Patient Weight
- Required for: mg/kg dosing (especially pediatrics)
- Types: Actual body weight (ABW), Ideal body weight (IBW), Adjusted body weight (AdjBW)
- IBW formula (Swedish): Male: 50 + 0.9×(height in cm - 152), Female: 45.5 + 0.9×(height in cm - 152)
- **Never guess weight for:** aminoglycosides, pediatric dosing, narrow therapeutic index drugs

### Age Band
Swedish conventions:
- Neonate: 0-28 days (often requires specialist)
- Infant: 1-12 months
- Child: 1-12 years
- Adolescent: 12-18 years
- Adult: 18-65 years
- Elderly: >65 years (FASS: "äldre patienter")
- Very elderly: >80 years

Geriatric principle: "Start low, go slow"

### Renal Function
- Swedish standard: **eGFR** (CKD-EPI) in ml/min/1.73 m²
- GFR categories (KDIGO):
  - G1: ≥90 (normal)
  - G2: 60-89 (mild, usually no adjustment)
  - G3a: 45-59 (monitor)
  - G3b: 30-44 (often needs adjustment)
  - G4: 15-29 (major adjustment)
  - G5: <15 (many drugs contraindicated)
- Source: FASS "Dosering vid nedsatt njurfunktion", Janusmed tables
- **Check for:** All elderly, renally-cleared drugs, drugs with renal dosing section in FASS

### Hepatic Function
- Swedish assessment: **Child-Pugh class**
  - A (5-6 points): Mild, usually no adjustment
  - B (7-9 points): Moderate, often 50% reduction
  - C (10-15 points): Severe, many drugs contraindicated
- Source: FASS "Dosering vid nedsatt leverfunktion"

### Concomitant Medications
- Tool: **Janusmed Interactions** (primary in Sweden)
- Interaction severity: A (none), B (minor), C (moderate), D (contraindicated)
- Common issues: CYP450 interactions, renal competition, additive effects
- Always check if patient has >2 medications

## Special Populations

### Pediatric Dosing
- Almost always mg/kg with maximum dose cap
- Example: "10-15 mg/kg var 4-6:e timme, max 60 mg/kg/dygn"
- If not in FASS "Barn och ungdom" → may state "Används ej till barn" → requires specialist
- **Never extrapolate from adult doses**
- **Always use actual weight**

### Geriatric Dosing
- Start at lower end of FASS range
- FASS often specifies: "Äldre patienter: Börja med lägre dos, vanligen halva vuxendosen"
- Linked to reduced renal function (GFR declines with age)
- Increased sensitivity to CNS drugs, anticholinergics, anticoagulants

### Narrow Therapeutic Index Drugs
Require TDM (Therapeutic Drug Monitoring):
- **Aminoglycosides** (gentamicin, tobramycin): Trough before 3rd dose, peak at 1hr
- **Vancomycin**: Trough target 10-20 mg/L
- **Warfarin**: INR monitoring (target 2-3 for most indications)
- **Digoxin**: Serum level 0.5-2 ng/mL
- **Lithium**: Serum level 0.6-1.2 mmol/L

Always state monitoring plan.

## Antibiotic-Specific Guidance

For ALL antibiotic queries:

1. **Check Strama first** - Usually more specific than FASS
2. **Include duration** - Strama specifies (e.g., "7 days")
3. **Note if second-line** - Strama lists first-line vs. alternatives
4. **Consider local resistance** - May affect choice
5. **Specify infection site** - Different infections = different doses/durations

Example Strama format:
- Indication: Community-acquired pneumonia
- First-line: Penicillin V 1 g × 3 for 7 days
- Alternative (PCN allergy): Doxycycline 200 mg day 1, then 100 mg × 7 days

## Quality Checklist

Before finalizing any dose recommendation:

**Required inputs:**
- [ ] Indication clearly stated
- [ ] Route specified
- [ ] Age category determined
- [ ] Weight obtained (if weight-based)
- [ ] Renal function checked (if renally-cleared)
- [ ] Hepatic function checked (if hepatically-metabolized)
- [ ] Medications reviewed (Janusmed)

**Sources cited:**
- [ ] FASS section referenced with exact quote
- [ ] Swedish guidelines cited (Strama/Kloka listan if applicable)
- [ ] Assumptions stated explicitly

**Safety:**
- [ ] Contraindications ruled out
- [ ] Interactions checked
- [ ] Narrow therapeutic index → monitoring plan
- [ ] Elderly/renal/hepatic → adjustments applied

**Practicality:**
- [ ] Dose matches available formulations
- [ ] Frequency realistic for compliance
- [ ] Monitoring plan specified
- [ ] Titration plan (if applicable)

**Missing inputs:**
- [ ] Critical missing inputs → refused to provide dose
- [ ] Non-critical missing inputs → assumptions stated
- [ ] Action items clear

## Example Outputs

### Example 1: Clear Case

**Query:** "Metoprolol for hypertension, 45-year-old, eGFR 80, no other medications"

```
DOSE RECOMMENDATION: Metoprolol

INDICATION: Hypertension
ROUTE: Oral (tablet)

PATIENT INPUTS:
✅ Age: 45 years (healthy adult)
✅ Renal function: eGFR 80 (normal, no adjustment)
✅ Other medications: None

FASS DOSING:
"Hypertoni: 50-100 mg 2 gånger dagligen"

KLOKA LISTAN:
Metoprolol listed as acceptable beta-blocker for hypertension

RECOMMENDED DOSE:
Start: 50 mg twice daily (morning and evening)

RATIONALE:
- Standard starting dose at lower end of FASS range
- Healthy adult with normal renal function
- No contraindications or interactions

TITRATION:
- Week 0-4: 50 mg twice daily
- If BP not at goal → increase to 75-100 mg twice daily
- Maximum: 100 mg twice daily (FASS)

MONITORING:
- Blood pressure and heart rate at 2 weeks and 4 weeks
- Target BP: <140/90
```

### Example 2: Missing Critical Input

**Query:** "Dose gentamicin for sepsis, no weight provided"

```
CANNOT PROVIDE DOSE

Drug: Gentamicin
Indication: Sepsis

❌ MISSING CRITICAL INPUT: Patient weight

WHY WEIGHT IS CRITICAL:
- Gentamicin is dosed as mg/kg (FASS: "5-7 mg/kg per dose")
- Narrow therapeutic index
- Wrong dose → treatment failure OR nephrotoxicity/ototoxicity
- Cannot assume weight for critically ill patient

FASS DOSING (once weight obtained):
"5-7 mg/kg som engångsdos var 24:e timme"

WHAT DOSE DEPENDS ON:
1. Patient weight in kg (ACTUAL) - MISSING
2. Renal function (eGFR) - needed for interval
3. Severity (sepsis = 7 mg/kg)

EXAMPLE DOSES (reference only):
- 70 kg patient: 490 mg every 24 hours
- 90 kg patient: 630 mg every 24 hours

ACTION REQUIRED:
1. ✅ Obtain patient weight in kg
2. ✅ Obtain eGFR
3. ✅ Consult pharmacy (gentamicin requires specialist dosing)
4. ✅ Plan TDM: Trough before 3rd dose

DO NOT guess weight for aminoglycosides.
```

### Example 3: Vague Range Resolved

**Query:** "Sertraline for depression, 30-year-old healthy adult, no other medications"

```
DOSE RECOMMENDATION: Sertraline

INDICATION: Depression (major depressive disorder)
ROUTE: Oral tablet

PATIENT INPUTS:
✅ Age: 30 years (healthy adult)
✅ Renal/hepatic: Assumed normal
✅ Other medications: None

FASS DOSING:
"Depression: 50-200 mg dagligen"

KLOKA LISTAN:
"Sertraline 50-200 mg (börja med 50 mg)"

RECOMMENDED DOSE:
Start: 50 mg once daily (morning)

RATIONALE:
- Kloka listan explicitly specifies 50 mg starting dose
- First episode depression
- Young healthy adult
- No contraindications

TITRATION:
- Week 0-4: 50 mg daily (assess tolerability)
- Week 4-6: If inadequate response → increase to 100 mg
- Maximum: 200 mg daily (FASS)
- Therapeutic effect: 4-6 weeks

SOURCES:
- Kloka listan: Start 50 mg
- FASS: Approved range 50-200 mg

PATIENT COUNSELING:
- May take 4-6 weeks for full effect
- Common side effects: Nausea, headache (usually transient)
- Do NOT stop abruptly

MONITORING:
- Follow-up in 2 weeks (tolerability)
- Follow-up in 4-6 weeks (efficacy)
```

### Example 4: Source Conflict

**Query:** "Pneumonia antibiotic, 85-year-old, eGFR 30. FASS says 1-2 g × 3-4, Strama says 1 g × 3"

```
DOSE RECOMMENDATION: Penicillin V

INDICATION: Community-acquired pneumonia

PATIENT INPUTS:
✅ Age: 85 years (very elderly)
✅ Renal: eGFR 30 (G4 - severe impairment)

SOURCE ANALYSIS:

FASS: "1-2 g × 3-4 gånger dagligen"
- Regulatory approved range (what's allowed)

STRAMA: "1 g × 3 gånger dagligen i 7 dagar"
- National evidence-based guideline

RESOLUTION:
All sources agree: 1 g per dose ✅
Differ on frequency: × 3 vs. × 4

RECOMMENDED DOSE:
1 g three times daily × 7 days

RATIONALE:
- Following Strama national guideline
- All options within FASS range
- Simpler regimen (× 3 vs. × 4) better for elderly
- No specific renal adjustment for PcV per FASS

ALTERNATIVE:
1 g × 4 daily also acceptable for severe pneumonia

SOURCES:
- FASS: Approved range confirms both options
- Strama: "1 g × 3 for 7 days" (national standard)

MONITORING:
- Clinical response in 48-72 hours
- If worsening → consider increasing frequency
```

## Integration with Other Skills

- **fass-dosing-navigator** - Use when needing to efficiently search FASS for specific sections
- Works alongside Swedish clinical guideline skills

## Version History

- **v2.1.0 (2026-05-05):** Restructured based on Anthropic Skills Guide
  - Improved description with specific trigger phrases
  - Clearer step-by-step workflow instructions
  - Condensed from 7,000+ words to ~3,500 words
  - Enhanced output formatting guidance
  - Maintained all safety features and Swedish source integration
  
- **v2.0.0:** Major update integrating Swedish healthcare sources
- **v1.0.0:** Initial release

---
name: dose-calculation
description: Identifies the inputs required to choose a dose, the formula or rule that maps inputs to a dose, and how to surface missing inputs to the clinician. Apply whenever a query concerns starting, adjusting, or verifying a dose. Integrates Swedish healthcare sources (FASS, Janusmed, Strama, Kloka listan) and handles vague dosing ranges with clinical decision support.
license: MIT
metadata:
  author: Healthcare Workflow Optimization
  version: 2.0.0
  category: healthcare
  tags: [dosing, dose-calculation, swedish-healthcare, clinical-decision-support]
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

## Required Inputs for Every Dose

### 1. Indication
**Why it matters:** Different indications often have different dose ranges

**Examples:**
- Metoprolol: 50-100 mg bid for hypertension vs. 15 mg IV for acute MI
- Warfarin: INR 2-3 for DVT vs. 2.5-3.5 for mechanical valve
- Prednisolon: 5-10 mg for maintenance vs. 40-60 mg for acute inflammation

**Swedish sources:**
- FASS "Indikationer" section lists approved uses
- Strama for infection indications
- Kloka listan for first-line vs. second-line by condition

**Output format:**
```
Indication: Hypertension (not acute MI, not heart failure)
Source: Stated in query / FASS approved indication
Impact on dose: Determines whether 50-100 mg bid (hypertension) vs. different dosing for other indications
```

### 2. Route of Administration
**Why it matters:** Oral vs. IV vs. infusion changes dose by fixed conversion factors

**Common conversions:**
- Metoprolol: PO 100 mg ≈ IV 5 mg (20:1 ratio)
- Furosemid: PO 40 mg ≈ IV 20 mg (2:1 ratio, approximately)
- Morfin: PO 30 mg ≈ IV 10 mg (3:1 ratio)

**Swedish sources:**
- FASS lists all available formulations with separate dosing
- Search FASS for each formulation separately (e.g., "Metoprolol tabletter" vs. "Metoprolol injektionsvätska")

**Output format:**
```
Route: Oral (tablet)
Source: Query specifies oral / FASS tablet formulation
Alternative routes: IV available with different dosing (see FASS injektionsvätska)
```

### 3. Patient Weight
**Why it matters:** Required for weight-based drugs (mg/kg)

**Weight types:**
- **Actual body weight (ABW):** Most common for children, healthy adults
- **Ideal body weight (IBW):** For hydrophilic drugs in obese patients (e.g., aminoglycosides)
- **Adjusted body weight (AdjBW):** For some drugs in obesity (e.g., some chemotherapy)

**Formula for IBW (Swedish convention):**
- Male: 50 kg + 0.9 × (height in cm − 152)
- Female: 45.5 kg + 0.9 × (height in cm − 152)

**Swedish practice:**
- Pediatric dosing almost always mg/kg based on actual weight
- FASS specifies "mg/kg kroppsvikt" when weight-based
- Check FASS for maximum dose cap (e.g., "max 2 g/dygn")

**Output format:**
```
Patient weight: 75 kg (actual body weight)
Source: Stated in query
Weight-based calculation needed: Yes (drug is dosed as mg/kg per FASS)
Maximum dose cap: 2 g per day (FASS)
```

**If weight is missing:**
```
Patient weight: NOT PROVIDED — required for weight-based dosing
Action needed: Ask clinician for patient weight before calculating dose
Cannot proceed: Weight-based drugs require actual patient weight
```

### 4. Age Band
**Why it matters:** Neonatal / pediatric / adult / geriatric have different dosing

**Age categories (Swedish convention):**
- **Neonate:** 0-28 days (often NOT in standard FASS, requires specialist)
- **Infant:** 1-12 months
- **Child:** 1-12 years (often subdivided: 1-6 years, 6-12 years)
- **Adolescent:** 12-18 years
- **Adult:** 18-65 years
- **Elderly:** >65 years (FASS often says "äldre patienter")
- **Very elderly:** >80 years (often needs dose reduction)

**Swedish sources:**
- FASS "Dosering" → "Barn och ungdom" subsection
- FASS "Dosering" → "Äldre patienter" subsection
- Janusmed often has clearer age-based dosing tables

**Pediatric considerations:**
- Usually mg/kg with maximum dose cap
- Example from FASS: "10-15 mg/kg var 4-6:e timme, max 60 mg/kg/dygn"
- If not approved for children, FASS will state "Används ej till barn"

**Geriatric considerations:**
- "Start low, go slow" principle
- Increased sensitivity to side effects
- Often linked to renal function (GFR declines with age)
- Example from FASS: "Äldre patienter: Börja med lägre dos, vanligen halva vuxendosen"

**Output format:**
```
Age: 75 years (elderly adult)
Source: Stated in query
Age-specific adjustments: FASS recommends starting with lower dose in elderly
Standard adult dose: 100 mg twice daily
Elderly starting dose: 50 mg twice daily (FASS "Äldre patienter" section)
Rationale: Increased sensitivity and likely reduced renal function
```

### 5. Renal Function
**Why it matters:** Renally-cleared drugs accumulate in renal impairment

**Swedish standard: eGFR (CKD-EPI)**
- Reported in ml/min/1.73 m²
- Found in patient's lab results as "eGFR"
- Swedish labs automatically calculate from creatinine

**Alternative: Creatinine clearance (Cockcroft-Gault)**
- Sometimes needed for drug dosing tables (less common in Sweden)
- Formula: CrCl = ((140-age) × weight in kg × 0.85 if female) / (72 × Creatinine in mg/dL)
- Swedish creatinine is in µmol/L: divide by 88.4 to convert to mg/dL

**When to check renal function:**
- All elderly patients (GFR declines with age)
- Renally-cleared drugs (check FASS "Farmakokinetik" for % renal excretion)
- Drugs with "Dosering vid nedsatt njurfunktion" section in FASS

**Swedish source hierarchy:**
1. **FASS:** Ctrl+F "njurfunktion" → GFR-based dose adjustments
2. **Janusmed:** Often has clearer GFR-based dosing tables
3. **Local PM:** May have hospital-specific renal dosing protocols

**GFR categories (Swedish/KDIGO classification):**
- G1: eGFR ≥90 (normal)
- G2: eGFR 60-89 (mild reduction, usually no adjustment)
- G3a: eGFR 45-59 (mild-moderate, monitor)
- G3b: eGFR 30-44 (moderate-severe, often needs adjustment)
- G4: eGFR 15-29 (severe, usually needs major adjustment)
- G5: eGFR <15 (kidney failure, many drugs contraindicated)

**Output format:**
```
Renal function: eGFR 35 ml/min/1.73 m² (G3b - moderate-severe impairment)
Source: Stated in query / patient lab results
FASS guidance: "GFR 30-60: Reduce dose to 50% of standard dose"
Adjusted dose: 50 mg daily (instead of 100 mg daily)
Source: FASS "Dosering vid nedsatt njurfunktion"
Monitoring: Check creatinine regularly, adjust as needed
```

**If eGFR is missing:**
```
Renal function: NOT PROVIDED
Drug characteristics: 80% renal excretion (FASS Farmakokinetik)
Action needed: MUST obtain eGFR before dosing
Cannot proceed: High risk of accumulation if renal impairment undetected
Alternative: If patient is young (<40), healthy, no risk factors → assume normal GFR (but document assumption)
```

### 6. Hepatic Function
**Why it matters:** Hepatically-metabolized drugs need dose reduction in liver disease

**Swedish assessment: Child-Pugh class**
- **Class A (5-6 points):** Mild, usually no adjustment
- **Class B (7-9 points):** Moderate, often 50% dose reduction
- **Class C (10-15 points):** Severe, many drugs contraindicated

**When to check hepatic function:**
- Patients with known cirrhosis
- Drugs with >50% hepatic metabolism (FASS "Farmakokinetik")
- FASS section "Dosering vid nedsatt leverfunktion" exists

**Swedish sources:**
- FASS: Ctrl+F "lever" or "hepat" → dose adjustments
- FASS "Kontraindikationer" → may be contraindicated in severe liver disease
- Janusmed: Sometimes has Child-Pugh-based dosing

**Output format:**
```
Hepatic function: Child-Pugh Class B (moderate cirrhosis)
Source: Stated in query / patient clinical status
FASS guidance: "Nedsatt leverfunktion: Minska dosen med 50%"
Adjusted dose: 50 mg daily (instead of 100 mg daily)
Source: FASS "Dosering vid nedsatt leverfunktion"
```

### 7. Concomitant Medications
**Why it matters:** CYP/transporter interactions modify drug exposure

**Swedish source: Janusmed Interaktioner**
- **Best tool** for checking drug-drug interactions in Sweden
- Rates interactions: Green (no interaction), Yellow (monitor), Orange (caution), Red (contraindicated)
- Provides dose adjustment recommendations

**Common interactions requiring dose adjustment:**
- Warfarin + antibiotics → INR monitoring, possible dose reduction
- Statins + CYP3A4 inhibitors → statin dose reduction
- Methotrexate + NSAIDs → increased toxicity risk
- Digoxin + verapamil → digoxin dose reduction

**Output format:**
```
Concomitant medications: Warfarin, atorvastatin, metoprolol
Interaction check: Janusmed Interaktioner
Relevant interaction: None affecting dose of current drug
Proceed with: Standard dosing
```

**If interaction affects dose:**
```
Concomitant medications: Warfarin
Interaction: New antibiotic may increase INR (Janusmed: Orange - caution)
Dose adjustment: No immediate warfarin dose change needed
Monitoring: Check INR in 3-5 days, adjust warfarin dose if needed
Source: Janusmed Interaktioner + FASS warfarin
```

## Output Format Template

**For every dosing recommendation, structure as:**

```
DOSE RECOMMENDATION FOR: [Drug name]

INDICATION: [Specific indication]
Source: [Query / FASS approved indication]

ROUTE: [Oral / IV / other]
Source: [Query / FASS formulation]

PATIENT INPUTS:
✅ Age: [X years] → [Category: adult/elderly/pediatric]
✅ Weight: [X kg] → [Required: Yes/No]
✅ Renal function: [eGFR X] → [Category: G1/G2/G3a/G3b/G4/G5]
✅ Hepatic function: [Normal / Child-Pugh X]
❌ [Any missing input]: NOT PROVIDED - see below

STANDARD DOSE (for normal adult with normal organ function):
[X mg/dose] [frequency] [duration]
Source: FASS "Dosering" section / Strama / Kloka listan

ADJUSTMENTS FOR THIS PATIENT:

[If elderly:]
Elderly adjustment: Start with [X mg] (FASS recommends lower starting dose in elderly)

[If renal impairment:]
Renal adjustment: eGFR [X] → Reduce to [X mg] per FASS "Dosering vid nedsatt njurfunktion"

[If hepatic impairment:]
Hepatic adjustment: Child-Pugh [X] → Reduce to [X mg] per FASS "Dosering vid nedsatt leverfunktion"

[If weight-based:]
Weight-based calculation: [X mg/kg] × [weight] = [X mg], capped at [max dose] per FASS

RECOMMENDED DOSE FOR THIS PATIENT:
[X mg] [frequency] [duration]

SOURCES:
- FASS: [specific sections cited]
- [Janusmed / Strama / Kloka listan / Local PM]: [if used]

MISSING INPUTS (if any):
❌ [Input name]: Required because [reason]
Action: [Obtain from clinician / lab / patient record]
Cannot commit to exact dose until: [input obtained]

MONITORING (if applicable):
- [Drug levels / labs / clinical signs]
- [Frequency of monitoring]
- [When to reassess dose]

SAFETY NOTES:
[Narrow therapeutic index / Black box warnings / Special precautions]
```

## Handling Vague Dosing Ranges

### Problem: "FASS says 10-20 mg" - Which dose?

**Survey finding:** This is one of the most frustrating aspects of dosing for students and junior doctors.

### Decision Framework

**Step 1: Check FASS for internal guidance**
Sometimes FASS provides guidance within the range:
- "Börja med 10 mg, kan ökas till 20 mg efter 1-2 veckor"
- "Vanligen 15 mg, dosintervall 10-20 mg"
- "10 mg för lindriga fall, 20 mg för måttliga till svåra fall"

**Step 2: Apply patient-specific factors**

**Start with LOWER end of range when:**
- ✅ Elderly (>65-70 years)
- ✅ Renal impairment (eGFR <60)
- ✅ Hepatic impairment
- ✅ Low body weight (<60 kg)
- ✅ Frail or debilitated
- ✅ Multiple medications (polypharmacy >5 drugs)
- ✅ First episode of condition
- ✅ Narrow therapeutic index drug

**Start with HIGHER end of range when:**
- ✅ Young healthy adult (18-50 years)
- ✅ Severe or acute condition
- ✅ Previous treatment failure at lower dose
- ✅ High body weight (if not weight-based dosing)
- ✅ Rapid control needed (e.g., acute symptom relief)

**Step 3: Check Kloka listan / Strama for national recommendations**
- Often more specific than FASS
- May state "recommended starting dose" within FASS range
- Example: FASS says "50-200 mg", Kloka listan says "start with 50 mg"

**Step 4: Check local PM for hospital-specific protocols**
- May have standardized starting doses
- Reflects local patient population and practice patterns

**Output format when FASS gives range:**
```
FASS dosing range: 10-20 mg once daily

Patient factors:
- Age: 75 years (elderly)
- eGFR: 45 (moderate renal impairment)
- Other medications: 6 concurrent drugs

Recommendation: START WITH 10 mg (lower end of range)

Rationale:
- Elderly patient → increased sensitivity
- Moderate renal impairment → risk of accumulation
- Polypharmacy → drug interaction risk
- FASS principle: "start low, go slow" in elderly

Titration plan:
- Start 10 mg daily
- Reassess after 1-2 weeks
- If inadequate response and well-tolerated → increase to 15 mg
- Maximum: 20 mg (FASS upper limit)

Source: FASS dose range + clinical decision-making based on patient factors
```

## Handling Missing Inputs

### Critical vs. Non-Critical Missing Inputs

**CRITICAL missing inputs (refuse to commit to dose):**
- ❌ Renal function for renally-cleared drug (>50% renal excretion)
- ❌ Weight for weight-based dosing (especially pediatrics)
- ❌ Hepatic function for hepatically-metabolized drug in patient with known liver disease
- ❌ Drug levels for narrow therapeutic index drugs requiring monitoring

**Output when critical input missing:**
```
CANNOT RECOMMEND EXACT DOSE

Missing critical input: eGFR

Why it's critical:
- Drug is 80% renally excreted (FASS Farmakokinetik)
- Dose adjustment required for eGFR <60
- Risk of accumulation and toxicity if renal function impaired

Standard dose (for eGFR >60): 100 mg twice daily
Potential adjusted doses based on eGFR:
- eGFR 30-60: 50 mg twice daily
- eGFR 15-30: 25 mg twice daily
- eGFR <15: Contraindicated

ACTION REQUIRED: Obtain eGFR before prescribing
```

**NON-CRITICAL missing inputs (can provide dose with assumptions stated):**
- Patient weight (if NOT weight-based dosing)
- Exact age (if clearly adult and no extreme age concerns)
- Complete medication list (if no high-risk interactions expected)

**Output when non-critical input missing but assumption made:**
```
RECOMMENDED DOSE: 100 mg twice daily

ASSUMPTION MADE:
- Patient age not stated, assuming adult 18-65 years
- If patient is >65 years, consider starting with 50 mg twice daily
- If patient is <18 years, STOP - pediatric dosing requires age and weight

ACTION: Verify patient age before prescribing
```

## Swedish Source Hierarchy for Dosing

### When to use which Swedish source

**1. FASS (Always check first)**
- **Use for:** Approved dosing, contraindications, official prescribing information
- **Strength:** Regulatory authority, comprehensive
- **Weakness:** Often gives wide ranges without clinical guidance

**2. Strama (Infections)**
- **Use for:** First-line antibiotic choice and dosing
- **Strength:** National evidence-based antibiotic stewardship
- **Weakness:** Only covers antibiotics
- **Example:** "Nedre luftvägsinfektion: PcV 1 g x 3 i 7 dagar"

**3. Kloka listan (First-line treatment)**
- **Use for:** Which drug to choose within FASS-approved options
- **Strength:** Evidence-based first-line recommendations
- **Weakness:** Not all conditions covered

**4. Janusmed**
- **Use for:** Interactions, pregnancy/breastfeeding, clearer renal dosing tables
- **Strength:** Practical clinical guidance, better organized than FASS
- **Weakness:** Region Stockholm-specific (but widely used nationally)

**5. Local PM (Hospital protocols)**
- **Use for:** Hospital-specific dosing protocols
- **Strength:** Tailored to local patient population and practice
- **Weakness:** Access restricted, may not be evidence-based

**6. Internetmedicin**
- **Use for:** Clinical context, when to treat, clinical decision-making
- **Strength:** Overview of condition and management
- **Weakness:** Less specific on exact dosing than FASS

### Multi-source dosing workflow

**Example: "What antibiotic and dose for pneumonia?"**

**Step 1 - Strama:** First-line choice
→ "PcV 1 g x 3 or Amoxicillin 500 mg x 3"

**Step 2 - FASS:** Verify dosing, check contraindications
→ PcV: "1-2 g x 3-4" (FASS gives range)
→ Check patient allergies, contraindications

**Step 3 - Patient factors:** Adjust based on renal function, age
→ eGFR 35: FASS says "No adjustment needed for PcV"
→ Age 80: FASS says "No specific elderly dose reduction"

**Step 4 - Final decision:**
→ PcV 1 g x 3 (Strama first-line dose, FASS approved, no adjustment needed)

**Output:**
```
RECOMMENDED ANTIBIOTIC DOSE:

Drug: Penicillin V (PcV)
Indication: Pneumonia (community-acquired)
Dose: 1 g three times daily (oral)
Duration: 7 days

SOURCES:
- Strama: First-line recommendation for pneumonia
- FASS: Approved dosing range 1-2 g x 3-4, chose 1 g x 3 per Strama
- FASS: No renal adjustment needed (patient eGFR 35)
- FASS: No elderly-specific adjustment

PATIENT INPUTS:
✅ Age: 80 years (elderly)
✅ eGFR: 35 (G3b - moderate-severe impairment)
✅ Allergies: No penicillin allergy reported

MONITORING:
- Clinical response in 48-72 hours
- No drug level monitoring needed
```

## Narrow Therapeutic Index Drugs

**Survey finding:** Clinicians want explicit guidance on when monitoring is needed.

### High-risk drugs requiring therapeutic drug monitoring (TDM)

**Swedish practice - Always monitor:**

**1. Warfarin**
- Monitor: INR
- Frequency: Every 1-2 days initially, then weekly, then monthly when stable
- Target: INR 2-3 (most indications), 2.5-3.5 (mechanical valves)
- Source: FASS + Janusmed + Local anticoagulation clinic

**2. Digoxin**
- Monitor: Serum digoxin level
- Frequency: At steady state (5-7 days), then as needed
- Target: 0.5-2.0 nmol/L (FASS range varies by indication)
- Swedish note: Lower targets often used in elderly (0.5-1.0 nmol/L)

**3. Lithium**
- Monitor: Serum lithium level
- Frequency: Weekly until stable, then every 3 months
- Target: 0.6-1.0 mmol/L (maintenance), 0.8-1.2 mmol/L (acute)
- Also monitor: Renal function, thyroid function

**4. Aminoglycosides (Gentamicin, Tobramycin)**
- Monitor: Peak and trough levels
- Frequency: After 3rd dose, then per protocol
- Target: Varies by indication (consult pharmacy/infectious disease)

**5. Phenytoin**
- Monitor: Serum phenytoin level
- Frequency: At steady state (7-10 days), dose changes, drug interactions
- Target: 40-80 µmol/L (FASS)

**6. Methotrexate (high-dose)**
- Monitor: Serum methotrexate level + renal function
- Frequency: Per oncology protocol
- Requires leucovorin rescue based on levels

**Output format for narrow therapeutic index drugs:**
```
RECOMMENDED DOSE: Warfarin 5 mg daily (initial dose)

⚠️ NARROW THERAPEUTIC INDEX DRUG
Requires intensive monitoring:

MONITORING PLAN:
- INR: Check on Day 3-4, then adjust dose based on result
- INR: Every 1-2 days until stable in range
- INR: Weekly when stable, then monthly
- Target INR: 2-3 (for DVT treatment per query)

DOSE ADJUSTMENT:
- INR <2: Increase dose (per protocol or anticoagulation clinic)
- INR 2-3: Continue current dose
- INR >3: Hold 1 dose, reduce maintenance dose
- INR >4: Contact anticoagulation clinic

SAFETY:
- Bleeding risk: Monitor for signs of bleeding
- Drug interactions: Check Janusmed before adding any new medication
- Diet: Counsel on vitamin K-containing foods (consistency matters)

Source: FASS warfarin + Janusmed + Local anticoagulation protocol
```

## Pediatric Dosing - Special Considerations

**Survey finding:** "Om du inte vet barnets vikt och ålder, vågar du inte ge en dos."

### Critical rules for pediatric dosing

**1. NEVER guess pediatric doses**
- If weight/age missing → REFUSE to give dose
- If FASS says "Används ej till barn" → STOP, consult pediatrician
- If off-label → ALWAYS consult pediatrician

**2. Always check maximum dose cap**
- Pediatric doses are usually mg/kg with upper limit
- Example: "10 mg/kg, max 500 mg per dose"
- ALWAYS apply the cap

**3. Round to available formulations**
- Calculate exact dose, then round to what's available
- Example: Calculated 156 mg → Available as 5 ml of 25 mg/ml suspension → Round to 150 mg (6 ml) or 175 mg (7 ml)
- Document the rounding decision

**Output format for pediatric dosing:**
```
PEDIATRIC DOSE CALCULATION

Patient: 5 years old, 18 kg

Drug: Paracetamol (Alvedon)
Indication: Fever
Route: Oral suspension (24 mg/ml)

FASS PEDIATRIC DOSING:
"10-15 mg/kg per dos, max 60 mg/kg/dygn, max 4 doser/dygn"

CALCULATION:
Weight-based dose: 10-15 mg/kg
Lower range: 10 mg/kg × 18 kg = 180 mg
Upper range: 15 mg/kg × 18 kg = 270 mg
Maximum single dose: 270 mg (within safe range)
Maximum daily dose: 60 mg/kg × 18 kg = 1080 mg/day

AVAILABLE FORMULATION:
Oral suspension 24 mg/ml

Volume calculation:
270 mg ÷ 24 mg/ml = 11.25 ml

PRACTICAL ROUNDING:
Recommend: 11 ml (264 mg) per dose
Frequency: Every 6 hours as needed (max 4 doses/day)
Maximum daily: 44 ml (1056 mg) - within 1080 mg limit

PARENT INSTRUCTION:
"Give 11 ml of Alvedon oral suspension every 6 hours as needed for fever, maximum 4 times per day"

Source: FASS Alvedon "Barn och ungdom" section
```

**If critical input missing:**
```
CANNOT PROVIDE PEDIATRIC DOSE

Missing: Patient weight

Why critical:
- Pediatric dosing is weight-based (mg/kg per FASS)
- Calculation impossible without weight
- Risk of over/underdosing

ACTION REQUIRED:
1. Obtain patient weight in kg
2. Verify patient age (dosing may differ for infants vs. children)
3. Return with weight for dose calculation

DO NOT proceed with adult dosing assumptions for children.
```

## Real-World Examples

### Example 1: Straightforward Adult Dosing

**Query:** "Start metoprolol for hypertension in 45-year-old healthy patient"

```
DOSE RECOMMENDATION: Metoprolol

INDICATION: Hypertension (first-line beta-blocker per Kloka listan)

ROUTE: Oral tablet

PATIENT INPUTS:
✅ Age: 45 years (adult, no elderly adjustments needed)
✅ Renal function: Assumed normal (young, no risk factors stated)
✅ Hepatic function: Assumed normal
✅ Other medications: None stated

STANDARD DOSE:
50-100 mg twice daily
Source: FASS "Dosering" section for hypertension

RECOMMENDATION FOR THIS PATIENT:
Start: 50 mg twice daily (lower end of range for initial therapy)
Titration: Increase to 100 mg twice daily after 1-2 weeks if BP remains elevated
Maximum: 200 mg twice daily (FASS)

SOURCES:
- FASS: Approved dosing 50-200 mg bid for hypertension
- Kloka listan: First-line beta-blocker recommendation

MONITORING:
- Blood pressure: Check in 1-2 weeks
- Heart rate: Should be 50-60 bpm on therapy
- If inadequate BP control: Increase dose or add second agent
```

### Example 2: Elderly with Renal Impairment

**Query:** "Ciprofloxacin for UTI, 78-year-old, eGFR 40"

```
DOSE RECOMMENDATION: Ciprofloxacin

INDICATION: UTI (uncomplicated lower urinary tract infection)

ROUTE: Oral tablet

PATIENT INPUTS:
✅ Age: 78 years (elderly)
✅ Renal function: eGFR 40 ml/min/1.73 m² (G3b - moderate-severe impairment)
✅ Weight: Not required (not weight-based dosing)

STANDARD DOSE (for normal renal function):
500 mg twice daily × 3 days (Strama for uncomplicated UTI)

FASS RENAL ADJUSTMENT:
"GFR 30-50: 250-500 mg x 2"

JANUSMED GUIDANCE:
eGFR 30-50: Reduce dose to 250 mg x 2

ELDERLY CONSIDERATIONS:
FASS: "Äldre patienter med nedsatt njurfunktion: särskild försiktighet"

RECOMMENDED DOSE:
250 mg twice daily × 3 days

RATIONALE:
- eGFR 40 (G3b) requires dose reduction (FASS + Janusmed)
- Elderly → increased sensitivity + falls risk (fluoroquinolones)
- Choose LOWER end of FASS range (250 mg vs. 500 mg) given age + renal function

SOURCES:
- Strama: First-line fluoroquinolone for UTI when indicated
- FASS: Renal dosing adjustment for GFR 30-50
- Janusmed: Confirms 250 mg x 2 for eGFR 30-50

SAFETY NOTES:
⚠️ Fluoroquinolones: Tendon rupture risk (especially elderly)
⚠️ Falls risk: Dizziness, CNS effects more common in elderly
⚠️ Counsel patient: Avoid strenuous exercise, report tendon pain immediately

MONITORING:
- Clinical response in 48 hours
- Renal function if treatment extends beyond 3 days
```

### Example 3: Missing Critical Input

**Query:** "Dose gentamicin for sepsis, no weight provided"

```
CANNOT PROVIDE DOSE

Drug: Gentamicin
Indication: Sepsis

MISSING CRITICAL INPUT: Patient weight

Why weight is critical:
- Gentamicin is dosed as mg/kg (FASS: "5-7 mg/kg per dose")
- Narrow therapeutic index (requires TDM)
- Wrong dose → inadequate treatment OR nephrotoxicity/ototoxicity
- Cannot assume average weight for critically ill patient

FASS DOSING (once weight obtained):
"5-7 mg/kg som engångsdos var 24:e timme"

WHAT DOSE DEPENDS ON:
- Patient weight in kg (actual body weight)
- Renal function (eGFR) - may need interval adjustment
- Indication (higher doses for severe infections)
- Whether extended-interval or traditional dosing

EXAMPLE DOSES (for reference only, NOT patient-specific):
- 70 kg patient: 350-490 mg every 24 hours
- 90 kg patient: 450-630 mg every 24 hours
- Obese patient: May use adjusted body weight (consult pharmacy)

ACTION REQUIRED:
1. ✅ Obtain patient weight in kg
2. ✅ Obtain eGFR
3. ✅ Consult pharmacy for dosing (gentamicin requires specialist dosing)
4. ✅ Plan TDM: Trough level before 3rd dose

DO NOT guess weight for narrow therapeutic index aminoglycosides.
```

### Example 4: Vague Range with Decision Support

**Query:** "Start sertraline for depression, 30-year-old healthy adult, no other medications"

```
DOSE RECOMMENDATION: Sertraline

INDICATION: Depression (major depressive disorder)

ROUTE: Oral tablet

PATIENT INPUTS:
✅ Age: 30 years (healthy adult)
✅ Renal function: Assumed normal (young, no risk factors)
✅ Hepatic function: Assumed normal
✅ Other medications: None (no interactions)
✅ Previous SSRI use: Not stated, assuming first episode

FASS DOSING RANGE:
"50-200 mg dagligen"

KLOKA LISTAN RECOMMENDATION:
First-line SSRI: Sertraline or Escitalopram
Starting dose: "Sertraline 50 mg dagligen"

RECOMMENDED DOSE:
Start: 50 mg once daily (morning)
Duration: Minimum 6 months after symptom resolution (per Internetmedicin)

RATIONALE FOR STARTING DOSE:
- Kloka listan specifies 50 mg (lower end of FASS range)
- First episode depression → start with standard dose
- Young healthy adult → no need for extra-low dose
- No contraindications or interactions

TITRATION PLAN:
- Week 0-2: 50 mg daily (assess tolerability)
- Week 2-4: If partial response → continue 50 mg
- Week 4: If inadequate response → increase to 100 mg daily
- Maximum: 200 mg daily (FASS)
- Therapeutic effect: May take 4-6 weeks at adequate dose

SOURCES:
- Kloka listan: First-line SSRI, starting dose 50 mg
- FASS: Approved range 50-200 mg for depression
- Internetmedicin: Duration of treatment guidance

PATIENT COUNSELING:
- May take 2-4 weeks to notice effect
- Common initial side effects: Nausea, headache (usually transient)
- Take with food if nausea occurs
- Do NOT stop abruptly (risk of discontinuation syndrome)

MONITORING:
- Follow-up in 2 weeks: Assess tolerability and early response
- Follow-up in 4-6 weeks: Assess efficacy, consider dose increase if needed
```

### Example 5: Multi-source Conflict Resolution

**Query:** "Antibiotic for pneumonia, 85-year-old, eGFR 30. FASS says 1-2 g x 3-4, Strama says 1 g x 3, Local PM says 1 g x 4. Which is right?"

```
DOSE RECOMMENDATION: Penicillin V (PcV)

INDICATION: Community-acquired pneumonia

PATIENT INPUTS:
✅ Age: 85 years (very elderly)
✅ Renal function: eGFR 30 ml/min/1.73 m² (G4 - severe impairment)

SOURCE ANALYSIS:

FASS: "1-2 g × 3-4 gånger dagligen"
- Regulatory range (all approved doses)
- No specific renal adjustment noted for PcV
- Widest range, least specific

STRAMA: "1 g × 3 gånger dagligen"
- National evidence-based recommendation
- Standard dose for community-acquired pneumonia
- Duration: 7 days

LOCAL PM: "1 g × 4 gånger dagligen"
- Hospital-specific protocol
- May reflect local practice patterns
- Could be for more severe cases

RESOLUTION HIERARCHY:
1. All three sources agree on 1 g per dose ✅
2. Frequency differs: x 3 (Strama) vs. x 4 (Local PM)
3. Both are within FASS approved range ✅

RECOMMENDED DOSE:
1 g three times daily × 7 days

RATIONALE:
- Dose: 1 g (all sources agree, lower end for elderly + severe renal impairment)
- Frequency: × 3 (per Strama national guideline)
- PcV has no specific renal adjustment in FASS
- Very elderly → prefer simpler regimen (x3 vs. x4 for compliance)
- Strama represents national evidence-based practice

ALTERNATIVE (if hospital culture prefers):
1 g four times daily × 7 days (per Local PM)
- Also acceptable within FASS range
- Slightly higher total daily dose (4 g vs. 3 g)
- May be preferred for more severe pneumonia

SOURCES:
- Strama: National first-line recommendation
- FASS: Confirms both regimens within approved range
- Local PM: Hospital protocol (consider if severe pneumonia)

CLINICAL DECISION:
Start with 1 g × 3 (Strama)
If severe pneumonia or inadequate response → increase to 1 g × 4 (within FASS range and Local PM protocol)

DOCUMENTATION:
"Started PcV 1 g × 3 per Strama national guideline (FASS approved 1-2 g × 3-4). Dose appropriate for eGFR 30 (no specific adjustment required per FASS)."
```

## Quality Checklist

Before finalizing any dose recommendation, verify:

**✅ Required inputs**
- [ ] Indication clearly stated
- [ ] Route specified (oral/IV/other)
- [ ] Age category determined (pediatric/adult/elderly)
- [ ] Weight obtained (if weight-based dosing)
- [ ] Renal function checked (if renally-cleared drug)
- [ ] Hepatic function checked (if hepatically-metabolized drug)
- [ ] Concomitant medications reviewed (Janusmed)

**✅ Sources cited**
- [ ] FASS section referenced (e.g., "Dosering", "Dosering vid nedsatt njurfunktion")
- [ ] Swedish guidelines cited (Strama/Kloka listan if applicable)
- [ ] Any assumptions stated explicitly

**✅ Safety considerations**
- [ ] Contraindications ruled out (FASS "Kontraindikationer")
- [ ] Interactions checked (Janusmed)
- [ ] Narrow therapeutic index → monitoring plan stated
- [ ] Elderly/renal/hepatic → adjustments applied

**✅ Clinical practicality**
- [ ] Dose matches available formulations
- [ ] Frequency realistic for patient compliance
- [ ] Monitoring plan specified
- [ ] Titration plan provided (if applicable)
- [ ] Patient counseling points noted

**✅ Missing inputs handled**
- [ ] Critical missing inputs → refused to commit to dose
- [ ] Non-critical missing inputs → assumptions stated
- [ ] Action items clear for clinician

## Version History

- **v2.0.0 (2026-05-04):** Major update integrating Swedish healthcare practice and survey findings
  - Added Quick Reference section for urgent dosing questions
  - Expanded "Handling Vague Dosing Ranges" with clinical decision framework (addresses "10-20 mg" problem)
  - Added Swedish source hierarchy (FASS, Strama, Kloka listan, Janusmed, Local PM, Internetmedicin)
  - Added multi-source conflict resolution examples
  - Added complete workflow integrating multiple Swedish sources
  - Enhanced pediatric dosing section with "never guess" safety rules
  - Expanded narrow therapeutic index section with Swedish TDM practices
  - Added real-world examples based on Swedish clinical scenarios
  - Integrated with FASS navigator skill workflow
  - Added quality checklist for dose verification

- **v1.0.0:** Initial release with core dose calculation framework

---
name: side-effects
description: Reports adverse effects filtered and ranked by clinical relevance to patient context, distinguishing common from serious. Use when prescribing, counseling, or evaluating drug tolerability—particularly when user mentions "biverkningar", "side effects", "tolerability", "ADR", "can I give to [patient description]", or asks about starting/continuing medication. Apply proactively when patient context suggests specific organ-system risks.

---

# Adverse Effects Skill

A raw list of side effects is rarely useful at the point of care. This skill filters and ranks adverse effects by clinical context, emphasizing what would change a clinical decision today. Uses Swedish sources (janusmed.se, FASS) as primary references.

## Instructions

### Step 1: Extract Clinical Context

Identify from the query:
- **Drug being evaluated** (generic name preferred)
- **Patient factors**:
  - Age (pediatric, elderly, pregnancy/breastfeeding)
  - Organ function (renal, hepatic impairment)
  - Comorbidities (cardiovascular, diabetes, psychiatric, etc.)
  - Current medications (potential for additive toxicity)
- **Clinical scenario**: starting new drug, troubleshooting existing therapy, counseling patient

If context is minimal, surface the most clinically important ADRs but note that risk stratification requires patient-specific information.

### Step 2: Search Swedish Sources

**Primary workflow:**
1. Navigate to **janusmed.se** → search drug → "Biverkningar" (Adverse effects) section
2. Review frequency classifications and organ-system breakdown
3. Check for "Särskilda varningar" (Special warnings) and contraindications

**Secondary source:**
- **FASS** (https://www.fass.se) → drug SPC → "Biverkningar" section for detailed frequency data and post-marketing reports

### Step 3: Categorize by Clinical Priority

Use this three-tier structure for your output:

#### Tier 1: Serious / Boxed-Warning Effects
Effects that are:
- Life-threatening or require immediate intervention
- Subject to regulatory warnings (FASS "Särskilda varningar", EMA safety alerts)
- Relevant to this drug **regardless of frequency**

Tag with: `[ADR: SERIOUS]`

#### Tier 2: Context-Relevant Effects
Effects amplified by patient's specific situation:
- Existing organ dysfunction (e.g., hepatotoxicity in liver disease)
- Additive effects with co-medications (e.g., bradycardia with beta-blocker + verapamil)
- Age-related vulnerability (e.g., anticholinergic effects in elderly)
- Comorbidity interaction (e.g., hyperglycemia in diabetes)

#### Tier 3: Common Counseling Points
Effects patients will commonly experience, requiring counseling:
- Usually `[ADR: VERY COMMON]` or `[ADR: COMMON]`
- Impact daily function or adherence
- Manageable with supportive measures

### Step 4: Apply Frequency Labels

Use these exact inline tags based on FASS/EMA frequency definitions:

- `[ADR: VERY COMMON]` — ≥1/10 (≥10%)
- `[ADR: COMMON]` — ≥1/100 and <1/10 (1-10%)
- `[ADR: UNCOMMON]` — ≥1/1,000 and <1/100 (0.1-1%)
- `[ADR: RARE]` — ≥1/10,000 and <1/1,000 (0.01-0.1%)
- `[ADR: VERY RARE]` — <1/10,000 (<0.01%)
- `[ADR: SERIOUS]` — independent of frequency, always surface

### Step 5: Include Monitoring Parameters

For each serious effect, specify:
- **What to monitor** (lab test, vital sign, symptom)
- **When to monitor** (baseline, during titration, ongoing)
- **Action threshold** (when to hold drug or adjust dose)

### Step 6: Format Output

For each adverse effect surfaced:

1. **Effect name** with frequency/severity tag
2. **Clinical relevance** to this patient (why it matters here)
3. **Monitoring/management** (specific parameter + timing)
4. **Källa** (Source: janusmed.se, FASS with section reference)

## Examples

### Example 1: Starting SSRI in Elderly Patient with Hyponatremia History

**User says:** "85-årig kvinna, tidigare hyponatremi, ska starta sertralin. Biverkningar att tänka på?"

**Actions:**
1. Search janusmed.se for "sertralin" → "Biverkningar"
2. Identify hyponatremia as context-relevant risk
3. Surface serious/context-specific effects first

**Output:**
```
TIER 1: ALLVARLIGA BIVERKNINGAR (Serious Effects)

[ADR: SERIOUS] Hyponatremi (SIADH)
Klinisk relevans: Särskilt förhöjd risk hos äldre (>65 år) och vid tidigare 
hyponatremi. Kan ge förvirring, fall, kramper.

Övervakning: S-Natrium vid baseline, efter 1-2 veckor, vid dos-ökning, och vid 
nya symtom (förvirring, illamående, huvudvärk). Hold sertralin om Na <125 mmol/L 
eller symtomatisk.

Källa: janusmed.se - SSRI biverkningar, FASS sertralin SPC avsnitt 4.4 + 4.8

---

[ADR: SERIOUS] Blödningsrisk (särskilt GI-blödning)
Klinisk relevans: SSRI hämmar trombocytfunktion. Risk ökar med ålder >80 år.

Övervakning: Fråga om blödningshistorik, undvik NSAID-kombination, överväg PPI 
om hög GI-risk. Instruera patient att rapportera blödningstecken.

Källa: FASS sertralin, Swedish national guidelines on SSRI safety

---

TIER 2: KONTEXTRELEVANTA BIVERKNINGAR (Context-Specific)

[ADR: COMMON] Illamående (frekvens ~20%)
Klinisk relevans: Kan förvärra nutritionsstatus hos äldre. Vanligast första veckan.

Hantering: Ta med mat, starta låg dos (25 mg), titrera långsamt. Avtar efter 1-2 veckor.

---

[ADR: COMMON] Yrsel/sedation
Klinisk relevans: Fallrisk hos äldre. Särskild risk om diuretika samtidigt 
(hypovolemi + yrsel).

Hantering: Varna patient om fallrisk, starta kvällsdos, se över övriga CNS-aktiva 
läkemedel.

---

TIER 3: VANLIGA BIVERKNINGAR (Common Counseling Points)

[ADR: VERY COMMON] Huvudvärk (10-15%)
Hantering: Vanligen övergående, paracetamol vid behov.

[ADR: COMMON] Muntorrhet, förstoppning
Hantering: God munhygien, ökad vätskeintag, fibrer i kosten.

Källa: janusmed.se biverkningsprofil SSRI, FASS sertralin
```

### Example 2: Metformin in Patient with Declining Renal Function

**User says:** "Patient on metformin 1g bid, eGFR dropped to 35. Side effects to worry about?"

**Actions:**
1. Search janusmed.se for "metformin" → check renal dosing guidance
2. Identify lactic acidosis risk at eGFR <30-45
3. Surface dose-adjustment requirement

**Output:**
```
TIER 1: ALLVARLIG BIVERKNING MED AKUT ÅTGÄRD (Serious - Immediate Action Required)

[ADR: SERIOUS] Laktacidos (Lactic Acidosis)
Klinisk relevans: Risk ökar kraftigt vid eGFR <45 ml/min pga. metforminackumulation. 
Vid eGFR <30: kontraindikation. Vid eGFR 30-45: max 1000 mg/dag.

AKUT ÅTGÄRD: eGFR 35 → Reducera dos till 500 mg dagligen. Ny eGFR-kontroll om 3 mån. 
Om fortsatt försämring till <30 → avsluta metformin, överväg annan antidiabetika 
(DPP4-hämmare, SGLT2-hämmare med njurskydd).

Övervakning: 
- eGFR var 3-6:e månad vid instabil njurfunktion
- Vid akutsjukdom (infektion, dehydrering): pausera metformin tillfälligt
- Varna patient om laktacidossymtom: andnöd, buksmärta, muskelkramper, trötthet

Källa: janusmed.se - metformin njurdosering, FASS metformin SPC avsnitt 4.3-4.4

---

TIER 2: KONTEXTRELEVANTA BIVERKNINGAR

[ADR: VERY COMMON] GI-besvär (diarré, illamående, buksmärta - 10-30%)
Klinisk relevans: Kan förvärra dehydrering och njurfunktion vid nedsatt eGFR.

Hantering vid fortsatt metformin: Ta med mat, övergå till depottablett (Metformin 
Depot) för bättre GI-tolerans.

Källa: FASS metformin
```

### Example 3: Minimal Context - General Adverse Effect Query

**User says:** "Starting amiodarone. Side effects?"

**Actions:**
1. Search janusmed.se/FASS for "amiodaron"
2. No patient context provided → surface most clinically important ADRs
3. Note that risk stratification requires patient-specific information

**Output:**
```
Amiodarone has många allvarliga biverkningar. Komplett riskvärdering kräver patient-
specifik information (ålder, hjärtfunktion, leverfunktion, tyreoideafunktion, lung-
funktion). Nedan är de viktigaste biverkningarna att screena för:

TIER 1: ALLVARLIGA BIVERKNINGAR (Kräver baslinje-screening + regelbunden övervakning)

[ADR: SERIOUS] Lungfibros/pneumonit (1-17% i långtidsbehandling)
Baseline: Lungröntgen, spirometri, DLCO
Övervakning: Klinisk bedömning var 6:e mån, lungröntgen årligen, DLCO vid symtom
Symtom: Nytillkommen dyspné, hosta, feber → avsluta amiodaron omedelbart

---

[ADR: SERIOUS] Tyreoideastörningar (hyper- eller hypothyreos - 14-18%)
Baseline: TSH, fritt T4, fritt T3
Övervakning: TSH + fritt T4 var 6:e månad under behandling
Åtgärd: Vid hyperthyreos → endokrinolog, kardiolog (risk för arytmi-försämring)

---

[ADR: SERIOUS] Levertoxicitet (15-50% lätt ALAT-stegring, <3% allvarlig)
Baseline: ALAT, ASAT, ALP, bilirubin
Övervakning: Leverkörtel var 6:e månad, vid dos-ökning
Åtgärd: Hold amiodaron om ALAT >3x ULN eller symtomatisk

---

[ADR: SERIOUS] QT-förlängning → torsades de pointes
Baseline: EKG (QTc), elektrolyter (K, Mg)
Övervakning: EKG efter 1 vecka, vid dos-ändring, vid tillkomst av QT-förlängande 
läkemedel
Kontraindikation: QTc >500 ms

---

[ADR: SERIOUS] Hornhinnedepåer / optisk neuropati
Baseline: Ögonundersökning (synskärpa, slitslampa)
Övervakning: Årlig ögonundersökning, vid synstörning → akut bedömning
Hornhinnedepåer: Vanliga (>90%) men oftast asymtomatiska

---

TIER 3: VANLIGA BIVERKNINGAR (Counseling Points)

[ADR: VERY COMMON] Fotosensitivitet (10-75%)
Hantering: Solskydd (SPF 50+), täckande kläder, undvik stark sol

[ADR: VERY COMMON] Blågrå hudmissfärgning (långtidsbehandling 1-10%)
Hantering: Försvinner långsamt efter utsättning (månader-år)

[ADR: COMMON] GI-besvär (illamående, förstoppning)
Hantering: Ta med mat, dosreduktion vid behov

Källa: janusmed.se - amiodaron, FASS amiodaron SPC, ESC guidelines on antiarrhythmics

VIKTIGT: Amiodaron kräver strukturerad övervakning. Se references/amiodarone-
monitoring-protocol.md för komplett monitoringschema.
```

## Troubleshooting

### Issue: janusmed.se or FASS unavailable

**Solution:**
1. Fall back to European Medicines Agency (EMA) SmPC database
2. Search UpToDate or BMJ Best Practice for adverse effect profiles
3. State clearly: "Primära svenska källor inte tillgängliga. Rekommenderar 
   verifiering i janusmed.se eller FASS när tillgängligt."

### Issue: Frequency data conflicts between sources

**Solution:**
1. Prioritize: janusmed.se > FASS > EMA SmPC > Post-marketing reports
2. If significant discrepancy, state both: "FASS anger [X%], medan post-marketing 
   data tyder på [Y%]. Klinisk erfarenhet stödjer [högre/lägre] frekvens."
3. Always err on side of caution when counseling patients

### Issue: Patient context incomplete

**Solution:**
Follow this triage:
- **If age provided**: Emphasize age-specific ADRs (anticholinergics in elderly, 
  growth effects in pediatrics)
- **If organ dysfunction mentioned**: Filter for that system first
- **If minimal context**: Surface serious ADRs + most common ADRs, then state: 
  "Fullständig riskvärdering kräver mer patientinformation (ålder, njurfunktion, 
  leverfunktion, samsjuklighet)"

### Issue: Drug has multiple indications with different risk profiles

**Example:** Methotrexate (rheumatology vs. oncology dosing)

**Solution:**
1. Ask user to clarify indication and dose if not stated
2. If cannot clarify: provide ADR profile for lowest-risk indication first, 
   note variation
3. Example: "Vid låg-dos MTX (reumatologi): följande ADRs. Vid hög-dos kemoterapi: 
   risk för myelosuppression, mucosit kraftigt förhöjd."

## Critical Rules

1. **Lead with decision-changing information** — serious effects first, never buried
2. **Filter by context** — don't give exhaustive textbook lists; prioritize what matters for THIS patient
3. **Include monitoring parameters** — state WHAT to monitor, WHEN, and action thresholds
4. **Apply proactively** — if patient context suggests organ-system risk, surface ADRs in that system even if not explicitly asked
5. **Cite source** — janusmed.se, FASS with section reference, or guideline
6. **Use Swedish naturally** — Swedish terms for Swedish healthcare context, but be bilingual-ready

## High-Risk Drug Classes Requiring Extra Vigilance

These drug classes have serious ADR profiles requiring structured monitoring—see references for protocols:

- **Antiarytmika** (amiodarone, sotalol, flecainide): multi-organ toxicity, pro-arrhythmic risk
- **Immunosuppressiva** (methotrexate, azathioprine): infection, malignancy, cytopenias
- **Antikoagulantia/antiplatelet**: bleeding risk amplified by polypharmacy
- **Psykofarmaka i äldre** (antipsychotics, benzodiazepines): fall, delirium, mortality
- **Nefrotoxiska** (NSAIDs, aminoglycosides, tenofovir): AKI, CKD progression

## References

For detailed adverse effect management protocols:
- `references/high-risk-drug-monitoring.md` — Structured monitoring schedules for high-risk drugs
- `references/age-specific-adr-risks.md` — Pediatric and geriatric ADR considerations  
- `references/organ-dysfunction-adr-modifications.md` — Renal/hepatic impairment ADR profiles
- `references/swedish-adr-reporting.md` — BiSi (Swedish ADR reporting system) guidelines

Source: janusmed.se, FASS, Läkemedelsverket (Swedish Medical Products Agency), EMA

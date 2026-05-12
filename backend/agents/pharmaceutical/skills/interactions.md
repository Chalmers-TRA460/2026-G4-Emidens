---
name: drug-interactions
description: Identifies drug-drug and drug-condition interactions using Swedish sources (janusmed.se, FASS). Use when prescribing, dosing, or reviewing medications—particularly when user mentions "kombinera", "interaktion", "kan jag ge", "together with", "interactions", or lists multiple drugs. Apply proactively on every prescribing query, even when interactions aren't explicitly asked about.

---

# Drug Interactions Skill

Interactions are one of the highest-yield places to prevent knowledge-based harm. This skill surfaces clinically significant interactions using Swedish sources, primarily janusmed.se, with FASS as secondary reference.

## Instructions

### Step 1: Identify the Query Drug and Context

Extract:
- The medication being queried (generic name preferred)
- Patient's current medication list (if provided)
- Relevant conditions or context (renal impairment, hepatic dysfunction, pregnancy, etc.)

If the current medication list is incomplete, surface the most clinically important class-level interactions.

### Step 2: Search janusmed.se for Interactions

**Primary workflow:**
1. Navigate to https://janusmed.se
2. Search for the queried medication
3. Access the "Interaktioner" (Interactions) section
4. Review for:
   - Kontraindikationer (Contraindications)
   - Kliniskt signifikanta interaktioner (Clinically significant interactions)
   - Övervakningskrävande kombinationer (Combinations requiring monitoring)

**Secondary sources (if janusmed.se is insufficient):**
- FASS (https://www.fass.se) - official Swedish drug information
- Swedish national guidelines (Läkemedelsverket)
- European guidelines (ESC, EMA) when Swedish sources are silent

### Step 3: Categorize by Severity

Use these exact inline labels:

**[INTERACTION: KONTRAINDIKATION]** — combination must not be used. State the alternative.

**[INTERACTION: MAJOR]** — clinically significant; usually requires dose adjustment, alternative, or close monitoring.

**[INTERACTION: MÅTTLIG/MODERATE]** — relevant; monitor for the specific effect described.

**[INTERACTION: MINOR]** — typically managed, but worth noting if the patient is fragile.

### Step 4: Identify Mechanism

State the mechanism category:

**Farmakokinetisk (Pharmacokinetic):**
- CYP450-hämning/induktion (inhibition/induction)
- P-glykoprotein-påverkan
- Njur-/gallvägs-transportörskonkurrens
- Proteinbindningsförskjutning

**Farmakodynamisk (Pharmacodynamic):**
- Additiv effekt (e.g., två QT-förlängare, två serotonerga medel, två antikoagulantia)
- Antagonism
- Synergi

**Farmaceutisk (Pharmaceutical):**
- Fysikalisk inkompatibilitet vid samtidig IV-administrering

### Step 5: Format Output

For each interaction surfaced, provide:

1. **Interagerande läkemedel/klass** (Interacting drug/class)
2. **Svårighetsgrad** (Severity tier with inline tag)
3. **Mekanism** (Mechanism in one sentence)
4. **Klinisk konsekvens** (Clinical consequence in one sentence)
5. **Åtgärd** (Action: stop, switch, dose-adjust, or monitor—and what to monitor)
6. **Källa** (Source: janusmed.se, FASS, guideline reference)

### Step 6: Prioritize High-Risk Patterns

Flag these explicitly (most common preventable-harm patterns in Swedish practice):

- **QT-förlängning** (QT prolongation): additive effects with other QT-prolongers
- **Blödningsrisk** (Bleeding risk): NOAK + NSAID, warfarin combinations
- **Serotonergt syndrom** (Serotonin syndrome): SSRI + tramadol, SSRI + TCA
- **Hyperkalemi** (Hyperkalemia): ACE-hämmare + kaliumsparande diuretika
- **Njurtoxicitet** (Nephrotoxicity): NSAID + ACE-hämmare + diuretika ("triple whammy")

## Examples

### Example 1: Starting NSAID in Patient on Warfarin

**User says:** "Kan jag ge diklofenak till en patient som står på warfarin?"

**Actions:**
1. Search janusmed.se for "diklofenak" → "Interaktioner" section
2. Identify warfarin interaction
3. Surface interaction with severity and mechanism

**Output:**
```
[INTERACTION: MAJOR] Diklofenak + Warfarin

Interagerande läkemedel: Warfarin (och andra K-vitaminantagonister)

Svårighetsgrad: MAJOR

Mekanism: Farmakodynamisk—additiv antikoagulant effekt plus gastrointestinal 
mukosaskada från NSAID ökar blödningsrisken.

Klinisk konsekvens: Kraftigt ökad risk för allvarlig blödning, särskilt 
gastrointestinal blödning.

Åtgärd: Undvik kombination om möjligt. Om nödvändig: använd PPI som 
gastroprotektion, tät INR-kontroll (var 3-5:e dag initialt), använd lägsta 
effektiva NSAID-dos kortast möjliga tid. Överväg paracetamol som alternativ.

Källa: janusmed.se - NSAID interaktioner, FASS diklofenak SPC
```

### Example 2: Multiple Drug Review (Polypharmacy)

**User says:** "Patient takes sertraline, tramadol, and metoprolol. Are there concerns?"

**Actions:**
1. Search janusmed.se for each drug
2. Cross-reference interactions
3. Prioritize by severity

**Output:**
```
[INTERACTION: MAJOR] Sertralin + Tramadol

Mekanism: Farmakodynamisk—båda ökar serotonerg aktivitet.

Klinisk konsekvens: Risk för serotonergt syndrom (agitation, konfusion, takykardi, 
hypertoni, hypertermi, hyperreflexi, kloni, diarré).

Åtgärd: Undvik kombination. Välj alternativt analgetikum (paracetamol, NSAID om 
inga kontraindikationer). Om kombination nödvändig: starta tramadol i lägsta dos, 
intensiv övervakning första veckan, patienten ska känna till varningssymtom.

Källa: janusmed.se - Serotonerga interaktioner, FASS sertralin

---

[INTERACTION: MODERATE] Sertralin + Metoprolol

Mekanism: Farmakokinetisk—sertralin hämmar CYP2D6, vilket minskar metabolism av 
metoprolol (som är CYP2D6-substrat).

Klinisk konsekvens: Ökade plasmanivåer av metoprolol, risk för bradykardi, 
hypotension.

Åtgärd: Ingen dosändring nödvändig initialt, men övervaka puls och blodtryck. 
Överväg dosreduktion av metoprolol om bradykardi (<50 bpm) eller hypotension 
utvecklas.

Källa: janusmed.se - CYP2D6 interaktioner
```

### Example 3: Class-Level Warning (Incomplete Med List)

**User says:** "Starting apixaban 5 mg bid. Interactions?"

**Actions:**
1. Search janusmed.se for "apixaban"
2. Since current meds unknown, surface key class interactions

**Output:**
```
Viktiga interaktioner för apixaban (även om fullständig läkemedelslista saknas):

[INTERACTION: KONTRAINDIKATION] Samtidig behandling med andra antikoagulantia
- Warfarin, dabigatran, rivaroxaban, edoxaban: Additiv antikoagulant effekt → 
  kraftigt ökad blödningsrisk
- Åtgärd: Avsluta tidigare antikoagulantium innan apixaban startas (bridging-
  protokoll kan behövas)

[INTERACTION: MAJOR] Stark CYP3A4/P-gp-hämmare
- Ketokonazol, itrakonazol, ritonavir, klaritromycin: Ökar apixaban-nivåer 
  2-4 gånger
- Åtgärd: Undvik kombination eller reducera apixaban till 2,5 mg bid

[INTERACTION: MAJOR] Stark CYP3A4/P-gp-induktor
- Rifampicin, fenytoin, karbamazepin, johannesört: Minskar apixaban-nivåer ~50%
- Åtgärd: Undvik kombination (behandlingssvikt risk)

[INTERACTION: MAJOR] NSAID/antiplatelet-medel
- Ibuprofen, naproxen, ASA, klopidogrel: Additiv effekt på hemostas
- Åtgärd: Undvik NSAID om möjligt. Om nödvändig ASA 75 mg: acceptabelt med 
  gastroprotektion och noggrann nytta-riskbedömning

Källa: janusmed.se - NOAK interaktioner, FASS apixaban SPC
```

## Troubleshooting

### Issue: janusmed.se is unavailable or search fails

**Solution:**
1. Fall back to FASS: https://www.fass.se
2. Search for the drug's SPC (summary of product characteristics)
3. Navigate to "Interaktioner" section in FASS
4. If both unavailable, state clearly: "Primära svenska källor inte tillgängliga. 
   Rekommenderar verifiering i janusmed.se eller FASS när tillgängligt."

### Issue: Drug has Swedish trade name only

**Solution:**
1. Identify generic (INN) name first
2. Search by generic name in janusmed.se
3. Trade name examples: Trombyl → acetylsalisylsyra, Seloken → metoprolol

### Issue: Conflicting information between sources

**Solution:**
1. Prioritize: janusmed.se > FASS > European guidelines
2. State the conflict explicitly: "Janusmed anger [X], medan FASS anger [Y]. 
   Rekommendation baseras på janusmed som primär svensk källa."
3. When in doubt, err on side of caution (report more conservative recommendation)

### Issue: Patient-specific factors not addressed

**Solution:**
Remind user to consider:
- Renal function (eGFR) — many interactions worsen with renal impairment
- Hepatic function — affects drug metabolism
- Age — elderly more sensitive to interactions
- Genetic factors — CYP2D6/2C19 poor metabolizers have altered interaction profiles

## Critical Rules

1. **List KONTRAINDIKATION and MAJOR interactions first** — never bury life-threatening interactions
2. **Apply proactively** — check interactions on every prescribing query, even when user doesn't ask
3. **Use Swedish terms naturally** — write in Swedish when appropriate for Swedish healthcare context
4. **Cite source for every claim** — janusmed.se, FASS, specific guideline with section reference
5. **When uncertain, verify** — if you cannot find the interaction in janusmed.se/FASS, state that explicitly and recommend clinical pharmacist consultation

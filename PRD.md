# Emidens
## Product Requirements Document

> **TRA460: Digital Health Implementation** | Chalmers University of Technology

> **v1.0 Section Guide:**
> - **[Required]** — Must be substantive for this submission to pass.
> - **[Recommended]** — Optional for v1.0, but strengthens your foundation.
> - **[Expand Later]** — Scaffolding for future iterations. Initial thoughts welcome.

---

### Project Details [Required]

| Field               | Value                                      |
|---------------------|--------------------------------------------|
| **Group**           | TRA460_Group_4                             |
| **Version**         | 1.0                                        |
| **Date**            | 2026-04-15                                 |
| **Clinical Mentor** | [Araz Rawshani, Dr. , University of Gothenburg/ Sahlgrenska]|
| **Group Members**   | [Andrej Kocijan (MPALG), Viggo Trobäck (MPCAS), Ida Thorburn (MPQOM), Victor Zexi He (MD)]      |

---

## 1. Needs Statement [Required]

<!--
  REQUIRED FOR v1.0

  THE CORE OF YOUR PRD.
  Use the Stanford Biodesign format below. Be specific:
  - The verb should describe a function, not a technology.
  - The population should be narrow enough to be actionable.
  - The outcome should be measurable or clearly observable.

  Weak:  "A way to use AI for patients that improves healthcare."
  Strong: "A way to detect early signs of atrial fibrillation
           in post-stroke patients managed in primary care
           that reduces time-to-treatment for recurrent events."
-->

> **A way to** prevent knowledge-based errors at the point of care - including those from unrecognized knowledge gaps - 
> **for** clinicians making direct patient care decisions
> **that** reduces serious adverse events and preventable deaths.

From Spezi tool:
"A way to prevent knowledge-based errors at the point of care - including those from unrecognized knowledge gaps - in clinicians making direct patient care decisions, especially in time-critical situations, in order to reduce serious adverse events and preventable deaths."
---

### 1.1 Clinical Context & Background [Required]

<!--
  REQUIRED FOR v1.0

  Set the stage. What is the clinical problem space?
  - What condition, workflow, or care gap are you addressing?
  - How significant is this problem? (incidence, prevalence, burden)
  - Why does it matter — clinically, economically, or humanly?
-->

### 1.2 Key Clinical Insights [Required]

<!--
  REQUIRED FOR v1.0

  THIS IS THE MOST IMPORTANT SECTION FOR v1.0.
  Synthesize what you learned from your clinical mentor meeting(s).
  - What did you observe or hear?
  - What is the current workflow / status quo?
  - Where are the friction points, inefficiencies, or risks?
  - What surprised you?

  Ground this in specifics. Quotes, scenarios, and concrete
  examples are more valuable than generalizations.
-->

### 1.3 Existing Solutions & Gaps [Required]

<!--
  REQUIRED FOR v1.0

  What solutions or tools exist today for this problem?
  - Clinical tools, apps, devices, workflows
  - Why are they insufficient, inaccessible, or underused?
  - What gap remains that your project could fill?
-->

Existing AI-powered solutions already exist, and this project is a direct offshoot of a Swedish effort to address this specific issue. Major actors in this field include companies such as OpenEvidence, which use knowledge-based RAG systems and general large language models (LLMs) such as Claude or Gemini.

The issues with LLMs are that they lack robust reasoning capabilities, rely on any available information, and may hallucinate—both due to these factors and inherent limitations of attention-based architectures. OpenEvidence addresses many of these issues through its custom RAG system, which enhances both knowledge retrieval and reasoning capabilities.

A major limitation, however, is that these systems are not run locally and are not native to Swedish regulations, which is a requirement for use in a Swedish medical context.

Beyond model capabilities, the Konsult project also focuses on model–clinician interaction. Here, there is a significant gap in deployment readiness: the standard web interface for interaction may not be optimal for clinical use, particularly in time-constrained situations.

### 1.4 Success Metrics [Recommended]

<!--
  RECOMMENDED FOR v1.0

  How will you know your solution actually addresses the need?
  Think about the "that..." clause in your Needs Statement —
  how would you measure or observe that outcome?
-->

Depending on design choices, alternative success metrics may be considered. One such metric is the volume of prompts processed, which can serve as a proxy for usability and adoption.

Another key metric is the frequency of corrections relative to clinicians’ recommendations. This provides a direct measure of alignment with medical judgment and may indicate the system’s potential to reduce erroneous clinical decisions and their associated consequences.

---

## 2. Stakeholders & Users

### 2.1 Primary User(s) [Required]

<!--
   REQUIRED FOR v1.0

  Who will directly use or interact with your solution day-to-day?
  Be specific: "Cardiac nurses in outpatient clinics" not just "nurses."
-->

The ultimate target group comprises all medical professionals in decision-making roles. However, for the purposes of project scoping, the user population is restricted to those accessible to the project and for whom the existing model has been optimized. Specifically, this includes on-call cardiologists within specialized healthcare settings.

### 2.2 Other Stakeholders [Required]

<!--
  REQUIRED FOR v1.0

  Who else is affected by or has influence over this solution?
  Consider: patients, caregivers, administrators, IT departments,
  payers/insurers, regulators, clinical champions, etc.
-->

Patients: Arguably the primary stakeholder, as they are the ultimate beneficiaries or subjects of clinical decision-making.
Students: A secondary stakeholder group, particularly in the context of medical education and training, where such systems may support learning and clinical reasoning development.

### 2.3 User Journey — Current State [Recommended]

<!--
  RECOMMENDED FOR v1.0

  Describe the current care pathway or experience of your primary user.
  A simple narrative walkthrough is fine, e.g.:
  "The patient wakes up, measures their..., calls the clinic to..."
-->

---

## 3. Solution Vision [Required]

<!--
  REQUIRED FOR v1.0

  1-2 paragraphs maximum. This is your "north star," not a feature list.
  - What is the high-level concept?
  - How does it directly address the Needs Statement?
  - What does success look like from the user's perspective?

  Keep it directional. You will refine this throughout the course.
-->

---

## 4. Requirements

### 4.1 Functional Requirements (MoSCoW) [Recommended]

<!--
  RECOMMENDED FOR v1.0

  Categorize what your MVP needs to DO.
  Each requirement should be a clear, testable capability.
  A few items per category is enough for v1.0 — this section
  will grow significantly in later iterations.
-->

**Must Have** — *Non-negotiable for a functioning MVP*
- [e.g., Patient can log daily symptom entries via a mobile interface]
-

**Should Have** — *High value, but the MVP could technically function without these*
- [e.g., Clinician receives a weekly summary report of patient-logged data]
-

**Could Have** — *Nice-to-have if time and resources allow*
- [e.g., Push notification reminders for symptom logging]
-

**Won't Have** — *Explicitly out of scope for this project*
- [e.g., Integration with national EHR systems]
-

### 4.2 Non-Functional Requirements & Constraints [Recommended]

<!--
  RECOMMENDED FOR v1.0

  Consider the "invisible" requirements:
  - Data privacy & security (GDPR, patient data handling)
  - Regulatory considerations (MDR, wellness vs. medical device)
  - Accessibility (WCAG, language/localization)
  - Interoperability standards (FHIR, HL7, openEHR)
  - Performance, offline capability
-->

---

## 5. Technical Direction [Expand Later]

<!--
  EXPAND IN LATER ITERATIONS

  Initial thoughts only. No commitments required yet.
  This section helps your future self (and your AI agent, if using
  Claude Code) understand the technical landscape you are considering.
-->

- **Platform:** [iOS / Android / Web / Cross-platform / TBD]
- **Key Integrations:** [EHR systems, wearables, sensors, APIs, etc.]
- **Candidate Tech Stack:** [SpeziVibe, Swift/Kotlin, React, etc. / TBD]
- **Infrastructure:** [Cloud provider, on-premise, hybrid / TBD]

---

## 6. Open Questions & Risks [Required]

<!--
  REQUIRED FOR v1.0

  Be honest about what you don't know yet. This is a sign of
  rigorous thinking, not weakness.
  - What assumptions are you making that haven't been validated?
  - What could block or derail this project?
  - What do you need to ask your clinical mentor next?
-->

- **[Question/Risk]:** [Your plan to resolve it, and by when]
- **[Question/Risk]:** [Your plan to resolve it, and by when]
-

---

## Changelog [Required]

| Version | Date       | Summary of Changes                                  |
|---------|------------|-----------------------------------------------------|
| 1.0     | 2026-04-15 | Initial draft after first clinical mentor meeting   |
|         |            |                                                     |
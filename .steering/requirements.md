# ER Handover Triage — Hackathon Requirements

**Event:** Build with Gemma — Triage in Light Speed (Kaggle)
**Goal:** Reduce friction in the paramedic → nurse → doctor handover chain for critical ER cases, using Gemma to scribe, structure, extract, and prioritize — with a single evolving patient record as the through-line.

---

## 1. Overview

We are building one continuous pipeline, not three disconnected tools. A shared **SQLite-backed patient record** (minimal FHIR R4 subset) is created at paramedic intake and progressively enriched as it moves through nurse review and doctor triage. The demo's strength is that judges can follow one patient from ambulance to bed and see the same record grow more structured and more useful at every stage.

**Stack:** Gradio (UI + deployment), Gemma (all NLP/reasoning steps), SQLite (persistence).

---

## 2. Personas

| Persona | Tab / View | Primary need |
|---|---|---|
| Paramedic | Intake | Capture observations hands-free, fast, with a photo if relevant |
| ER Nurse | Review | Get a structured picture instantly, know what's changed since last visit, get an ESI recommendation |
| ER Doctor | Execution | See the full patient queue ranked by acuity, assign staff, dictate and code notes |

---

## 3. Core User Stories

### Epic A — Data Foundation (build first, blocks everything else)

**A1. Synthetic patient dataset**
As the dev team, we need 10 synthetic patients seeded in SQLite so every downstream feature has realistic data to demo against.
- Schema: `patients`, `encounters`, `conditions`, `observations`, `allergies` (minimal FHIR R4 subset — text-based codes are fine, real-looking ICD-10 strings are a nice touch)
- Each patient has 2–3 prior `encounters` with associated `conditions` (for lookback) and at least one active/current encounter
- Acuity spread across the 10 patients (mix of high and low urgency) so the doctor queue has something meaningful to rank
- Seed script runs idempotently at app startup (creates tables + seeds only if empty)

**A2. Shared persistence layer**
As the dev team, we need every tab to read/write the same SQLite store so a patient's record stays consistent across paramedic, nurse, and doctor views.
- No long-lived connections held across Gradio callbacks (open/close per call, or `check_same_thread=False`)
- All views re-query SQLite on render rather than relying on in-memory state between callbacks

---

### Epic B — Paramedic Intake

**B1. Voice dictation capture**
As a paramedic, I want to dictate my observations and recommendations instead of typing, so I can hand over a patient without breaking stride.
- Gradio audio input (or Web Speech API) captures speech → transcript
- Raw transcript is written to a new `encounters` row tied to a patient (new or existing) as unstructured text
- *Acceptance:* recording a short spoken note results in a visible raw transcript saved against a patient record

**B2. Photo capture for visible injuries**
As a paramedic, I want to attach a photo of a visible injury during handover, so the nurse has visual context without me describing it verbatim.
- Simple image upload attached to the same encounter
- **PaliGemma** returns a short visual tag (e.g., "laceration, moderate bleeding") — no bounding boxes, just a 3-word tag
- Tag is stored alongside the encounter and can bump a priority flag
- *Acceptance:* uploading a sample injury photo produces a visible tag attached to the patient record

**B3. Handover synthesis into structured MIST grid**
As a nurse, I want the paramedic's messy dictated notes turned into a standard MIST grid instantly, so I don't have to parse chaotic speech under pressure.
- Gemma consumes the raw transcript (+ image tag if present) and outputs structured fields: Mechanism, Injury, Signs, Treatment (plus Chief Complaint, Vitals, Interventions Given)
- Structured output is written back into the encounter record in SQLite
- *Acceptance:* pasting/dictating one of 3 prepared sample paramedic notes produces a correctly structured, color-coded grid within seconds

---

### Epic C — Nurse Review

**C1. Medical entity extraction**
As an ER nurse, I want key medical entities (symptoms, vitals, meds, allergies) pulled out automatically from the structured handover, so I can scan rather than re-read.
- Gemma extracts entities from the encounter's structured MIST data
- Output displayed as a scannable list/table in the nurse tab

**C2. Lookback flagging (2–3 prior visits)**
As an ER nurse, I want to see relevant flags from the patient's last 2–3 visits, so I don't miss a recurring condition or known allergy.
- SQLite query joins the current patient's last 2–3 `encounters`/`conditions`/`allergies`
- Gemma summarizes anything clinically relevant to the current complaint (e.g., repeat presentation, relevant allergy, prior related condition)
- *Acceptance:* a patient with a matching prior condition shows a visible flag; a patient with no relevant history shows a clean "no flags" state

**C3. ESI recommendation with Chain-of-Verification**
As an ER nurse, I want a recommended ESI level (1–5) backed by a visible reasoning check, so I can trust and quickly validate the score under time pressure.
- Step 1: Gemma flags explicit red flags in the current record
- Step 2: Gemma proposes a preliminary ESI score
- Step 3: Gemma critiques its own score against basic guardrails before finalizing
- Final ESI score + resource recommendation (e.g., "requires trauma bay") written to the record
- *Acceptance:* for each of the 10 seeded patients, the tool returns an ESI score and a short rationale that's clinically plausible

---

### Epic D — Doctor Execution

**D1. Prioritized patient queue**
As an ER doctor coming on shift, I want all active patients ranked by acuity, so I know who to see first.
- SQL query: `SELECT ... ORDER BY esi_score` (ascending, ESI 1 = most urgent) across all patients with active encounters
- Displayed as a ranked table/dataframe in the doctor tab, pulling directly from records already scored in Epic C — no new Gemma call required
- *Acceptance:* the 10 seeded patients render in a correctly ordered queue

**D2. Staffing assignment (stretch)**
As an ER doctor, I want to mark which staff member is assigned to each patient, so responsibility is visible at a glance.
- Simple `assigned_to` column + dropdown/checkbox in the queue view
- No Gemma involvement — pure state tracking

**D3. Dictation + coding of doctor notes (stretch)**
As an ER doctor, I want to dictate my assessment and have it structured with relevant codes, so documentation doesn't slow me down.
- Reuses the same transcript → structured-fields Gemma pattern as B3
- Adds a suggested code (ICD-10-style text is fine) alongside the structured note
- Written back into the patient's encounter record

---

### Epic E — Cut Unless Ahead of Schedule

**E1. LASA prescription safety buffer**
As an ER clinician, I want a warning if my entered drug doesn't match the stated condition, so I don't make a fatal medication error under stress.
- Not on the paramedic → nurse → doctor handover path; build only with spare time at the end

---

## 4. Data Schema Summary (SQLite, FHIR R4-lite)

- `patients` — id, name, birthDate, gender
- `encounters` — id, patient_id, status, class, period, raw_transcript, structured_mist (JSON), esi_score, esi_rationale, image_tag
- `conditions` — id, patient_id, code, recorded_date
- `observations` — id, encounter_id, type (HR/BP/RR/SpO2/temp), value
- `allergies` — id, patient_id, substance

## 5. Build Order

1. Epic A — schema + seed script (10 synthetic patients, 2–3 visit lookback each)
2. Gradio skeleton with 3 tabs (Paramedic / Nurse / Doctor), all reading/writing SQLite
3. Epic B — voice + photo intake, MIST synthesis
4. Epic C — entity extraction, lookback flags, ESI + CoV
5. Epic D1 — prioritized queue (pure SQL + display)
6. Epic D2/D3 — staffing + dictation, if time remains
7. Epic E — LASA buffer, only if well ahead of schedule

## 6. Explicitly Out of Scope

- Real STT/vision services (use browser/Gradio-native capture + **PaliGemma** local or API tagging only)
- Bounding-box image analysis
- True FHIR R4 compliance / FHIR server
- Multi-user auth, production-grade concurrency handling
- Persistent storage beyond the demo session

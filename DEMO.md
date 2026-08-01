# Demo Script — ER Handover Triage

Judge-facing walkthrough notes. Goal: show **one patient record** getting progressively more structured and more useful as it moves paramedic → nurse → doctor — that continuity is the pitch, not three separate tools.

---

## 1. Before judges arrive

- [ ] `.env` has a working `GEMINI_API_KEY` (and `GEMMA_API_BASE_URL` if not using the default)
- [ ] `ffmpeg` installed and on `PATH` (`brew install ffmpeg` / `apt-get install ffmpeg`) — Whisper needs it
- [ ] `python app.py` running, reachable at `http://127.0.0.1:7860` (or your deployed URL)
- [ ] Click through the mic **and** camera permission prompts once yourself, on the demo machine, before judges are watching — first click pops a browser dialog
- [ ] Confirm DB is freshly seeded: delete `db/erhub.sqlite3` and restart if you've been testing and want a clean slate (idempotent seed re-populates all 10 patients)

---

## 2. Recommended demo patient: **Yuki Tanaka**

She's the single best patient to walk start-to-finish — one story hits nearly every feature:
- A **repeat, related presentation** (prior anaphylaxis from shellfish) → strong lookback flag
- An **on-file allergy she doesn't have to re-state** during dictation → shows the safety-net merge working
- A **clearly critical case** → dramatic, legible ESI 1 with a full Chain-of-Verification trail

Keep **Grace Odhiambo** on standby to show photo tagging (T7) — her case is a real injury photo (not stock), which lands better than describing an injury verbally. Keep **Robert Kaczmarek** on standby as the LASA check example — his on-file ibuprofen allergy makes for a clean mismatch flag on the Doctor tab.

---

## 3. Paramedic Intake tab

1. Select **Yuki Tanaka** from the patient dropdown.
2. Dictate (or type into the transcript box if mic isn't cooperating):
   > "Patient with facial swelling, hives, difficulty breathing after eating at a restaurant. Given epinephrine and oxygen. BP 92 over 60, heart rate 130, SpO2 90."
3. Click **Generate Handover**.

**Say:** *"That's Whisper transcribing locally — no cloud STT, no API key — and Gemma structuring it into a standard MIST grid in seconds. The paramedic never touches a keyboard."*

**Optional — photo showcase:** switch to Grace Odhiambo, upload the real injury photo from `Images/one.png`, point at the auto-generated tag ("abrasion, moderate") before it even reaches the MIST grid.

---

## 4. Nurse Review tab

1. Select **Yuki Tanaka**, click **Load Patient**.
2. Point at three things in order:
   - **Entity table** — note the "Allergies" column shows *Shellfish* even though this encounter's dictation never re-mentioned it. **Say:** *"That's pulled from her on-file record, not just what was said out loud — a nurse under pressure doesn't have to hope the paramedic remembered to restate it."*
   - **Lookback flags** — her prior anaphylaxis visit surfaces automatically. **Say:** *"The system checked her last 2-3 visits and found this isn't her first time — that's the kind of thing that's easy to miss in a five-minute handover."*
   - **ESI Chain-of-Verification (expanded by default)** — walk through all 3 steps out loud: red flags identified → preliminary score → self-critique → final ESI 1. **Say:** *"This isn't a black-box number — you can see exactly why it landed on a 1, and the model checks its own work before finalizing."*
3. Click **Re-run Assessment** once to show it's deterministic — same inputs, same score, not a random number generator.

---

## 5. Doctor Queue tab

1. Show the ranked queue — Yuki should be at or near the top (ESI 1), correctly ahead of lower-acuity patients.
2. Click **Refresh Queue** to show it's live off the same DB the other two tabs just wrote to.
3. **Staffing:** assign Yuki to a staff member from the dropdown, show the queue update.
4. **Dictation:** switch to Robert Kaczmarek, dictate a short discharge note, click **Structure Note** — show the structured note + suggested code appear.
5. **LASA check** (stretch, if time allows): enter `Metformin` as the drug and `anaphylaxis` as the condition — show the red mismatch warning (Metformin is a diabetes drug, not indicated for anaphylaxis). Optionally follow with `Epinephrine` / `anaphylaxis` to show it correctly clears a valid pairing too — proves it's not just flagging everything. **Say:** *"This one's explicitly out of the core handover flow — a bonus safety check we built with the time we had left. It's checking drug-vs-condition appropriateness, not just an allergy list."*

---

## 6. If something breaks live

- **API is slow/down:** fall back to narrating what *should* happen using this doc's expected outputs — the full 10-patient smoke test (see below) already produced real examples for every patient.
- **Mic doesn't work:** every transcript box is editable — type the sample line instead, nobody will notice.
- **Wrong patient selected:** switching patients now correctly clears the form (this was a real bug we caught and fixed) — re-select and continue.

---

## 7. Full smoke test results (for confidence, not for the live demo)

All 10 seeded patients were run through the complete paramedic → nurse pipeline with 0 failures. Final ESI spread: **1, 1, 2, 2, 2, 3, 4, 4, 5, 5** — a real spread across the full acuity range, not clustered. Lookback flags correctly fired for every patient with a genuinely related prior visit (Ava/migraine, Marcus/chest pain, Diego/DKA, Harold/AFib, Yuki/anaphylaxis, Isabelle/fever, Robert/trauma) and stayed a clean "no flags" for the two with unrelated current complaints (Grace, Samuel) — matching C2's acceptance criteria exactly. All three stretch features (staffing, dictation, LASA) also verified working.

---

## 8. What to say if asked "why Gemma / why this architecture"

- **One shared SQLite record**, not three disconnected tools — every tab re-reads the same DB live, so the demo works no matter which tab a judge clicks first.
- **One Gemma prompt function per reasoning step** (MIST synthesis, entity extraction, lookback, ESI+CoV, dictation) — each independently testable, which is also why we could run a clean 10-patient smoke test before this demo.
- **The ESI Chain-of-Verification stays visible in all 3 steps** — a deliberate choice, not a UI limitation. Trust in a triage tool comes from being able to check its reasoning, not just its output.
- All patient data is **synthetic** — worth saying explicitly if asked, given the domain.

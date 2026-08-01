# Tasks — Executable Work Breakdown

Companion to `requirements.md` and `design.md`. Decomposes the design into discrete, independently executable tasks, grouped into **phases** for clean ordering, sized for parallel work by multiple agents/developers on the same repo. Each task lists its **inputs**, **outputs (what it delivers)**, **dependencies**, and **trace-back** to the user story and design component it implements.

Agents own their task's implementation details — file names, internal structure, and code organization are up to whoever builds it, as long as the deliverable and interface (what the task produces/exposes for downstream tasks to consume) match what's described below.

**Shared-component rule:** some tasks extend the same underlying component (e.g., the database layer, or the nurse reasoning module) as an earlier task. Where that's the case, it's called out explicitly — coordinate with whoever built the earlier piece (or pull latest) before starting, since you'll be adding to their code rather than starting fresh.

**Phase rule:** a phase does not start until its entry criteria (prior phase's exit gate) are met. Within a phase, tasks on separate components run in parallel; tasks extending the same component run in the listed order.

---

## 1. Phases at a Glance

| Phase | Name | Tasks | Can run in parallel within phase? | Exit gate |
|---|---|---|---|---|
| **0** | Bootstrap | T0 | — (single task) | Repo exists, deps installable, environment config documented |
| **1** | Foundation | T1, T2, T3, T4, T5 | Yes — Track A (T1→T2) ‖ Track B (T3→T4); T5 waits on both | App launches, shows 3 empty tabs, seeded DB verified by direct query |
| **2** | Independent Services | T6, T7, T8, T10 | Yes — all 4 fully independent, only need T0 | Each function callable standalone and returns sane output on 1 sample input |
| **3** | Paramedic Flow + Nurse Chain Start | T9, T11 | Yes — separate components, separate story tracks | Paramedic tab demoable end-to-end; lookback summarization tested against a seeded patient |
| **4** | Nurse Flow Completion + Doctor Query | T12, T13, T14 | T12 first (blocks both); T13 ‖ T14 after | Nurse tab demoable end-to-end (MIST → entities → flags → ESI+CoV); queue query returns correct ESI order |
| **5** | Doctor Flow | T15 | — (single task) | Doctor tab shows ranked queue from live DB |
| **6** | Stretch Features | T16, T17, T18 | Yes — independent of each other | Time-boxed; ship whatever's done, cut the rest without blocking Phase 7 |
| **7** | Integration & Demo Prep | T19, T20 | T19 then T20 (sequential) | Full smoke test passes on all 10 seeded patients; demo script ready |

---

## 2. Task Table

| ID | Phase | Task | Deliverable | Depends on | Story trace | Design component trace |
|---|---|---|---|---|---|---|
| **T0** | 0 | Repo scaffold: folder structure, dependency manifest, environment config placeholder (Gemma API key), top-level readme stub | Buildable, empty repo | none | — | §1 (all) |
| **T1** | 1 | Define the database schema: 5 resource types (`patients`, `encounters`, `conditions`, `observations`, `allergies`) per the FHIR-lite spec | Schema definition (SQL or equivalent) | T0 | A1, A2 | §1.1 |
| **T2** | 1 | Build the database access layer: connection handling safe for concurrent Gradio callbacks + CRUD operations used across all tabs | DB access module | T1 | A2 | §1.1 |
| **T3** | 1 | Author synthetic patient content: 10 patients, 2–3 prior visits each, varied acuity, plausible vitals/conditions/allergies | Seed dataset | T1 | A1 | §1.1 |
| **T4** | 1 | Build idempotent startup seeding: inserts T3's data into the DB only if empty | Seed routine | T2, T3 | A1 | §1.1 |
| **T5** | 1 | Build the app skeleton: 3-tab layout (Paramedic / Nurse / Doctor), wired to run seeding once at launch | Running (empty) app | T4 | — | §3.1 |
| **T6** | 2 | Build speech-to-text: local open-source Whisper transcription (`tiny`/`base` model), free, no API key | Transcription function | T0 | B1 | §1.2, §3.5 |
| **T7** | 2 | Build image tagging: vision call that returns a short visual tag for an uploaded photo | Image-tagging function | T0 | B2 | §1.2 |
| **T8** | 2 | Build handover synthesis: raw transcript (+ optional image tag) → structured MIST fields | MIST synthesis function | T0 | B3 | §1.2 |
| **T10** | 2 | Build entity extraction: structured MIST data → extracted symptoms/vitals/meds/allergies | Entity extraction function | T0 | C1 | §1.2 |
| **T9** | 3 | Build the Paramedic tab: patient select, audio capture, transcript display, photo upload, "Generate Handover" action, structured MIST output — integrates T6, T7, T8 with the DB layer | Working Paramedic tab | T5, T6, T7, T8, T2 | B1, B2, B3 | §1.3, §3.2 |
| **T11** | 3 | Build lookback summarization: given a patient's last 2–3 encounters, surface anything clinically relevant to the current complaint | Lookback function + supporting DB query | T2, T10 | C2 | §1.2 |
| **T12** | 4 | Build ESI scoring with Chain-of-Verification: red-flag pass → preliminary score → self-critique → final score + rationale | ESI+CoV function + supporting DB write | T2, T11 | C3 | §1.2 |
| **T13** | 4 | Build the Nurse tab: patient select, MIST summary, entity table, lookback flags, ESI reasoning display — integrates T10, T11, T12 | Working Nurse tab | T5, T10, T11, T12 | C1, C2, C3 | §1.3, §3.3 |
| **T14** | 4 | Build the active-patient queue query: all patients with active encounters, ranked by ESI score | Queue query | T2, T12 | D1 | §1.1 |
| **T15** | 5 | Build the Doctor tab: ranked queue display with refresh — integrates T14 | Working Doctor tab | T5, T14 | D1 | §1.3, §3.4 |
| **T16** | 6 *(stretch)* | Add staffing assignment: track which staff member is assigned per patient, editable from the queue view | Staffing assignment feature | T15 | D2 | §1.1, §3.4 |
| **T17** | 6 *(stretch)* | Build doctor dictation: reuse T6's transcription, add note structuring + suggested code, wire into the Doctor tab | Dictation + coding feature | T6, T15 | D3 | §1.2, §3.4 |
| **T18** | 6 *(cut candidate)* | Build the LASA safety check: compare an entered drug against the stated condition, flag mismatches | Standalone LASA check | T5 | E1 | §2 (E1) |
| **T19** | 7 | Integration pass: assemble all tabs, end-to-end smoke test across all 10 seeded patients, fix cross-tab data consistency issues | Fully integrated app | T9, T13, T15 | all | §4 (data flow) |
| **T20** | 7 | Demo script + judge-facing walkthrough notes (which patient to use, what to say at each tab) | Demo script | T19 | all | — |

---

## 3. Parallelization Guide (within-phase tracks)

Tasks that don't extend the same component and have no dependency edge between them can be run concurrently by different agents, as long as they're in the same phase (or the current phase's prerequisites are already met).

- **Phase 1 tracks:** Track A (T1→T2) ‖ Track B (T3→T4) — fully independent of each other; T5 is the phase's join point and waits on both.
- **Phase 2 tracks:** T6, T7, T8, T10 — four fully independent single-function tasks, each only needing T0. Ideal phase for maximum agent parallelism (up to 4 agents, zero coordination needed).
- **Phase 3 tracks:** T9 (needs all of Phase 2's T6/T7/T8 plus Phase 1's T2/T5) ‖ T11 (needs only T2 + T10) — two agents, separate components, no conflict.
- **Phase 4:** T12 must land first (it extends the same nurse-reasoning component as T11, and gates both T13 and T14). Once T12 is committed, T13 and T14 can run in parallel — different components (Nurse tab UI vs. DB query), though both depend on the DB layer, so pull latest before starting either.
- **Phase 5, 6, 7:** see phase table above; Phase 6 tasks (T16, T17, T18) are the natural place to add/drop agents depending on remaining time.

**Shared-component warning:** the database layer (from T2) is extended by T11, T12, T14, T16, T17 across multiple phases, and the nurse reasoning module (from T10) is extended by T11 and T12. Treat these as **serialization points** within any phase where more than one of their extending tasks appears: agents should pull latest before editing and add new functionality rather than modifying existing logic where possible. Consider one agent "owning" the database layer and taking small patches from others rather than multiple agents editing it simultaneously.

---

## 4. Dependency Graph (annotated by phase)

```
Phase 0                Phase 1                              Phase 2
────────                ─────────────────────────────────    ─────────────────────
T0 (scaffold)
├─► T1 (schema)
│   ├─► T2 (DB access layer) ─────────────────────────────────┐
│   │                                                          │
│   └─► T3 (seed data) ──────► T4 (seed routine) ─► T5 (app skeleton)
│                                                    │          │
├─► T6 (speech-to-text) ─────────────────────────────┼────────────────┤  Phase 2:
├─► T7 (image tagging) ───────────────────────────────┼────────────────┤  T6,T7,T8,T10
├─► T8 (MIST synthesis) ────────────────────────────────┼────────────────┤  all independent,
├─► T10 (entity extraction) ──────────────────────────────┼────────────────┘  only need T0
│                                                        │
│              Phase 3                                  ▼
│              ──────────                     T9 (Paramedic tab) ◄── T6,T7,T8,T2,T5
│
│              T2,T10 ─► T11 (lookback summarization)
│
│              Phase 4
│              ──────────
│              T11 ─► T12 (ESI+CoV) ──┬─► T13 (Nurse tab, needs T5,T10,T11,T12)
│                                     └─► T14 (queue query, needs T2,T12)
│
│              Phase 5
│              ──────────
│              T14 ─► T15 (Doctor tab, needs T5)
│
│              Phase 6 (stretch, parallel, time-boxed)
│              ──────────
│              T15 ─► T16 (staffing)
│              T6,T15 ─► T17 (dictation)
│              T5 ─► T18 (LASA, cut candidate)
│
▼              Phase 7
T9,T13,T15 ──► T19 (integration) ─► T20 (demo script)
```

**Phase transition rule:** don't start a phase's tasks until every task in the previous phase that they depend on is merged — not just "in progress." This is what keeps the phases as clean gates rather than a loose suggestion.

**Critical path** (longest dependency chain, determines minimum build time regardless of team size):
`T0 → T1 → T2 → T11 → T12 → T13 → T19 → T20` — spans Phases 0, 1, 2 (T10 prerequisite), 3, 4, 7.
*(the nurse reasoning chain is the longest — prioritize starting T10 the moment Phase 2 opens, and don't let one agent get blocked waiting on others for this track)*

---

## 5. Definition of Done (per task)

Applies on top of the story-level DoD in `design.md` §6:
1. Deliverable runs/is callable standalone, without needing the full app running, wherever that's feasible (e.g., a reasoning function can be tested with a script before it's wired into a tab).
2. No modification to another task's component without flagging it to whoever built it first — see the shared-component warning in §3.
3. Committed with a message referencing the task ID (e.g., `T12: add ESI scoring with Chain-of-Verification`) so traceability holds through git history.
4. If a task extends a shared component (DB layer, nurse reasoning module, app skeleton), pull latest immediately before starting to avoid stale-state conflicts.

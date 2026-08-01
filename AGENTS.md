# AGENTS.md

Context file for any AI coding agent (or human) working in this repository. Read this before making changes. Planning docs live under `.steering/`: `.steering/requirements.md` (user stories), `.steering/design.md` (component breakdown + UI layout), `.steering/tasks.md` (executable tasks, phases, dependency graph). Check `.steering/` for the current state of these documents before starting any task — they're the source of truth for scope and sequencing.

---

## 1. Project Overview

**What this is:** A half-day hackathon build for the Kaggle "Build with Gemma: Triage in Light Speed" competition. A Gradio web app that reduces friction in the ER handover chain — paramedic → nurse → doctor — for critical patients, using Gemma for scribing, structuring, extraction, and clinical reasoning.

**Core idea:** One patient record, progressively enriched across three tabs:
1. **Paramedic tab** — dictate/photograph observations → Gemma structures into a MIST handover grid.
2. **Nurse tab** — Gemma extracts entities, flags relevant history from the last 2–3 visits, recommends an ESI acuity score with visible chain-of-verification reasoning.
3. **Doctor tab** — patients ranked by ESI in a live queue; optional staffing assignment and dictated notes.

**Why this matters for how you build:** the demo's value is the *continuity* of one record across three views, not three separate tools. Always ask "does this change keep the record consistent across tabs?" before merging.

---

## 2. Tech Stack

- **UI + deployment:** Gradio (`Blocks` + `Tabs`), single-page, served over HTTP(S) in a normal browser
- **Persistence:** SQLite — single file, no external DB server
- **LLM reasoning:** Gemma (for text tasks) and **PaliGemma** (for image analysis/vision tasks, via whatever API/local inference path the team has configured — check `.env`/environment config before assuming)
- **Speech-to-text:** local open-source Whisper (`tiny`/`base` model) — free, no API key, loaded once at startup
- **Language:** Python throughout

---

## 3. Setup & Run

```bash
pip install -r requirements.txt
# copy .env.example to .env and fill in the Gemma API key/endpoint if required
python app.py
```

The app seeds SQLite with 10 synthetic patients on first run (idempotent — safe to restart). If the app won't start, check the DB file isn't locked by another process and that the schema has been applied.

---

## 4. Data & Domain Constraints — read before touching anything patient-related

- **All patient data is synthetic.** Never introduce real patient information, real names, or real medical records — including from personal experience, example datasets found online, or "realistic-looking" data scraped from elsewhere. Fabricated-but-plausible data only.
- **Schema is a minimal FHIR R4 subset** (`patients`, `encounters`, `conditions`, `observations`, `allergies`) — don't add full FHIR compliance machinery; keep it minimal and demo-appropriate.
- **This is a hackathon demo, not a clinical tool.** ESI scores, LASA warnings, and any other clinical output are illustrative only. Don't add language to the UI implying these are validated for real clinical use, and don't optimize prompts to sound more clinically authoritative than the underlying reasoning supports.
- **Lookback window is fixed at 2–3 prior visits** — don't expand scope to full history; it's an intentional scope cut for the time box.

---

## 5. Architecture Conventions

- **One shared SQLite store, read fresh on every tab load.** Don't pass patient state between tabs via in-memory Python variables or Gradio session state — every tab should re-query the DB so the three personas' views stay consistent by construction.
- **One Gemma prompt function per distinct reasoning task** (MIST synthesis, entity extraction, lookback summarization, ESI+CoV scoring, dictation structuring). Keep these as standalone, independently testable functions — don't collapse multiple reasoning steps into one giant prompt, even if it seems more efficient. Testability and demo narratability both depend on this separation.
- **The ESI Chain-of-Verification must stay visible in its 3 steps** (red flags → preliminary score → self-critique → final score) in both the function output and the UI. Don't collapse it to just a final number — the visible reasoning trail is a deliberate design choice, not an implementation detail.
- **Speech-to-text is a separate, reusable function**, not embedded inside each tab's callback — both the paramedic and doctor dictation flows call the same transcription function.

See `.steering/design.md` §3 for full UI layout per tab and `.steering/design.md` §3.5 for browser-specific constraints (HTTPS required for mic access, webcam fallback to file upload, etc.).

---

## 6. Task Workflow (multi-agent coordination)

This repo is built using the phased task breakdown in `.steering/tasks.md`. Before starting work:

1. **Check which phase is currently open.** Don't start a task whose dependencies (per `.steering/tasks.md` §2 and §4) haven't been merged yet — "in progress" doesn't count as done.
2. **Check the shared-component warning in `.steering/tasks.md` §3** before editing the database layer or the nurse reasoning module — these are extended by multiple tasks across phases; pull latest first and add new functionality rather than restructuring existing logic.
3. **File names and internal structure are yours to decide** — tasks specify deliverables and interfaces, not file layouts. Keep names predictable and consistent with whatever pattern the rest of the repo has already established, rather than introducing a new convention per task.
4. **Reference the task ID in commit messages** (e.g., `T12: add ESI scoring with Chain-of-Verification`) so progress is traceable against `.steering/tasks.md`.

---

## 7. Code Style

- Prefer small, single-purpose functions over large ones — this mirrors the task decomposition and keeps each piece independently testable ahead of full integration.
- Prompt strings for Gemma calls should live in one obvious place per function (not scattered/duplicated) so they're easy to tune quickly during the hackathon.
- Favor clarity over cleverness — this is a half-day build multiple people/agents will touch; optimize for someone else being able to read and extend your code in five minutes, not for elegance.
- No dead code or commented-out experiments left in merged work — delete or don't commit.

---

## 8. Testing Expectations

Given the time box, formal test suites are out of scope. Instead:
- Every reasoning function should be runnable standalone against at least one sample input before being wired into a tab (see `.steering/tasks.md` §5, Definition of Done #1).
- Before the Phase 7 integration pass, every tab should be manually exercised against at least 2 of the 10 seeded patients.
- The Phase 7 exit gate requires a full smoke test across **all 10** seeded patients — don't skip stretch-feature patients or edge-case acuity levels.

---

## 9. What Not to Do

- Don't add authentication, multi-user session handling, or role-based access — out of scope per `.steering/requirements.md` §6.
- Don't build real STT/vision services beyond what's specified (open-source Whisper for STT, **PaliGemma** for simple 3-word image tags) — no bounding boxes, no cloud vision APIs.
- Don't pursue full FHIR R4 compliance or a real FHIR server.
- Don't scope-creep into the LASA safety buffer (E1) or staffing/dictation stretch features (T16/T17) before the core three-tab flow (Phases 0–5) is fully working end to end.
- Don't hold a long-lived SQLite connection across Gradio callback invocations — open/close per call, or guard with `check_same_thread=False`, to avoid "database is locked" errors under concurrent demo usage.

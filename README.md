---
title: Lighteninghub App
emoji: ⚡
colorFrom: blue
colorTo: indigo
sdk: gradio
sdk_version: 4.44.0
app_file: app.py
pinned: false
short_description: ER Handover Triage continuous patient record powered by Gemma
---

# 🚑 ER Handover Triage — Gemma Lightning Hub (Healthcare Track)

**Build with Gemma Competition — Triage in Light Speed (Kaggle Hackathon)**

Reducing friction in the Emergency Room handover chain (**Paramedic ➔ Nurse ➔ Doctor**) for critical patients using Gemma for scribing, structuring, lookback audit, ESI triage, and clinical coding — with a single continuous patient record.

---

## 🌟 Key Features

1. **Paramedic Intake View:** Hands-free dictation + photo capture of injuries ➔ structured into a standard **MIST Grid** (Mechanism, Injury, Signs, Treatment) with visual tags.
2. **Nurse Review View:** Automated medical entity extraction, 2–3 visit historical lookback audit, and **ESI Level 1–5 scoring with Chain-of-Verification (CoV)**.
3. **Doctor Execution View:** **Live prioritized patient queue** ranked by acuity, healthcare staffing assignment, dictation structuring, and **ICD-10 clinical coding**.

---

## 📚 Documentation & Demo Guides

*   **Architecture & Presentation Pitch Design:** [`PRESENTATION_DESIGN.md`](file:///Users/moz/projects/spur-gemma-hackathon/Build-With-Gemma-Lightning-Hub/PRESENTATION_DESIGN.md) *(Includes Mermaid system architecture, sequence diagrams, ER diagrams, and 3-minute pitch deck structure)*
*   **Sample Paramedic Handover Notes & Images:** [`SAMPLE_HANDOVER_NOTES.md`](file:///Users/moz/projects/spur-gemma-hackathon/Build-With-Gemma-Lightning-Hub/SAMPLE_HANDOVER_NOTES.md) *(5 copy-pasteable clinical notes paired 1-to-1 with photos)*
*   **Sample Doctor Notes & Coding:** [`SAMPLE_DOCTOR_NOTES.md`](file:///Users/moz/projects/spur-gemma-hackathon/Build-With-Gemma-Lightning-Hub/SAMPLE_DOCTOR_NOTES.md) *(5 bedside dictation notes for ICD-10 coding demo)*

---

## 🚀 Quickstart & Setup

### 1. Requirements
* Python 3.10+
* Google AI Studio API Key (or Gemini API Key)

### 2. Environment Configuration
Create a `.env` file in the root directory:
```bash
GEMMA_API_KEY="your_api_key_here"
GEMMA_MODEL="gemini-flash-latest"
```

### 3. Install & Launch
```bash
# Install dependencies
uv venv
source .venv/bin/activate
pip install -r requirements.txt

# Run the Gradio Web App
python app.py
```

Open `http://localhost:7860` in your web browser.

---

## 📐 System Architecture Overview

```
[Paramedic Tab] ──► Speech STT + Photo Tagging ──► MIST Synthesis ──► SQLite (FHIR-lite)
                                                                            │
[Nurse Tab]     ──► Entity Extraction + Lookback Audit ──► ESI CoV Scoring ──┤
                                                                            │
[Doctor Tab]    ──► Priority Queue ──► Bedside Dictation ──► ICD-10 Coding ──┘
```

See [`PRESENTATION_DESIGN.md`](file:///Users/moz/projects/spur-gemma-hackathon/Build-With-Gemma-Lightning-Hub/PRESENTATION_DESIGN.md) for full interactive Mermaid sequence and component diagrams.

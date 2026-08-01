"""T15: Doctor Queue tab (design.md §3.4), plus Phase 6 stretch features:
T16 (staffing assignment), T17 (dictation + coding), T18 (LASA check).

T15's queue is pure read + refresh, no Gemma call. T17 reuses T6
(transcribe_speech) and adds structure_dictation(). T18 is a standalone,
stateless check with no patient/DB linkage.
"""
import json
from datetime import datetime

import gradio as gr

from db import db
from services.gemma_doctor import structure_dictation
from services.lasa import check_lasa
from services.stt import transcribe_speech

QUEUE_HEADERS = ["ESI", "Patient", "Chief Complaint", "Wait Time", "Assigned To"]
STAFF_OPTIONS = ["Dr. Chen", "Dr. Patel", "Dr. Okafor", "Nurse Ramirez", "Nurse Coleman", "Unassigned"]


def _wait_time(period_start_iso):
    """Seed data writes naive local wall-clock timestamps (e.g. "patient
    arrived at 9am", no timezone intent). Live intake (ui/paramedic.py)
    writes real UTC-aware timestamps. Normalize both to naive local time
    before diffing against local now() — treating a naive seed timestamp
    as UTC would skew every seeded patient's wait time by the system's
    UTC offset."""
    started = datetime.fromisoformat(period_start_iso)
    if started.tzinfo is not None:
        started = started.astimezone().replace(tzinfo=None)
    minutes = int((datetime.now() - started).total_seconds() // 60)
    if minutes < 0:
        minutes = 0
    if minutes < 60:
        return f"{minutes} min"
    return f"{minutes // 60}h {minutes % 60}m"


def _chief_complaint(structured_mist_json):
    if not structured_mist_json:
        return "Not yet triaged"
    try:
        return json.loads(structured_mist_json).get("chief_complaint", "Not yet triaged")
    except (TypeError, ValueError):
        return "Not yet triaged"


def _queue_rows():
    rows = []
    for enc in db.get_active_queue():
        esi = enc["esi_score"] if enc["esi_score"] is not None else "Pending"
        rows.append([
            esi,
            enc["patient_name"],
            _chief_complaint(enc["structured_mist"]),
            _wait_time(enc["period_start"]),
            enc["assigned_to"] or "Unassigned",
        ])
    return rows


def refresh_queue():
    return _queue_rows()


def _encounter_choices():
    return [
        (f"{e['patient_name']} (#{e['patient_id']})", e["id"])
        for e in db.list_active_encounters()
    ]


def refresh_doctor_tab():
    """Wired to the Doctor tab's `select` event (app.py) — re-queries the
    queue and both encounter dropdowns, same staleness fix as the other
    two tabs (see ui/paramedic.py's refresh_patient_dropdown)."""
    choices_update = gr.update(choices=_encounter_choices())
    return _queue_rows(), choices_update, choices_update


# ---- T16: staffing assignment (D2) ----

def _assign_staff(encounter_id, staff_name):
    if encounter_id is None:
        raise gr.Error("Select a patient first.")
    db.assign_staff(encounter_id, staff_name)
    return _queue_rows()


# ---- T17: doctor dictation + coding (D3) ----

def _on_dictation_audio(audio_path):
    if not audio_path:
        return gr.update()
    try:
        return transcribe_speech(audio_path)
    except Exception as e:
        raise gr.Error(f"Transcription failed: {e}")


def _on_dictation_patient_select(_encounter_id):
    """Clears any leftover transcript/note from a previous patient —
    without this, switching patients here and clicking "Structure Note"
    without re-dictating would save the previous patient's note into the
    newly selected patient's encounter record. Wired to `.select()`, not
    `.change()`, so it only fires on a genuine user pick (see
    ui/paramedic.py's _on_patient_select for why that distinction matters)."""
    return None, "", ""


def _structure_note(encounter_id, transcript):
    if encounter_id is None:
        raise gr.Error("Select a patient first.")
    if not transcript or not transcript.strip():
        raise gr.Error("Record or enter a dictation before structuring.")
    result = structure_dictation(transcript)
    db.update_encounter_note(encounter_id, result["structured_note"], result["suggested_code"])
    note_html = (
        f'<p><strong>Structured Note:</strong><br>{result["structured_note"]}</p>'
        f'<p><strong>Suggested Code:</strong> {result["suggested_code"]}</p>'
    )
    return note_html


# ---- T18: LASA safety check (E1, standalone) ----

def _run_lasa_check(drug, condition):
    if not drug or not condition:
        raise gr.Error("Enter both a drug and a condition.")
    result = check_lasa(drug, condition)
    color = "#fca5a5" if result["mismatch"] else "#bbf7d0"
    label = "⚠️ Possible mismatch" if result["mismatch"] else "✅ No mismatch found"
    return (
        f'<div style="background:{color};padding:10px;border-radius:6px;">'
        f'<strong>{label}</strong><br>{result["explanation"]}'
        f"</div>"
    )


def doctor_tab():
    with gr.Column() as tab:
        gr.Markdown("## Doctor Queue")
        refresh_btn = gr.Button("Refresh Queue", variant="primary")
        queue_df = gr.Dataframe(
            headers=QUEUE_HEADERS,
            datatype=["str", "str", "str", "str", "str"],
            value=_queue_rows(),
        )
        refresh_btn.click(refresh_queue, outputs=queue_df)

        gr.Markdown("### Staffing Assignment")
        with gr.Row():
            staff_patient_dropdown = gr.Dropdown(choices=_encounter_choices(), label="Patient")
            staff_dropdown = gr.Dropdown(choices=STAFF_OPTIONS, label="Assign to")
            assign_btn = gr.Button("Assign")
        assign_btn.click(
            _assign_staff, inputs=[staff_patient_dropdown, staff_dropdown], outputs=queue_df
        )

        gr.Markdown("### Doctor Dictation")
        with gr.Row():
            with gr.Column():
                dictation_patient_dropdown = gr.Dropdown(choices=_encounter_choices(), label="Patient")
                dictation_audio = gr.Audio(sources=["microphone", "upload"], type="filepath", label="Dictate assessment")
                dictation_transcript = gr.Textbox(label="Transcript (editable)", lines=3)
                dictation_audio.change(_on_dictation_audio, inputs=dictation_audio, outputs=dictation_transcript)
                structure_btn = gr.Button("Structure Note")
            with gr.Column():
                note_out = gr.HTML(label="Structured note + suggested code")
        dictation_patient_dropdown.select(
            _on_dictation_patient_select,
            inputs=dictation_patient_dropdown,
            outputs=[dictation_audio, dictation_transcript, note_out],
        )
        structure_btn.click(
            _structure_note,
            inputs=[dictation_patient_dropdown, dictation_transcript],
            outputs=note_out,
        )

        gr.Markdown("### LASA Safety Check _(illustrative only — not for real clinical use)_")
        with gr.Row():
            lasa_drug = gr.Textbox(label="Drug entered")
            lasa_condition = gr.Textbox(label="Patient condition")
            lasa_btn = gr.Button("Check")
        lasa_out = gr.HTML()
        lasa_btn.click(_run_lasa_check, inputs=[lasa_drug, lasa_condition], outputs=lasa_out)

    return tab, queue_df, staff_patient_dropdown, dictation_patient_dropdown

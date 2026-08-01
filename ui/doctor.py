"""T15: Doctor Queue tab (design.md §3.4), plus Phase 6 stretch features:
T16 (staffing assignment), T17 (dictation + coding), T18 (LASA check).

T15's queue is pure read + refresh, no Gemma call. T17 reuses T6
(transcribe_speech) and adds structure_dictation(). T18 is a standalone,
stateless check with no patient/DB linkage — its condition field is
pre-filled from the selected patient's chief complaint but stays editable.

All three action panels (staffing/dictation/LASA) stay hidden until a row
with a valid (non-Pending) ESI score is selected in the queue table — a
patient hasn't been triaged yet if esi_score is NULL, and there's nothing
actionable to attach staffing/dictation/a safety check to until they have.
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

NO_SELECTION_MESSAGE = "_Select a **triaged** patient (with an ESI score) from the queue above to take action._"


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


def _esi_display(enc):
    """The effective score (nurse override if present, else the AI's),
    marked so a doctor scanning the queue can tell at a glance which
    numbers reflect nurse judgment rather than raw AI output — without
    having to open every patient to find out."""
    if enc["esi_score"] is None:
        return "Pending"
    if enc.get("esi_override_score") is not None:
        return f"{enc['esi_override_score']} ⚠️ Overridden"
    return enc["esi_score"]


def _queue_data():
    """Single DB query, returns (raw encounter list, display rows) in the
    same order — the raw list backs a gr.State so a Dataframe row click can
    be resolved back to a real encounter_id/esi_score, not just display
    strings."""
    encounters = db.get_active_queue()
    rows = [
        [
            _esi_display(enc),
            enc["patient_name"],
            _chief_complaint(enc["structured_mist"]),
            _wait_time(enc["period_start"]),
            enc["assigned_to"] or "Unassigned",
        ]
        for enc in encounters
    ]
    return encounters, rows


def _override_info_markdown(enc):
    if enc.get("esi_override_score") is None:
        return "_No nurse override on this case — ESI reflects the AI's assessment as-is._"
    return (
        "**⚠️ Nurse Override**\n\n"
        f"AI recommended: ESI {enc['esi_score']}\n\n"
        f"Overridden to: ESI {enc['esi_override_score']}\n\n"
        f"Justification: {enc['esi_override_reason']}"
    )


def refresh_queue():
    """Re-queries the queue and clears any active row selection — row
    indices may no longer point at the same patients after a refresh, so
    keeping a stale selection open risks acting on the wrong patient."""
    encounters, rows = _queue_data()
    return rows, encounters, gr.update(visible=False), NO_SELECTION_MESSAGE, None, ""


def _on_queue_select(evt: gr.SelectData, encounters):
    """Gates all three action panels behind a valid ESI score. Also clears
    any leftover dictation/note/LASA fields from whichever patient was
    selected before — without this, switching the selected row and
    clicking "Structure Note" without re-dictating would save the
    previous patient's note into the newly selected patient's record
    (same class of bug fixed earlier for the paramedic/dictation patient
    dropdowns, which this replaces)."""
    row_idx = evt.index[0] if isinstance(evt.index, (list, tuple)) else evt.index
    if not encounters or row_idx is None or row_idx >= len(encounters):
        return gr.update(visible=False), NO_SELECTION_MESSAGE, None, "", None, "", "", "", "", ""

    enc = encounters[row_idx]
    if enc["esi_score"] is None:
        message = (
            f"⚠️ **{enc['patient_name']}** hasn't been triaged yet — no ESI score. "
            "Select a triaged patient to take action."
        )
        return gr.update(visible=False), message, None, "", None, "", "", "", "", ""

    header = f"**Selected:** P{enc['patient_id']:03d} - {enc['patient_name']} (ESI {enc['esi_score']})"
    chief_complaint = _chief_complaint(enc["structured_mist"])
    return (
        gr.update(visible=True), header, enc["encounter_id"], _override_info_markdown(enc),
        None, "", "", "", chief_complaint, "",
    )


# ---- T16: staffing assignment (D2) ----

def _assign_staff(encounter_id, staff_name):
    if encounter_id is None:
        raise gr.Error("Select a triaged patient first.")
    db.assign_staff(encounter_id, staff_name)
    encounters, rows = _queue_data()
    return rows, encounters


# ---- T17: doctor dictation + coding (D3) ----

def _on_dictation_audio(audio_path):
    if not audio_path:
        return gr.update()
    try:
        return transcribe_speech(audio_path)
    except Exception as e:
        raise gr.Error(f"Transcription failed: {e}")


def _structure_note(encounter_id, transcript):
    if encounter_id is None:
        raise gr.Error("Select a triaged patient first.")
    if not transcript or not transcript.strip():
        raise gr.Error("Record or enter a dictation before structuring.")
    result = structure_dictation(transcript)
    db.update_encounter_note(encounter_id, result["structured_note"], result["suggested_code"])
    note_html = (
        f'<p><strong>Structured Note:</strong><br>{result["structured_note"]}</p>'
        f'<p><strong>Suggested Code:</strong> {result["suggested_code"]}</p>'
    )
    return note_html


# ---- T18: LASA safety check (E1) ----

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
        gr.Markdown('<span class="section-header">👨‍⚕️ Doctor Queue</span>')
        refresh_btn = gr.Button("🔄 Refresh Queue", variant="primary")

        encounters, rows = _queue_data()
        queue_state = gr.State(encounters)
        queue_df = gr.Dataframe(
            headers=QUEUE_HEADERS,
            datatype=["str", "str", "str", "str", "str"],
            value=rows,
        )

        selected_encounter_state = gr.State(None)
        with gr.Column(elem_classes=["section-box"]):
            selection_header = gr.Markdown(NO_SELECTION_MESSAGE)

        with gr.Group(visible=False, elem_classes=["transparent-wrapper"]) as action_group:
            with gr.Column(elem_classes=["section-box"]):
                gr.Markdown('<span class="section-header">⚠️ Nurse Override Status</span>')
                override_info_out = gr.Markdown()

            with gr.Column(elem_classes=["section-box"]):
                gr.Markdown('<span class="section-header">🧑‍⚕️ Staffing Assignment</span>')
                with gr.Row():
                    staff_dropdown = gr.Dropdown(choices=STAFF_OPTIONS, label="Assign to")
                    assign_btn = gr.Button("Assign", variant="primary")

            with gr.Column(elem_classes=["section-box"]):
                gr.Markdown('<span class="section-header">🎙️ Doctor Dictation</span>')
                with gr.Row():
                    with gr.Column():
                        dictation_audio = gr.Audio(sources=["microphone", "upload"], type="filepath", label="Dictate assessment")
                        dictation_transcript = gr.Textbox(label="Transcript (editable)", lines=3)
                        dictation_audio.change(_on_dictation_audio, inputs=dictation_audio, outputs=dictation_transcript)
                        structure_btn = gr.Button("Structure Note", variant="primary")
                    with gr.Column():
                        note_out = gr.HTML(label="Structured note + suggested code")

            with gr.Column(elem_classes=["section-box"]):
                gr.Markdown('<span class="section-header">💊 LASA Safety Check</span> _(illustrative only — not for real clinical use)_')
                with gr.Row():
                    lasa_drug = gr.Textbox(label="Drug entered")
                    lasa_condition = gr.Textbox(label="Patient condition (auto-filled from chief complaint, editable)")
                    lasa_btn = gr.Button("Check", variant="primary")
                lasa_out = gr.HTML()

        queue_df.select(
            _on_queue_select,
            inputs=[queue_state],
            outputs=[
                action_group, selection_header, selected_encounter_state, override_info_out,
                dictation_audio, dictation_transcript, note_out,
                lasa_drug, lasa_condition, lasa_out,
            ],
        )

        refresh_btn.click(
            refresh_queue,
            outputs=[
                queue_df, queue_state, action_group, selection_header,
                selected_encounter_state, override_info_out,
            ],
        )

        assign_btn.click(
            _assign_staff, inputs=[selected_encounter_state, staff_dropdown], outputs=[queue_df, queue_state]
        )

        structure_btn.click(
            _structure_note, inputs=[selected_encounter_state, dictation_transcript], outputs=note_out
        )

        lasa_btn.click(_run_lasa_check, inputs=[lasa_drug, lasa_condition], outputs=lasa_out)

    return (
        tab, queue_df, queue_state, action_group,
        selection_header, selected_encounter_state, override_info_out,
    )

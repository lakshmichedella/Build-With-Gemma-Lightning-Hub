"""T9: Paramedic Intake tab (design.md §3.2).

Integrates T6 (transcribe_speech), T7 (tag_image), T8 (synthesize_mist)
with the DB layer (T2). Patient select, audio capture, transcript display,
photo upload, "Generate Handover" action, structured MIST output.
"""
import json
from datetime import datetime, timezone

import gradio as gr

from db import db
from services.gemma_intake import synthesize_mist
from services.gemma_vision import tag_image
from services.stt import transcribe_speech

NEW_PATIENT_VALUE = "__new__"

FIELD_COLORS = {
    "chief_complaint": "#fde68a",
    "mechanism": "#bfdbfe",
    "injury": "#fecaca",
    "signs": "#fed7aa",
    "treatment": "#bbf7d0",
    "vitals": "#e9d5ff",
    "interventions_given": "#a5f3fc",
    "allergies": "#fca5a5",
}


def _patient_choices():
    choices = [(f"P{p['id']:03d} - {p['name']}", p["id"]) for p in db.list_patients()]
    choices.append(("+ New Patient", NEW_PATIENT_VALUE))
    return choices


def refresh_patient_dropdown():
    """Re-queries the DB for current patients. Wired to this tab's `select`
    event in app.py so switching to this tab always shows patients created
    elsewhere (e.g. via the Nurse tab), per AGENTS.md's "read fresh on every
    tab load" rule — a plain `choices=` kwarg only evaluates once, at
    app-build time."""
    return gr.update(choices=_patient_choices())


def _on_patient_select(patient_choice):
    """Also clears the audio/transcript/photo/tag/MIST fields — without
    this, switching patients leaves the previous patient's dictation and
    photo tag sitting in the form, and clicking "Generate Handover" would
    write them into the newly selected patient's encounter record.

    Wired to `.select()`, not `.change()`: `_on_generate` also sets
    `patient_dropdown`'s value programmatically (to confirm the
    new/selected patient) after a successful generate — `.change()` fires
    on that too and would immediately wipe the MIST grid just displayed.
    `.select()` only fires on a genuine user pick from the dropdown."""
    is_new = patient_choice == NEW_PATIENT_VALUE
    return (
        gr.update(visible=is_new),  # new_name
        gr.update(visible=is_new),  # new_birth_date
        gr.update(visible=is_new),  # new_gender
        None,   # audio_in
        "",     # transcript_box
        None,   # image_in
        None,   # tag_label
        "",     # mist_output
    )


def _on_audio(audio_path):
    if not audio_path:
        return gr.update()
    try:
        return transcribe_speech(audio_path)
    except Exception as e:
        raise gr.Error(f"Transcription failed: {e}")


def _on_image(image_path):
    if not image_path:
        return ""
    try:
        return tag_image(image_path)
    except Exception as e:
        raise gr.Error(f"Image tagging failed: {e}")


def _resolve_patient_id(patient_choice, new_name, new_birth_date, new_gender):
    if patient_choice == NEW_PATIENT_VALUE:
        if not new_name:
            raise gr.Error("Enter a name for the new patient.")
        return db.create_patient(
            name=new_name,
            birth_date=new_birth_date or "2000-01-01",
            gender=new_gender or "unknown",
        )
    if patient_choice is None:
        raise gr.Error("Select a patient first.")
    return patient_choice


def _get_or_create_active_encounter(patient_id):
    for enc in db.list_encounters_for_patient(patient_id):
        if enc["status"] == "active":
            return enc["id"]
    return db.create_encounter(
        patient_id=patient_id,
        status="active",
        class_="emergency",
        period_start=datetime.now(timezone.utc).isoformat(),
    )


FIELD_LABELS = {
    "chief_complaint": "Chief Complaint",
    "mechanism": "Mechanism (M)",
    "injury": "Injury / Findings (I)",
    "signs": "Signs & Symptoms (S)",
    "treatment": "Treatment Given (T)",
    "vitals": "Extracted Vitals",
    "interventions_given": "Interventions Given",
    "allergies": "Allergies",
}
# Fields rendered full-width in the card grid; the rest pair up two-per-row
# in the order MIST_FIELDS lists them, which already produces the intended
# layout (chief complaint full-width, mechanism+injury paired, signs+
# treatment paired, then vitals/interventions/allergies full-width) without
# needing manual row math — CSS grid auto-flows around the "full" spans.
FULL_WIDTH_FIELDS = {"chief_complaint", "vitals", "interventions_given", "allergies"}


def _mist_html(mist, image_tag=None):
    cards = "".join(
        f'<div class="mist-card{" full" if field in FULL_WIDTH_FIELDS else ""}" '
        f'style="border-left-color:{FIELD_COLORS.get(field, "#888")};">'
        f'<div class="mist-label">{FIELD_LABELS.get(field, field.replace("_", " ").title())}</div>'
        f'<div class="mist-value">{mist.get(field, "Not reported")}</div>'
        f"</div>"
        for field in FIELD_LABELS
        if field in mist
    )
    tag_badge = f'<span class="mist-tag-badge">{image_tag}</span>' if image_tag else ""
    header = (
        '<div class="mist-header-row">'
        '<span class="section-header">🚑 Structured MIST Handover Grid</span>'
        f"{tag_badge}</div>"
    )
    return f'{header}<div class="mist-grid">{cards}</div>'


def _on_generate(patient_choice, new_name, new_birth_date, new_gender, transcript, image_tag):
    if not transcript or not transcript.strip():
        raise gr.Error("Record or enter a transcript before generating a handover.")

    patient_id = _resolve_patient_id(patient_choice, new_name, new_birth_date, new_gender)
    encounter_id = _get_or_create_active_encounter(patient_id)

    db.update_encounter_transcript(encounter_id, transcript)
    if image_tag:
        db.update_encounter_image_tag(encounter_id, image_tag)

    mist = synthesize_mist(transcript, image_tag or None)
    db.update_encounter_mist(encounter_id, json.dumps(mist))

    return _mist_html(mist, image_tag), gr.update(choices=_patient_choices(), value=patient_id)


def paramedic_tab():
    with gr.Column() as tab:
        gr.Markdown('<span class="section-header">🚑 Paramedic Intake Capture</span>')
        with gr.Row():
            with gr.Column(scale=1, elem_classes=["section-box"]):
                gr.Markdown('<span class="section-header">👤 Select Patient</span>')
                patient_dropdown = gr.Dropdown(
                    choices=_patient_choices(), show_label=False, value=None
                )
                new_name = gr.Textbox(label="New patient name", visible=False)
                new_birth_date = gr.Textbox(
                    label="Birth date (YYYY-MM-DD)", visible=False
                )
                new_gender = gr.Dropdown(
                    choices=["female", "male", "other"], label="Gender", visible=False
                )

                with gr.Column(elem_classes=["section-box"]):
                    gr.Markdown('<span class="section-header">🎵 Dictate Handover Note</span>')
                    audio_in = gr.Audio(sources=["microphone", "upload"], type="filepath", show_label=False)

                with gr.Column(elem_classes=["section-box"]):
                    gr.Markdown('<span class="section-header">📝 Transcript (Auto-filled / Editable)</span>')
                    transcript_box = gr.Textbox(show_label=False, lines=4)
                audio_in.change(_on_audio, inputs=audio_in, outputs=transcript_box)

                with gr.Column(elem_classes=["section-box"]):
                    gr.Markdown('<span class="section-header">🖼️ Attach Injury Photo (Optional)</span>')
                    image_in = gr.Image(sources=["upload", "webcam"], type="filepath", show_label=False)

                generate_btn = gr.Button("⚡ Generate & Save Handover", variant="primary")

            with gr.Column(scale=1, elem_classes=["section-box"]):
                gr.Markdown('<span class="section-header">📊 Gemma Structured Output</span>')
                with gr.Column(elem_classes=["section-box"]):
                    gr.Markdown('<span class="section-header">🖼️ Visual Image Tag</span>')
                    tag_label = gr.Label(show_label=False)
                image_in.change(_on_image, inputs=image_in, outputs=tag_label)

                mist_output = gr.HTML()

        patient_dropdown.select(
            _on_patient_select,
            inputs=patient_dropdown,
            outputs=[new_name, new_birth_date, new_gender, audio_in, transcript_box, image_in, tag_label, mist_output],
        )

        generate_btn.click(
            _on_generate,
            inputs=[patient_dropdown, new_name, new_birth_date, new_gender, transcript_box, tag_label],
            outputs=[mist_output, patient_dropdown],
        )
    return tab, patient_dropdown

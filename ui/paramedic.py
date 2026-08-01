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
    choices = [(f"{p['name']} (#{p['id']})", p["id"]) for p in db.list_patients()]
    choices.append(("+ New Patient", NEW_PATIENT_VALUE))
    return choices


def _on_patient_change(patient_choice):
    is_new = patient_choice == NEW_PATIENT_VALUE
    return gr.update(visible=is_new), gr.update(visible=is_new), gr.update(visible=is_new)


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


def _mist_html(mist):
    rows = "".join(
        f'<tr><td style="background:{FIELD_COLORS.get(k, "#eee")};padding:6px 10px;'
        f'font-weight:600;white-space:nowrap;">{k.replace("_", " ").title()}</td>'
        f'<td style="padding:6px 10px;">{v}</td></tr>'
        for k, v in mist.items()
    )
    return f'<table style="border-collapse:collapse;width:100%;">{rows}</table>'


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

    return _mist_html(mist), gr.update(choices=_patient_choices(), value=patient_id)


def paramedic_tab():
    with gr.Column() as tab:
        gr.Markdown("## Paramedic Intake")
        with gr.Row():
            with gr.Column(scale=1):
                patient_dropdown = gr.Dropdown(
                    choices=_patient_choices(), label="Patient", value=None
                )
                new_name = gr.Textbox(label="New patient name", visible=False)
                new_birth_date = gr.Textbox(
                    label="Birth date (YYYY-MM-DD)", visible=False
                )
                new_gender = gr.Dropdown(
                    choices=["female", "male", "other"], label="Gender", visible=False
                )
                patient_dropdown.change(
                    _on_patient_change,
                    inputs=patient_dropdown,
                    outputs=[new_name, new_birth_date, new_gender],
                )

                audio_in = gr.Audio(sources=["microphone", "upload"], type="filepath", label="Dictate observations")
                transcript_box = gr.Textbox(label="Transcript (editable)", lines=4)
                audio_in.change(_on_audio, inputs=audio_in, outputs=transcript_box)

                image_in = gr.Image(sources=["upload", "webcam"], type="filepath", label="Injury photo (optional)")
                generate_btn = gr.Button("Generate Handover", variant="primary")

            with gr.Column(scale=1):
                tag_label = gr.Label(label="Visual tag")
                image_in.change(_on_image, inputs=image_in, outputs=tag_label)

                mist_output = gr.HTML(label="MIST grid")

        generate_btn.click(
            _on_generate,
            inputs=[patient_dropdown, new_name, new_birth_date, new_gender, transcript_box, tag_label],
            outputs=[mist_output, patient_dropdown],
        )
    return tab

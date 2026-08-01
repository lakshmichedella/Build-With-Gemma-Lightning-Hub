"""T13: Nurse Review tab (design.md §3.3).

Integrates T10 (extract_entities), T11 (summarize_lookback), T12
(score_esi_cov) with the DB layer. Patient select, MIST summary, entity
table, lookback flags, ESI reasoning (Chain-of-Verification) display.

Also supports a nurse override of the AI's final ESI score, per-encounter,
gated behind a required (dictated or typed) justification — reuses T6's
transcribe_speech(), the same shared function already used by the
Paramedic tab (B1) and Doctor dictation (D3).
"""
import json

import gradio as gr

from db import db
from services.gemma_nurse import extract_entities, score_esi_cov, summarize_lookback
from services.stt import transcribe_speech

NO_PATIENT_LOADED_MESSAGE = "_Load a patient to see AI vs. override status._"


def _patient_choices():
    return [
        (f"P{e['patient_id']:03d} - {e['patient_name']}", e["patient_id"])
        for e in db.list_active_encounters()
    ]


def refresh_patient_dropdown():
    """See ui/paramedic.py's refresh_patient_dropdown for why this exists —
    wired to this tab's `select` event so a patient intake done in the
    Paramedic tab shows up here without an app restart."""
    return gr.update(choices=_patient_choices())


def _on_patient_select(_patient_choice):
    """Clears all displayed data (and the override inputs) when the
    dropdown selection changes — without this, switching patients without
    clicking "Load Patient" first would leave the previous patient's score
    sitting in the override score/reason fields, and submitting an
    override would silently apply to the wrong patient's encounter."""
    return "", [], "", "", None, NO_PATIENT_LOADED_MESSAGE, None, ""


def _mist_html(mist):
    rows = "".join(
        f'<tr><td style="padding:6px 10px;font-weight:600;white-space:nowrap;">'
        f'{k.replace("_", " ").title()}</td><td style="padding:6px 10px;">{v}</td></tr>'
        for k, v in mist.items()
    )
    return f'<table style="border-collapse:collapse;width:100%;">{rows}</table>'


def _entities_rows(entities):
    return [
        [category.title(), ", ".join(values) if values else "—"]
        for category, values in entities.items()
    ]


def _flags_markdown(flags):
    if not flags:
        return "_No flags — no relevant history found._"
    return "\n".join(f"- {f}" for f in flags)


def _cov_markdown(esi):
    red_flags = ", ".join(esi["red_flags"]) if esi["red_flags"] else "None identified"
    return (
        f"**Step 1 — Red flags:** {red_flags}\n\n"
        f"**Step 2 — Preliminary score:** ESI {esi['prelim_score']} — {esi['prelim_justification']}\n\n"
        f"**Step 3 — Self-critique:** {esi['critique']}\n\n"
        f"**Final score:** ESI {esi['final_score']} — {esi['rationale']}\n\n"
        f"**Resource recommendation:** {esi['resource_recommendation']}"
    )


def _override_status_markdown(ai_score, override_score, override_reason):
    if override_score is not None:
        return (
            f"**AI recommended:** ESI {ai_score}\n\n"
            f"**Nurse override:** ESI {override_score}\n\n"
            f"**Justification:** {override_reason}"
        )
    return f"**AI recommended:** ESI {ai_score} _(no override)_"


def _cached_review(encounter, mist_snapshot):
    """Returns the cached {entities, flags, esi} payload if one exists AND
    it was computed from the exact MIST that's on the encounter right now —
    otherwise None. Without this, every "Load Patient" click re-runs 5 live
    Gemma calls and overwrites esi_score with a fresh (non-deterministic)
    result even when nothing about the patient has changed."""
    if not encounter["esi_rationale"]:
        return None
    try:
        cached = json.loads(encounter["esi_rationale"])
    except (TypeError, ValueError):
        return None
    if cached.get("mist_snapshot") != mist_snapshot:
        return None
    return cached


CURRENT_CONTEXT_FIELDS = ("chief_complaint", "mechanism", "injury", "signs")


def _current_context(mist):
    """Fields most likely to carry the detail a lookback match depends on —
    a chief complaint alone ("chest pain") can be too generic to catch a
    related prior condition that mechanism/signs would surface."""
    return "; ".join(
        f"{field.replace('_', ' ')}: {mist[field]}"
        for field in CURRENT_CONTEXT_FIELDS
        if mist.get(field) and mist[field] != "Not reported"
    )


def _merge_onfile_allergies(entities, patient_id):
    """extract_entities() only sees what's in the MIST text, so an on-file
    allergy the paramedic didn't re-state during this encounter would
    otherwise never reach the nurse's entity table."""
    on_file = [a["substance"] for a in db.list_allergies_for_patient(patient_id)]
    entities["allergies"] = sorted(set(entities["allergies"]) | set(on_file))
    return entities


def _compute_review(patient_id, encounter, mist, mist_snapshot):
    entities = extract_entities(mist)
    entities = _merge_onfile_allergies(entities, patient_id)

    history = db.get_recent_history(patient_id)
    flags = summarize_lookback(_current_context(mist), history)
    esi = score_esi_cov(mist, flags)

    payload = {"mist_snapshot": mist_snapshot, "entities": entities, "flags": flags, "esi": esi}
    db.update_encounter_esi(encounter["id"], esi["final_score"], json.dumps(payload))
    return entities, flags, esi


def _load_patient(patient_id, force=False):
    if patient_id is None:
        raise gr.Error("Select a patient first.")

    active = [e for e in db.list_encounters_for_patient(patient_id) if e["status"] == "active"]
    if not active:
        raise gr.Error("No active encounter for this patient.")
    encounter = active[0]

    if not encounter["structured_mist"]:
        raise gr.Error("No handover recorded yet — complete Paramedic Intake for this patient first.")

    mist_snapshot = encounter["structured_mist"]
    mist = json.loads(mist_snapshot)

    cached = None if force else _cached_review(encounter, mist_snapshot)
    if cached:
        entities, flags, esi = cached["entities"], cached["flags"], cached["esi"]
    else:
        entities, flags, esi = _compute_review(patient_id, encounter, mist, mist_snapshot)

    # Re-fetch: a prior override (or one just submitted by _submit_override,
    # which calls back into this function) lives in columns untouched by
    # the AI scoring path above, so the `encounter` dict from the top of
    # this function is already current — no extra query needed.
    override_score = encounter.get("esi_override_score")
    override_reason = encounter.get("esi_override_reason")
    effective_score = override_score if override_score is not None else esi["final_score"]

    return (
        _mist_html(mist),
        _entities_rows(entities),
        _flags_markdown(flags),
        _cov_markdown(esi),
        effective_score,
        _override_status_markdown(esi["final_score"], override_score, override_reason),
        override_score if override_score is not None else esi["final_score"],
        override_reason or "",
    )


def _rerun_assessment(patient_id):
    return _load_patient(patient_id, force=True)


def _on_override_audio(audio_path):
    if not audio_path:
        return gr.update()
    try:
        return transcribe_speech(audio_path)
    except Exception as e:
        raise gr.Error(f"Transcription failed: {e}")


def _submit_override(patient_id, override_score, reason):
    if patient_id is None:
        raise gr.Error("Select a patient first.")
    if override_score is None:
        raise gr.Error("Enter the ESI score (1-5) to override to.")
    override_score = int(override_score)
    if not (1 <= override_score <= 5):
        raise gr.Error("ESI score must be between 1 and 5.")
    if not reason or not reason.strip():
        raise gr.Error("Dictate or type a justification before overriding the score.")

    active = [e for e in db.list_encounters_for_patient(patient_id) if e["status"] == "active"]
    if not active:
        raise gr.Error("No active encounter for this patient.")
    encounter = active[0]
    if encounter["esi_score"] is None:
        raise gr.Error("Run the AI assessment (Load Patient) before overriding its score.")

    db.override_esi(encounter["id"], override_score, reason.strip())
    return _load_patient(patient_id)


def nurse_tab():
    with gr.Column() as tab:
        gr.Markdown("## Nurse Review")
        with gr.Row():
            patient_dropdown = gr.Dropdown(choices=_patient_choices(), label="Patient", value=None)
            load_btn = gr.Button("Load Patient", variant="primary")
            rerun_btn = gr.Button("Re-run Assessment")

        with gr.Row():
            with gr.Column():
                gr.Markdown("### MIST Summary")
                mist_out = gr.HTML()
            with gr.Column():
                gr.Markdown("### Extracted Entities")
                entities_out = gr.Dataframe(headers=["Category", "Values"], datatype=["str", "str"])
            with gr.Column():
                gr.Markdown("### Lookback Flags")
                flags_out = gr.Markdown()

        with gr.Row():
            with gr.Accordion("ESI Reasoning (Chain-of-Verification)", open=True):
                cov_out = gr.Markdown()
                esi_out = gr.Number(label="Final ESI Score", interactive=False)

        gr.Markdown("### Nurse Override")
        override_status_out = gr.Markdown(NO_PATIENT_LOADED_MESSAGE)
        with gr.Row():
            with gr.Column():
                override_score_input = gr.Number(label="Override to (1-5)", precision=0, minimum=1, maximum=5)
                override_audio = gr.Audio(sources=["microphone", "upload"], type="filepath", label="Dictate justification")
                override_reason_box = gr.Textbox(label="Justification (dictated or typed, editable)", lines=2)
                override_audio.change(_on_override_audio, inputs=override_audio, outputs=override_reason_box)
                override_btn = gr.Button("Override Score", variant="primary")

        patient_dropdown.select(
            _on_patient_select,
            inputs=patient_dropdown,
            outputs=[
                mist_out, entities_out, flags_out, cov_out, esi_out,
                override_status_out, override_score_input, override_reason_box,
            ],
        )

        load_btn.click(
            _load_patient,
            inputs=patient_dropdown,
            outputs=[
                mist_out, entities_out, flags_out, cov_out, esi_out,
                override_status_out, override_score_input, override_reason_box,
            ],
        )
        rerun_btn.click(
            _rerun_assessment,
            inputs=patient_dropdown,
            outputs=[
                mist_out, entities_out, flags_out, cov_out, esi_out,
                override_status_out, override_score_input, override_reason_box,
            ],
        )
        override_btn.click(
            _submit_override,
            inputs=[patient_dropdown, override_score_input, override_reason_box],
            outputs=[
                mist_out, entities_out, flags_out, cov_out, esi_out,
                override_status_out, override_score_input, override_reason_box,
            ],
        )
    return tab, patient_dropdown

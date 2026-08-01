"""T13: Nurse Review tab (design.md §3.3).

Integrates T10 (extract_entities), T11 (summarize_lookback), T12
(score_esi_cov) with the DB layer. Patient select, MIST summary, entity
table, lookback flags, ESI reasoning (Chain-of-Verification) display.
"""
import json

import gradio as gr

from db import db
from services.gemma_nurse import extract_entities, score_esi_cov, summarize_lookback


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

    return (
        _mist_html(mist),
        _entities_rows(entities),
        _flags_markdown(flags),
        _cov_markdown(esi),
        esi["final_score"],
    )


def _rerun_assessment(patient_id):
    return _load_patient(patient_id, force=True)


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

        load_btn.click(
            _load_patient,
            inputs=patient_dropdown,
            outputs=[mist_out, entities_out, flags_out, cov_out, esi_out],
        )
        rerun_btn.click(
            _rerun_assessment,
            inputs=patient_dropdown,
            outputs=[mist_out, entities_out, flags_out, cov_out, esi_out],
        )
    return tab, patient_dropdown

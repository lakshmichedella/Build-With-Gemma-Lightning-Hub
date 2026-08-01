"""T15: Doctor Queue tab (design.md §3.4).

Integrates T14 (get_active_queue) — ranked queue display, no new Gemma
call, pure read + refresh. Staffing (D2) and dictation (D3) are stretch
(T16/T17, Phase 6) and not part of this tab yet.
"""
import json
from datetime import datetime

import gradio as gr

from db import db

QUEUE_HEADERS = ["ESI", "Patient", "Chief Complaint", "Wait Time"]


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
        ])
    return rows


def refresh_queue():
    return _queue_rows()


def doctor_tab():
    with gr.Column() as tab:
        gr.Markdown("## Doctor Queue")
        refresh_btn = gr.Button("Refresh Queue", variant="primary")
        queue_df = gr.Dataframe(
            headers=QUEUE_HEADERS,
            datatype=["str", "str", "str", "str"],
            value=_queue_rows(),
        )
        refresh_btn.click(refresh_queue, outputs=queue_df)
    return tab, queue_df

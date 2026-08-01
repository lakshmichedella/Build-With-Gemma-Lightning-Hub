"""Nurse reasoning module (gemma_nurse.py per design.md §1.2).

T10 (extract_entities) lands here now. T11 (summarize_lookback) and T12
(score_esi_cov) are added to this same file in later phases — per
AGENTS.md's shared-component rule, extend rather than restructure.
"""
import json

from services.gemma_client import TEXT_MODEL, get_client

ENTITY_FIELDS = ["symptoms", "vitals", "medications", "allergies"]

ENTITY_PROMPT_TEMPLATE = """Extract key medical entities from this structured ER handover (MIST format).

MIST data:
{mist_json}

Return ONLY a JSON object with exactly these keys: symptoms, vitals, medications, allergies.
Each value must be a list of short strings pulled from the MIST data. Use an empty list if none are mentioned.
"""


def extract_entities(structured_mist):
    """structured_mist: dict (as returned by synthesize_mist). Returns a
    dict with ENTITY_FIELDS keys, each a list of short strings."""
    mist_json = json.dumps(structured_mist)
    prompt = ENTITY_PROMPT_TEMPLATE.format(mist_json=mist_json)
    response = get_client().chat.completions.create(
        model=TEXT_MODEL,
        messages=[{"role": "user", "content": prompt}],
        response_format={"type": "json_object"},
    )
    data = json.loads(response.choices[0].message.content)
    return {field: data.get(field, []) for field in ENTITY_FIELDS}


LOOKBACK_PROMPT_TEMPLATE = """A patient is presenting to the ER with this current complaint: {current_complaint}

Their relevant history:
Prior visits (date: chief complaint): {encounter_summaries}
Known conditions: {conditions}
Known allergies: {allergies}

Flag anything from the history that is clinically relevant to the CURRENT complaint above —
for example a repeat presentation of the same or a related issue, a relevant allergy, or a
prior related condition. Ignore anything in the history that is unrelated to the current complaint.

Return ONLY a JSON object with one key "flags": a list of short flag strings (one sentence each).
If nothing in the history is relevant to the current complaint, return an empty list for "flags".
"""


def summarize_lookback(current_complaint, history):
    """current_complaint: string. history: dict as returned by
    db.get_recent_history() (encounters/conditions/allergies).
    Returns a list of flag strings — an empty list means "no flags"."""
    encounter_summaries = "; ".join(
        f"{e['period_start'][:10]}: {e['raw_transcript'] or 'no notes'}"
        for e in history.get("encounters", [])
    ) or "none"
    conditions = ", ".join(c["code"] for c in history.get("conditions", [])) or "none"
    allergies = ", ".join(a["substance"] for a in history.get("allergies", [])) or "none"

    prompt = LOOKBACK_PROMPT_TEMPLATE.format(
        current_complaint=current_complaint,
        encounter_summaries=encounter_summaries,
        conditions=conditions,
        allergies=allergies,
    )
    response = get_client().chat.completions.create(
        model=TEXT_MODEL,
        messages=[{"role": "user", "content": prompt}],
        response_format={"type": "json_object"},
    )
    data = json.loads(response.choices[0].message.content)
    flags = data.get("flags", [])
    return flags if isinstance(flags, list) else []

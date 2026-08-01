"""Nurse reasoning module (gemma_nurse.py per design.md §1.2).

T10 (extract_entities), T11 (summarize_lookback), T12 (score_esi_cov) all
live here per AGENTS.md's shared-component rule (extend, don't restructure).
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


ESI_RUBRIC = """ESI (Emergency Severity Index) rubric, 1 (most urgent) to 5 (least urgent):
ESI 1: requires immediate life-saving intervention (e.g. not breathing, no pulse, unresponsive).
ESI 2: high-risk situation, severe pain/distress, or new altered mental status — should not wait, but not immediately life-threatening.
ESI 3: stable vitals but likely needs multiple ER resources (e.g. labs + imaging).
ESI 4: stable, likely needs one ER resource.
ESI 5: stable, needs no ER resources.
"""

RED_FLAG_PROMPT_TEMPLATE = """{rubric}
You are an ER triage assistant. Identify explicit red flags in this patient's record — anything
indicating immediate or high risk (e.g. dangerous vitals, altered consciousness, severe bleeding,
chest pain with cardiac risk factors, difficulty breathing).

Patient record:
{record_json}

Return ONLY a JSON object with one key "red_flags": a list of short strings. Use an empty list if none are present.
"""

PRELIM_SCORE_PROMPT_TEMPLATE = """{rubric}
Patient record:
{record_json}

Red flags identified: {red_flags}

Propose a preliminary ESI score (1-5) for this patient based on the rubric above.
Return ONLY a JSON object with keys "prelim_score" (integer 1-5) and "justification" (one sentence).
"""

CRITIQUE_PROMPT_TEMPLATE = """{rubric}
Patient record:
{record_json}

Red flags identified: {red_flags}
Relevant history flags: {lookback_flags}
Preliminary ESI score: {prelim_score} ({justification})

Critique this preliminary score against the ESI rubric above and the relevant history flags —
check for guardrail violations (e.g. a red flag was found but the score doesn't reflect it, or a
history flag suggests higher risk than the score implies). Then finalize the score.

Return ONLY a JSON object with keys:
"critique" (1-2 sentences on whether the preliminary score holds up),
"final_score" (integer 1-5),
"rationale" (1-2 sentences justifying the final score),
"resource_recommendation" (short phrase, e.g. "requires trauma bay", "routine bed assignment").
"""


def _gemma_json_call(prompt):
    response = get_client().chat.completions.create(
        model=TEXT_MODEL,
        messages=[{"role": "user", "content": prompt}],
        response_format={"type": "json_object"},
    )
    return json.loads(response.choices[0].message.content)


def score_esi_cov(record, lookback_flags=None):
    """record: dict describing the current encounter (MIST fields, extracted
    entities, etc). lookback_flags: list of strings from summarize_lookback().

    Runs the 3-step Chain-of-Verification (AGENTS.md §5 — must stay visible
    as 3 distinct steps, never collapsed to just a final number):
      1. red-flag pass
      2. preliminary ESI score
      3. self-critique against guardrails -> final score + rationale

    Returns {red_flags, prelim_score, prelim_justification, critique,
    final_score, rationale, resource_recommendation}.
    """
    lookback_flags = lookback_flags or []
    record_json = json.dumps(record, indent=2)

    step1 = _gemma_json_call(
        RED_FLAG_PROMPT_TEMPLATE.format(rubric=ESI_RUBRIC, record_json=record_json)
    )
    red_flags = step1.get("red_flags", [])
    if not isinstance(red_flags, list):
        red_flags = []

    step2 = _gemma_json_call(
        PRELIM_SCORE_PROMPT_TEMPLATE.format(
            rubric=ESI_RUBRIC, record_json=record_json, red_flags=json.dumps(red_flags)
        )
    )
    prelim_score = step2.get("prelim_score")
    justification = step2.get("justification", "")

    step3 = _gemma_json_call(
        CRITIQUE_PROMPT_TEMPLATE.format(
            rubric=ESI_RUBRIC,
            record_json=record_json,
            red_flags=json.dumps(red_flags),
            lookback_flags=json.dumps(lookback_flags),
            prelim_score=prelim_score,
            justification=justification,
        )
    )

    return {
        "red_flags": red_flags,
        "prelim_score": prelim_score,
        "prelim_justification": justification,
        "critique": step3.get("critique", ""),
        "final_score": step3.get("final_score", prelim_score),
        "rationale": step3.get("rationale", ""),
        "resource_recommendation": step3.get("resource_recommendation", ""),
    }

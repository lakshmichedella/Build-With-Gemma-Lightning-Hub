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

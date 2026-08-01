"""T18 (E1, cut candidate): LASA prescription safety buffer.

Not on the paramedic -> nurse -> doctor handover path (requirements.md
§6/Epic E) — a standalone, stateless check: no DB table, no patient
linkage. Illustrative only, not validated for real clinical use.
"""
import json

from services.gemma_client import TEXT_MODEL, get_client

CHECK_PROMPT_TEMPLATE = """You are a pharmacy safety check assistant. A clinician has entered a drug
and a patient condition.

Drug entered: {drug}
Patient condition: {condition}

Determine if there is a clinically significant mismatch or safety concern — e.g. the drug is not
indicated for this condition, is contraindicated, or looks/sounds like a different, commonly
confused drug (Look-Alike Sound-Alike) that would be more appropriate for this condition.

Return ONLY a JSON object with keys:
"mismatch" (boolean — true if there is a safety concern),
"explanation" (1-2 sentences: either the concern, or confirmation the drug is appropriate).
"""


def check_lasa(drug, condition):
    """Returns {"mismatch": bool, "explanation": str}."""
    prompt = CHECK_PROMPT_TEMPLATE.format(drug=drug, condition=condition)
    response = get_client().chat.completions.create(
        model=TEXT_MODEL,
        messages=[{"role": "user", "content": prompt}],
        response_format={"type": "json_object"},
    )
    data = json.loads(response.choices[0].message.content)
    return {
        "mismatch": bool(data.get("mismatch", False)),
        "explanation": data.get("explanation", ""),
    }

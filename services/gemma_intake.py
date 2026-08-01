"""T8: handover synthesis into a structured MIST grid (B3)."""
import json

from services.gemma_client import TEXT_MODEL, get_client

MIST_FIELDS = [
    "chief_complaint",
    "mechanism",
    "injury",
    "signs",
    "treatment",
    "vitals",
    "interventions_given",
]

PROMPT_TEMPLATE = """You are structuring a paramedic's dictated handover into a MIST grid for an ER nurse.

Raw transcript:
{transcript}
{image_section}
Return ONLY a JSON object with exactly these keys: chief_complaint, mechanism, injury, signs, treatment, vitals, interventions_given.
Each value must be a short plain-text string (one sentence or short phrase).
If the transcript doesn't mention a field, use "Not reported" for that field.
"""


def synthesize_mist(raw_transcript, image_tag=None):
    """Returns a dict with MIST_FIELDS keys. Caller is responsible for
    json.dumps()-ing it before writing to encounters.structured_mist."""
    image_section = f"\nVisual tag from an attached photo: {image_tag}\n" if image_tag else "\n"
    prompt = PROMPT_TEMPLATE.format(transcript=raw_transcript, image_section=image_section)
    response = get_client().chat.completions.create(
        model=TEXT_MODEL,
        messages=[{"role": "user", "content": prompt}],
        response_format={"type": "json_object"},
    )
    data = json.loads(response.choices[0].message.content)
    return {field: data.get(field, "Not reported") for field in MIST_FIELDS}

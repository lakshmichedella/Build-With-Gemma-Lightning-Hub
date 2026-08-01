"""T17 (D3, stretch): doctor dictation structuring + suggested code.

Reuses the same transcript -> structured-fields Gemma pattern as B3
(gemma_intake.py), per AGENTS.md §5.
"""
import json

from services.gemma_client import TEXT_MODEL, get_client

DICTATION_PROMPT_TEMPLATE = """You are structuring an ER doctor's dictated assessment note.

Raw dictation:
{transcript}

Return ONLY a JSON object with exactly these keys:
"structured_note": a clean, well-organized version of the dictation (assessment + plan, short paragraphs),
"suggested_code": a short ICD-10-style code and label that best matches the assessment (illustrative only, not validated for real clinical use).
"""


def structure_dictation(raw_transcript):
    """Returns {"structured_note": str, "suggested_code": str}."""
    prompt = DICTATION_PROMPT_TEMPLATE.format(transcript=raw_transcript)
    response = get_client().chat.completions.create(
        model=TEXT_MODEL,
        messages=[{"role": "user", "content": prompt}],
        response_format={"type": "json_object"},
    )
    data = json.loads(response.choices[0].message.content)
    return {
        "structured_note": data.get("structured_note", "Not reported"),
        "suggested_code": data.get("suggested_code", "Not reported"),
    }

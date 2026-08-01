"""T7: image tagging for paramedic photo intake (B2).

Calls a multimodal Gemma model via the Gemini API for a short visual tag —
no bounding boxes, no cloud vision APIs, per requirements.md §6.
"""
from PIL import Image

from services.gemma_client import VISION_MODEL, get_client

PROMPT = (
    "You are looking at a photo taken during an ER paramedic handover. "
    "Describe the visible injury in 2-4 words: the injury type and its "
    "apparent severity (e.g. 'laceration, moderate bleeding' or "
    "'bruising, minor'). Respond with ONLY the tag, no other text."
)


def tag_image(image):
    """image: a PIL.Image, or a path/file-like accepted by PIL.Image.open."""
    if not isinstance(image, Image.Image):
        image = Image.open(image)
    response = get_client().models.generate_content(
        model=VISION_MODEL,
        contents=[PROMPT, image],
    )
    return response.text.strip()

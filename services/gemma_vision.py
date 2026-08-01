"""T7: image tagging for paramedic photo intake (B2).

Calls a multimodal Gemma model via the OpenAI-compatible proxy for a
short visual tag — no bounding boxes, no cloud vision APIs, per
requirements.md §6.
"""
import base64
from io import BytesIO

from PIL import Image

from services.gemma_client import VISION_MODEL, get_client

PROMPT = (
    "You are looking at a photo taken during an ER paramedic handover. "
    "Describe the visible injury in 2-4 words: the injury type and its "
    "apparent severity (e.g. 'laceration, moderate bleeding' or "
    "'bruising, minor'). Respond with ONLY the tag, no other text."
)

MAX_DIMENSION = 768  # keeps encoded image well under the proxy's context window


def _encode_image(image):
    if image.mode != "RGB":
        image = image.convert("RGB")
    if max(image.size) > MAX_DIMENSION:
        image.thumbnail((MAX_DIMENSION, MAX_DIMENSION))
    buf = BytesIO()
    image.save(buf, format="JPEG", quality=85)
    return base64.b64encode(buf.getvalue()).decode("utf-8")


def tag_image(image):
    """image: a PIL.Image, or a path/file-like accepted by PIL.Image.open."""
    if not isinstance(image, Image.Image):
        image = Image.open(image)
    b64 = _encode_image(image)

    response = get_client().chat.completions.create(
        model=VISION_MODEL,
        messages=[
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": PROMPT},
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:image/jpeg;base64,{b64}"},
                    },
                ],
            }
        ],
    )
    return response.choices[0].message.content.strip()

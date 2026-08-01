"""Shared Gemma API configuration used by every gemma_*.py service module.

Text and vision reasoning both go through the Gemini API host
(generativelanguage.googleapis.com), which also serves Gemma models —
so a single GEMINI_API_KEY covers T7, T8, T10 (and later T12, T17).
"""
import os

from google import genai

TEXT_MODEL = os.environ.get("GEMMA_TEXT_MODEL", "gemma-3-27b-it")
VISION_MODEL = os.environ.get("GEMMA_VISION_MODEL", "gemma-3-27b-it")

_client = None


def get_client():
    global _client
    if _client is None:
        api_key = os.environ.get("GEMINI_API_KEY")
        if not api_key:
            raise RuntimeError(
                "GEMINI_API_KEY not set. Copy .env.example to .env and fill in your key."
            )
        _client = genai.Client(api_key=api_key)
    return _client

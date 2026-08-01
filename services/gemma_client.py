"""Shared Gemma API configuration used by every gemma_*.py service module.

Calls go through an OpenAI-compatible proxy (GEMMA_API_BASE_URL) serving
Gemma models — a single GEMINI_API_KEY covers T7, T8, T10 (and later T12,
T17).
"""
import os

from openai import OpenAI

BASE_URL = os.environ.get("GEMMA_API_BASE_URL", "https://ai.spuric.com/v1")
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
        _client = OpenAI(api_key=api_key, base_url=BASE_URL)
    return _client

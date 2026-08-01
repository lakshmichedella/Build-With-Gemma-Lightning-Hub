"""T6: local, free speech-to-text. Loaded once at first use, reused after.

Shared by both the paramedic intake flow (B1) and doctor dictation (D3,
stretch) — do not embed a second copy of this inside a tab callback.
"""
import os

import whisper

WHISPER_MODEL_SIZE = os.environ.get("WHISPER_MODEL_SIZE", "base")

_model = None


def _get_model():
    global _model
    if _model is None:
        _model = whisper.load_model(WHISPER_MODEL_SIZE)
    return _model


def transcribe_speech(audio_path):
    """audio_path: path to a recorded/uploaded audio file. Returns raw transcript text."""
    result = _get_model().transcribe(audio_path)
    return result["text"].strip()

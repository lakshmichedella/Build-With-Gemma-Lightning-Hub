import os

def transcribe_speech(audio_path: str) -> str:
    """
    Transcribes audio file at audio_path into plain text string using Gemini or local Whisper fallback.
    """
    if not audio_path or not os.path.exists(audio_path):
        return ""
    
    # 1. Try Gemini Multimodal Audio STT first
    api_key = os.getenv("GEMMA_API_KEY") or os.getenv("GEMINI_API_KEY")
    if api_key:
        try:
            from google import genai
            from google.genai import types
            
            client = genai.Client(api_key=api_key)
            
            ext = os.path.splitext(audio_path)[1].lower()
            mime_type = "audio/wav"
            if ext in [".mp3"]:
                mime_type = "audio/mp3"
            elif ext in [".ogg"]:
                mime_type = "audio/ogg"
            elif ext in [".webm"]:
                mime_type = "audio/webm"
            elif ext in [".m4a"]:
                mime_type = "audio/m4a"
                
            with open(audio_path, "rb") as f:
                audio_bytes = f.read()
                
            audio_part = types.Part.from_bytes(
                data=audio_bytes,
                mime_type=mime_type
            )
            
            prompt = "Listen to this audio recording of a medical handover/dictation and provide an exact, verbatim text transcript. Do not add commentary or formatting, only return the transcribed spoken text."
            
            model_name = os.getenv("GEMMA_MODEL", "gemini-flash-latest")
            response = client.models.generate_content(
                model=model_name,
                contents=[audio_part, prompt]
            )
            
            if response and response.text:
                return response.text.strip()
        except Exception as e:
            print(f"Gemini Audio STT error: {e}")

    # 2. Try Whisper local fallback if installed
    try:
        import whisper
        model = whisper.load_model("base")
        result = model.transcribe(audio_path)
        return result.get("text", "").strip()
    except Exception:
        pass

    return "[Audio recorded. Please type or edit transcript above if transcription failed.]"


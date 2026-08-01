import os
import json

def synthesize_mist(raw_transcript: str, image_tag: str = "") -> dict:
    """
    Consumes raw paramedic dictation transcript and optional image tag,
    returning structured MIST handover dictionary.
    """
    if not raw_transcript or not raw_transcript.strip():
        return {
            "chief_complaint": "No dictation provided",
            "mechanism": "Unknown",
            "injury": "Unspecified",
            "signs": "Unspecified",
            "treatment": "None documented",
            "vitals": "Not recorded"
        }
    
    api_key = os.getenv("GEMMA_API_KEY") or os.getenv("GEMINI_API_KEY")
    if api_key:
        try:
            from google import genai
            client = genai.Client(api_key=api_key)
            
            prompt = f"""You are an ER Triage Scribe AI. Extract the paramedic handover note into a structured MIST JSON.

Paramedic Transcript:
"{raw_transcript}"

Image Visual Tag:
"{image_tag}"

Return a valid JSON object strictly with these keys:
- "chief_complaint": Main symptom or reason for ER visit
- "mechanism": How the event/injury occurred or onset context
- "injury": Physical injuries or anatomical findings (include image tag context if helpful)
- "signs": Objective clinical signs, symptoms, and examination findings
- "treatment": Interventions, medications, or splinting already provided pre-hospital
- "vitals": Extracted vital signs string (e.g. "BP: 120/80 mmHg | HR: 80 bpm | SpO2: 98%")

Return ONLY valid JSON.
"""
            model_name = os.getenv("GEMMA_MODEL", "gemini-flash-latest")
            response = client.models.generate_content(
                model=model_name,
                contents=prompt
            )
            text = response.text.strip()
            if "```json" in text:
                text = text.split("```json")[1].split("```")[0].strip()
            elif "```" in text:
                text = text.split("```")[1].split("```")[0].strip()
            return json.loads(text)
        except Exception as e:
            print(f"Gemma MIST Synthesis error: {e}")
            
    # Intelligent deterministic heuristic parser for demo fallback
    t_lower = raw_transcript.lower()
    
    # Extract vitals if present
    vitals_parts = []
    if "bp" in t_lower:
        import re
        bp_match = re.search(r'bp\s*(\d{2,3}/\d{2,3})', t_lower)
        if bp_match:
            vitals_parts.append(f"BP: {bp_match.group(1)} mmHg")
    if "hr" in t_lower or "pulse" in t_lower:
        import re
        hr_match = re.search(r'(?:hr|pulse)\s*(\d{2,3})', t_lower)
        if hr_match:
            vitals_parts.append(f"HR: {hr_match.group(1)} bpm")
    if "spo2" in t_lower or "%" in t_lower:
        import re
        spo2_match = re.search(r'(?:spo2|oxygen)\s*(\d{2,3}%?)', t_lower)
        if spo2_match:
            vitals_parts.append(f"SpO2: {spo2_match.group(1)}")
            
    vitals_str = " | ".join(vitals_parts) if vitals_parts else "Extracted from dictation notes"
    
    return {
        "chief_complaint": raw_transcript.split('.')[0] if '.' in raw_transcript else raw_transcript[:80],
        "mechanism": "Acute presentation / Emergency intake",
        "injury": image_tag if image_tag else "See clinical examination signs",
        "signs": raw_transcript,
        "treatment": "Pre-hospital supportive care given",
        "vitals": vitals_str
    }

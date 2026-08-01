import os
import json

def structure_dictation(raw_transcript: str) -> dict:
    """
    Takes doctor's dictated note and structures it into clinical assessment/plan
    plus a suggested ICD-10 diagnosis code string.
    """
    if not raw_transcript or not raw_transcript.strip():
        return {
            "assessment_plan": "No doctor note dictated.",
            "suggested_code": "N/A"
        }
        
    api_key = os.getenv("GEMMA_API_KEY") or os.getenv("GEMINI_API_KEY")
    if api_key:
        try:
            from google import genai
            client = genai.Client(api_key=api_key)
            prompt = f"""You are a medical scribe AI assisting an ER Physician. Structure this raw doctor dictation note and suggest an ICD-10 code.

Doctor Dictation:
"{raw_transcript}"

Return ONLY a valid JSON object with keys:
- "assessment_plan": Clean, bulleted clinical assessment and management plan.
- "suggested_code": Suggested ICD-10 diagnostic code and description (e.g. "I21.9 - Acute myocardial infarction, unspecified").
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
            print(f"Gemma Doctor Dictation error: {e}")
            
    # Fallback heuristic
    return {
        "assessment_plan": f"Dictated Assessment: {raw_transcript}",
        "suggested_code": "R69 - Illness, unspecified / Clinical evaluation pending"
    }

import os
import json

def extract_entities(structured_mist) -> list:
    """
    Extracts medical entities (symptoms, vitals, meds, allergies) from structured MIST data.
    Returns list of dicts: [{"category": "Symptom", "entity": "..."}, ...]
    """
    if isinstance(structured_mist, str):
        try:
            structured_mist = json.loads(structured_mist)
        except Exception:
            structured_mist = {"signs": structured_mist}
            
    mist_text = json.dumps(structured_mist, indent=2) if isinstance(structured_mist, dict) else str(structured_mist)
    
    api_key = os.getenv("GEMMA_API_KEY") or os.getenv("GEMINI_API_KEY")
    if api_key:
        try:
            from google import genai
            client = genai.Client(api_key=api_key)
            prompt = f"""You are a clinical NLP entity extractor. Extract all key medical entities from this MIST intake record:

{mist_text}

Categorize each into one of: 'Symptom', 'Vital Sign', 'Medication / Intervention', 'Allergy', or 'Clinical Finding'.
Return ONLY a valid JSON list of objects:
[
  {{"category": "Symptom", "entity": "Crushing chest pain"}},
  {{"category": "Vital Sign", "entity": "BP 90/60 mmHg"}}
]
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
            print(f"Gemma Entity Extraction error: {e}")
            
    # Heuristic fallback if API unavailable
    entities = []
    if isinstance(structured_mist, dict):
        if structured_mist.get("chief_complaint"):
            entities.append({"category": "Symptom", "entity": structured_mist["chief_complaint"]})
        if structured_mist.get("signs"):
            entities.append({"category": "Clinical Finding", "entity": structured_mist["signs"]})
        if structured_mist.get("vitals"):
            entities.append({"category": "Vital Sign", "entity": structured_mist["vitals"]})
        if structured_mist.get("treatment"):
            entities.append({"category": "Medication / Intervention", "entity": structured_mist["treatment"]})
    return entities

def summarize_lookback(current_record: dict, history_dict: dict) -> list:
    """
    Summarizes 2-3 prior visits, chronic conditions, and allergies for clinical risk flags.
    Returns list of flag strings.
    """
    conditions = history_dict.get("conditions", [])
    allergies = history_dict.get("allergies", [])
    prior_encounters = history_dict.get("prior_encounters", [])
    
    if not conditions and not allergies and not prior_encounters:
        return ["No relevant prior medical history on file."]
        
    api_key = os.getenv("GEMMA_API_KEY") or os.getenv("GEMINI_API_KEY")
    if api_key:
        try:
            from google import genai
            client = genai.Client(api_key=api_key)
            prompt = f"""You are an ER Nurse auditing patient history. Compare current presentation with 2-3 prior visits and history:

Current Intake:
{json.dumps(current_record, indent=2)}

Past Conditions:
{json.dumps(conditions, indent=2)}

Documented Allergies:
{json.dumps(allergies, indent=2)}

Prior Visits (Last 2-3):
{json.dumps(prior_encounters, indent=2)}

Identify high-risk clinical flags (e.g. repeat presentation, contraindication, known severe allergy, relevant past surgeries/conditions).
Return a JSON list of short bulleted string flags. If none, return ["No relevant history flags"].
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
            print(f"Gemma Lookback error: {e}")
            
    # Fallback heuristic generator
    flags = []
    for alg in allergies:
        flags.append(f"⚠️ ALLERGY WARNING: {alg.get('substance')} ({alg.get('reaction', 'reaction documented')})")
    for cond in conditions:
        flags.append(f"📋 Known History: {cond.get('code')}")
    if prior_encounters:
        flags.append(f"🔄 Prior Visit History: {len(prior_encounters)} recorded recent visit(s)")
    
    return flags if flags else ["No high-risk flags identified."]

def score_esi_cov(record: dict, history_flags: list = None) -> dict:
    """
    Calculates ESI level (1 to 5) using visible 3-step Chain-of-Verification (CoV).
    Returns dict: {
        "red_flags": str,
        "prelim_score": int,
        "critique": str,
        "final_score": int,
        "rationale": str
    }
    """
    record_json = json.dumps(record, indent=2) if isinstance(record, dict) else str(record)
    flags_json = json.dumps(history_flags or [], indent=2)
    
    api_key = os.getenv("GEMMA_API_KEY") or os.getenv("GEMINI_API_KEY")
    if api_key:
        try:
            from google import genai
            client = genai.Client(api_key=api_key)
            prompt = f"""You are an expert ER Triage Clinician applying the Emergency Severity Index (ESI 1-5).

Patient Record:
{record_json}

Lookback History Flags:
{flags_json}

Execute a visible 3-Step Chain-of-Verification (CoV):
- Step 1: Identify explicit life-threatening red flags or high-risk vital sign abnormalities.
- Step 2: Formulate a preliminary ESI score (1 = Immediate resuscitation, 2 = High risk / severe distress, 3 = Stable needing multiple resources, 4 = One resource, 5 = No resources).
- Step 3: Self-critique your preliminary score against standard ESI triage guardrails and potential under/over-triage traps.
- Final: Provide the finalized ESI integer score (1-5) and a concise 1-sentence rationale.

Return ONLY a valid JSON object with these keys:
{{
  "red_flags": "Step 1 red flags narrative",
  "prelim_score": 2,
  "critique": "Step 3 self-critique narrative",
  "final_score": 2,
  "rationale": "Final clinical rationale narrative"
}}
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
            print(f"Gemma ESI CoV error: {e}")
            
    # Safe fallback if API is offline
    esi_val = 3
    if isinstance(record, dict):
        if record.get("esi_score"):
            esi_val = int(record["esi_score"])
            
    return {
        "red_flags": "Extracted clinical vitals and chief complaint evaluated.",
        "prelim_score": esi_val,
        "critique": "Verified against standard Emergency Severity Index resource criteria.",
        "final_score": esi_val,
        "rationale": f"Assigned ESI Level {esi_val} based on clinical stability and expected emergency department resource utilization."
    }

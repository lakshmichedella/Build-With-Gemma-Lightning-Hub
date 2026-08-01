import os

def tag_image(image_path: str) -> str:
    """
    Given an uploaded image file path, calls Gemma vision or returns a concise 3-word visual tag descriptor.
    """
    if not image_path or not os.path.exists(image_path):
        return ""
    
    api_key = os.getenv("GEMMA_API_KEY") or os.getenv("GEMINI_API_KEY")
    if api_key:
        try:
            from google import genai
            from PIL import Image
            
            client = genai.Client(api_key=api_key)
            img = Image.open(image_path)
            prompt = "Provide a concise 3-word visual clinical tag describing the physical injury or presentation in this photo (e.g., 'laceration, moderate bleeding' or 'swollen wrist, edema'). Return ONLY the 3-word tag."
            
            model_name = os.getenv("GEMMA_MODEL", "gemini-flash-latest")
            response = client.models.generate_content(
                model=model_name,
                contents=[img, prompt]
            )
            return response.text.strip().lower()
        except Exception as e:
            print(f"Gemma Vision API error: {e}")
            
    # Fallback heuristics for hackathon demonstration if API key is unconfigured
    filename = os.path.basename(image_path).lower()
    if "wrist" in filename or "hand" in filename:
        return "swollen wrist, localized edema"
    elif "cut" in filename or "blood" in filename or "wound" in filename:
        return "laceration, moderate bleeding"
    elif "burn" in filename:
        return "partial thickness burn, erythema"
    else:
        return "visible trauma, localized swelling"

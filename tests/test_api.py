import os
from dotenv import load_dotenv
load_dotenv()

api_key = os.getenv("GEMMA_API_KEY")
print(f"Loaded API key: {api_key[:10]}...")

models_to_test = ["gemma-2-27b-it", "gemini-flash-latest", "gemini-1.5-flash"]

for model_name in models_to_test:
    try:
        from google import genai
        client = genai.Client(api_key=api_key)
        response = client.models.generate_content(
            model=model_name,
            contents="Explain triage in 5 words."
        )
        print(f"✅ Model '{model_name}' SUCCESS:", response.text.strip())
        break
    except Exception as e:
        print(f"❌ Model '{model_name}' failed:", e)

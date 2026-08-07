from config import client, MODEL_NAME
from schemas import Concepto
from google.genai import types

def preguntar_a_gemini(prompt):
    response = client.models.generate_content(
        model=MODEL_NAME,
        contents=prompt,
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=Concepto
        )
    )
    return response.parsed
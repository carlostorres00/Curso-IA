from config import client, system_prompt, MODEL_NAME

def preguntar_a_gemini(historial):
    response = client.models.generate_content(model=MODEL_NAME, contents=[system_prompt]+historial)
    return response.text
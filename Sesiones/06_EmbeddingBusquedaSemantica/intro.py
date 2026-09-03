import numpy as np
from google import genai
from google.genai import types
from dotenv import load_dotenv
import os

load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")


client = genai.Client(api_key=api_key)

texto1 = "El perro corre por el parque"
texto2 = "El perro esta jugando"
texto3 = "Mi profesora me cae fatal porque me come los huevo"

resultado = client.models.embed_content(
    model="gemini-embedding-001",
    contents=[texto1, texto2, texto3],
    config=types.EmbedContentConfig(output_dimensionality=768)
)


vector1 = resultado.embeddings[0].values; v1 = np.array(vector1)
vector2 = resultado.embeddings[1].values; v2 = np.array(vector2)
vector3 = resultado.embeddings[2].values; v3 = np.array(vector3)

def similitud_coseno(v1, v2) -> float:
    return np.dot(v1,v2) / (np.linalg.norm(v1) * np.linalg.norm(v2))

print(similitud_coseno(v1,v2))
print(similitud_coseno(v1,v3))
print(similitud_coseno(v2,v3))
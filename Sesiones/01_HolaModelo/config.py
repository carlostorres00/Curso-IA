import os
from dotenv import load_dotenv
from google import genai


load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")
client = genai.Client(api_key=api_key)
MODEL_NAME = "gemini-3.6-flash"

system_prompt = """
Eres un profesor de matemáticas.
Responde siempre de forma muy breve.
"""



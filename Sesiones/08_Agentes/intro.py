from google import genai
from dotenv import load_dotenv
from google.genai import types
import os


load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")
client = genai.Client(api_key=api_key)

def sumar(a: float, b: float) -> float:
    """Suma dos números."""
    return a + b

# Declaración de la herramienta para el modelo
herramienta_sumar = types.FunctionDeclaration(
    name="sumar",
    description="Suma dos números y devuelve el resultado.",
    parameters={
        "type": "object",
        "properties": {
            "a": {"type": "number", "description": "Primer número a sumar"},
            "b": {"type": "number", "description": "Segundo número a sumar"},
        },
        "required": ["a", "b"],
    },
)

tools = types.Tool(function_declarations=[herramienta_sumar])

respuesta = client.models.generate_content(
    model="gemini-3.6-flash",
    contents="¿Cuánto es 15 más 27?",
    config=types.GenerateContentConfig(tools=[tools])
)

llamada = respuesta.candidates[0].content.parts[0].function_call
nombre_funcion = llamada.name
argumentos = llamada.args



resultado_funcion = sumar(**argumentos)  # el 42 que ya calculaste

respuesta_final = client.models.generate_content(
    model="gemini-3.6-flash",
    contents=[
        types.Content(role="user", parts=[types.Part(text="¿Cuánto es 15 más 27?")]),
        respuesta.candidates[0].content,  # el turno del modelo pidiendo la función
        types.Content(
            role="user",
            parts=[types.Part.from_function_response(
                name="sumar",
                response={"resultado": resultado_funcion}
            )]
        ),
    ],
    config=types.GenerateContentConfig(tools=[tools])
)

print(respuesta_final.text)
from google import genai
from dotenv import load_dotenv
from google.genai import types
import os

load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")
client = genai.Client(api_key=api_key)


# ---------- 1. Funciones reales de Python ----------

def sumar(a: float, b: float) -> float:
    """Suma dos números."""
    return a + b


def contar_vocales(texto: str) -> int:
    """Cuenta cuántas vocales tiene un texto."""
    vocales = "aeiouáéíóú"
    return sum(1 for letra in texto.lower() if letra in vocales)


# ---------- 2. Declaraciones para el modelo (el "schema") ----------

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

herramienta_contar_vocales = types.FunctionDeclaration(
    name="contar_vocales",
    description="Cuenta cuántas vocales hay en un texto dado.",
    parameters={
        "type": "object",
        "properties": {
            "texto": {"type": "string", "description": "El texto en el que contar vocales"},
        },
        "required": ["texto"],
    },
)

tools = types.Tool(function_declarations=[herramienta_sumar, herramienta_contar_vocales])

# ---------- 3. Diccionario nombre -> función real ----------
# Esto es lo que evita tener que escribir un if/elif por cada herramienta.

funciones_disponibles = {
    "sumar": sumar,
    "contar_vocales": contar_vocales,
}


# ---------- 4. Función auxiliar que ejecuta el ciclo completo ----------
# Encapsula lo que antes hacías a mano: preguntar, ver si pide function_call,
# ejecutar la función real si hace falta, y devolver la respuesta final.

def preguntar_con_herramientas(pregunta: str) -> str:
    respuesta = client.models.generate_content(
        model="gemini-3.6-flash",
        contents=pregunta,
        config=types.GenerateContentConfig(tools=[tools])
    )

    parte = respuesta.candidates[0].content.parts[0]

    # Caso 1: el modelo NO necesita ninguna herramienta -> responde directo
    if parte.function_call is None:
        return respuesta.text

    # Caso 2: el modelo pide ejecutar una función
    llamada = parte.function_call
    nombre_funcion = llamada.name
    argumentos = llamada.args

    print(f"  [el modelo pidió llamar a: {nombre_funcion}({argumentos})]")

    funcion_real = funciones_disponibles[nombre_funcion]
    resultado_funcion = funcion_real(**argumentos)

    respuesta_final = client.models.generate_content(
        model="gemini-3.6-flash",
        contents=[
            types.Content(role="user", parts=[types.Part(text=pregunta)]),
            respuesta.candidates[0].content,  # turno del modelo pidiendo la función
            types.Content(
                role="user",
                parts=[types.Part.from_function_response(
                    name=nombre_funcion,
                    response={"resultado": resultado_funcion}
                )]
            ),
        ],
        config=types.GenerateContentConfig(tools=[tools])
    )

    return respuesta_final.text


# ---------- 5. Tres preguntas de prueba ----------

if __name__ == "__main__":
    preguntas = [
        "¿Cuánto es 15 más 27?",                     # debería activar sumar
        "¿Cuántas vocales tiene la palabra murciélago?",  # debería activar contar_vocales
        "¿De qué color es el cielo?",                 # no debería activar ninguna herramienta
    ]

    for p in preguntas:
        print(f"\nPregunta: {p}")
        print(f"Respuesta: {preguntar_con_herramientas(p)}")
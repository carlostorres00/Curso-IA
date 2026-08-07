#Versión definitiva con separación de ficheros
from gemini_client import preguntar_a_gemini
from pydantic import BaseModel

class Concepto(BaseModel):
    concepto: str
    definicion: str
    ejemplo: str

while True:

    nombre_prompt = input("Nombre del prompt: ")

    if nombre_prompt == "/salir":
        break

    if nombre_prompt == "/ayuda":
        print("Escribe el nombre de un archivo dentro de la carpeta prompts.")
        continue

    try:
        with open(f"prompts/{nombre_prompt}.txt", "r", encoding="utf-8") as archivo:
            prompt = archivo.read()

    except FileNotFoundError:
        print("Ese prompt no existe.")
        continue

    try:
        respuesta = preguntar_a_gemini(prompt)
        print(f"Concepto: {respuesta.concepto}")
        print(f"Definición: {respuesta.definicion}")
        print(f"Ejemplo: {respuesta.ejemplo}")

    except Exception as error:
        print(error)







#import os
#from dotenv import load_dotenv
#from google import genai

#load_dotenv()

#api_key = os.getenv("GEMINI_API_KEY")
#client = genai.Client(api_key=api_key)


''' Chat copiando el prompt
response = client.models.generate_content(model="gemini-3.6-flash",contents="Presentate en dos lineas")
print(response.text)
'''

''' Chat pregunta + Respuesta
pregunta = input("Qué quieres preguntar a Gemini?")
response = client.models.generate_content(
    model="gemini-3.6-flash",
    contents=pregunta)
print(response.text)
'''

''' Chat sin historial infinito hasta que sales
while True:
    pregunta = input("Que quieres preguntar a Gemini")
    if pregunta.lower() == "salir":
        print("¡Hasta luego!")
        break

    response = client.models.generate_content(model="gemini-3.6-flash", contents = pregunta)
    print(response.text)
'''

#historial = []
#system_prompt = """
#Eres un profesor de matemáticas.
#Responde siempre de forma muy breve.
#"""


''' Chat con historial hasta que sales
while True:
    pregunta = input('¿Que le quieres preguntar a Gemini?')

    if pregunta.lower() == "salir":
        break

    historial.append(f"Usuario: {pregunta}")

    response = client.models.generate_content(model='gemini-3.6-flash', contents=[system_prompt] + historial)
    print(response.text)
    historial.append(f"Gemini: {response.text}")
'''

'''
def preguntar_a_gemini(historial):
    response = client.models.generate_content(model="gemini-3.6-flash", contents=[system_prompt]+historial)
    return response.text

while True:
    pregunta = input('¿Que le quieres preguntar a Gemini?')
    if pregunta.lower() == 'salir':
        break
    historial.append(f"Usuario: {pregunta}")
    respuesta = preguntar_a_gemini(historial)
    print(respuesta)
    historial.append(f"Gemini: {respuesta}")
'''

#Versión definitiva con separación de ficheros
from gemini_client import preguntar_a_gemini

historial = []

while True:
    pregunta = input('¿Que le quieres preguntar a Gemini?')

    if pregunta.lower() == 'salir':
        break

    historial.append(f"Usuario: {pregunta}")
    respuesta = preguntar_a_gemini(historial)
    print(respuesta)
    historial.append(f"Gemini: {respuesta}")


import numpy as np
from google import genai
from google.genai import types
from dotenv import load_dotenv
import os

load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")


# Mismo client que ya usas en tu proyecto (con dotenv + api_key)
client = genai.Client(api_key=api_key)

def similitud_coseno(v1, v2) -> float:
    return np.dot(v1,v2) / (np.linalg.norm(v1) * np.linalg.norm(v2))

documentos = [
    "Me encanta cocinar pasta los domingos por la tarde",
    "El Real Madrid ganó el partido en el último minuto",
    "Estoy estudiando para el examen de álgebra lineal",
    "Python es un lenguaje de programación muy versátil",
    "Quiero viajar a Japón el próximo verano",
    "Ayer llovió muchísimo y se inundó la calle"]

query = "qué preparo de comer este fin de semana"

todos_los_textos = documentos + [query]

resultado = client.models.embed_content(
    model="gemini-embedding-001",
    contents=todos_los_textos,
    config=types.EmbedContentConfig(output_dimensionality=768)
)

vectores_documentos = [np.array(e.values) for e in resultado.embeddings[:-1]]
vector_query = np.array(resultado.embeddings[-1].values)

def buscar(vector_query, vectores_docs, docs):
    resultados = []
    #    resultados = [(doc, similitud_coseno(vector_query, vec)) for doc, vec in zip(docs, vectores_docs)]
    for i in range(len(docs)):
        resultados.append((docs[i], similitud_coseno(vector_query, vectores_docs[i])))
    resultados.sort(key=lambda x: x[1], reverse=True)
    return resultados

resultados = buscar(vector_query, vectores_documentos, documentos)
for texto, score in resultados:
    print(f"{score:.4f}  {texto}")  





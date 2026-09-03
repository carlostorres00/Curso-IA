from google import genai
from dotenv import load_dotenv
from google.genai import types
import os
import numpy as np


load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")
client = genai.Client(api_key=api_key)



def trocear_texto(texto: str, tamaño_chunk: int = 200, solapamiento: int = 40) -> list[str]:
    palabras = texto.split()
    chunks = []
    inicio = 0

    while inicio < len(palabras):
        chunk = palabras[inicio:inicio + tamaño_chunk]
        chunks.append(" ".join(chunk))

        inicio += tamaño_chunk - solapamiento

    return chunks

def similitud_coseno(v1, v2) -> float:
    return np.dot(v1,v2) / (np.linalg.norm(v1) * np.linalg.norm(v2))

def buscar(vector_query, vectores_docs, docs):
    resultados = []
    #    resultados = [(doc, similitud_coseno(vector_query, vec)) for doc, vec in zip(docs, vectores_docs)]
    for i in range(len(docs)):
        resultados.append((docs[i], similitud_coseno(vector_query, vectores_docs[i])))
    resultados.sort(key=lambda x: x[1], reverse=True)
    return resultados

texto = """CATEQUESIS 20/03: SEMANA SANTA

JUEGO INICAL

Yo creo que podemos explicar primero que queda poco para la Semana Santa y de nuevo, invitarles a que lo vivan allá donde vayan en Semana Santa, si se quedan aquí en Madrid, si se van a su pueblo a ver procesiones o lo que sea. Pero para ello tienen que entenderlo. Podemos explicar que es otro tiempo litúrgico, cuando empieza (Domingo de Ramos, hablamos aquí de esto porque ya luego empezamos con Triduo Pascual) Podríamos explicar el significado basándonos en el Credo
“padeció bajo el poder de Poncio Pilato
fue crucificado, muerto y sepultado,
descendió a los infiernos,
al tercer día resucitó de entre los muertos”
Y ya después de explicar todo el significado ver brevemente como se puede vivir y llevarlo a nuestra vida (Yo creo que casi lo más importante).

Padeció bajo el poder de Poncio Pilato (Antes de entrar aquí sería guay empezar con la Última Cena que también es importante jeje)
¿Qué ocurre antes de empezar Poncio Pilato? LA ÚLTIMA CENA 
¿Qué hizo Jesús en la última cena? ¿qué nos dijo? Jesús en la última cena se arrodilló a lavar los pies a uno de sus discípulos, y no solo eso sino que nos deja la Eucaristía. 
En la última cena Jesús instituye la Eucaristía, al convertir el pan en su cuerpo y el vino en su sangre, estando presente en ambas especies. Como el cuerpo físico necesita comida para no morir, el alma necesita alimento para la vida eterna. Al quedarse en forma de pan y vino , Jesús indica que quiere ser asimilado por nosotros, vivir dentro de nosotros .
Se hace pequeño, frágil y silencioso para no imponerse, sino para estar disponible. Es el gesto máximo de un Dios que, además de morir por la humanidad, decide no marcharse nunca y hacerse uno con el ser humano a través de la comunión.
Nos dijo: “ haced esto en memoria mía” iniciándonos a seguir su ejemplo, a seguir haciendo esos actos de servicio como el suyo de lavar los pies. (También institución del sacerdocio)

Cuando Jesús le llevan donde Pilato, Pilato sabía que Jesús era inocente, pero ¿que creéis q el sentiría en ese momento?  MIEDO, Pilato preferiría hacer lo que quería ver la gente y lavarse las manos que ir contra todo el mundo, Jesús fue traicionado por sus amigos y también por los que tenían poder.
Nosotros: ¿cuántas veces nos lavamos las manos? ¿Cuántas veces y en qué situaciones hemos hecho lo que quería que hicieran los demás a lo que tú querías hacer?

Fue crucificado, muerto y sepultado:
Muchas veces nos pensamos que la cruz es signo de derrota, sino que Dios nos ama hasta que incluso siendo el hijo De Dios, muere en la cruz por nosotros, se entrega con todo el sufrimiento, con todo el dolor y con el miedo, se entrega por nosotros, para salvarnos del pecado y de la muerte.
Todos tenemos una cruz en nuestra vida, una cosa que te pesa mucho y que te gustaría saber llevarla, no digo quitarla, sino aprender a vivir con ella dejando a un lado  el miedo, coger esa cruz y cargar en ella todas tus preocupaciones, todas las cosas que has hecho mal…
Que cada uno piense cuál es su cruz o sus cruces y piensen en cómo pueden aprender a llevarla.

Descendió a los infiernos:
El sábado santo fue un día de espera, un día de silencio, es el día en el que Dios estaba trabajando u nosotros no lo vemos. El hijo De Dios había fallecido y todos se dieron cuenta.
¿Cómo estaba la gente, como creéis que vivieron este día, que sentimientos tendrían tanto los apóstoles c9 como todos los que habían compartido momentos con el?
Yo creo q muchas veces en nuestra vida tenemos ese día, un día de silencio, en el que te pasa algo intentas buscar una respuesta en Dios y notas como que el no te responde, como que las cosas no avanzan 6 Dios te ignora, pero ahí es cuando tenemos que tener esa esperanza, darnos cuenta que aunque nosotros no lo veamos los planes De Dios son perfectos, que él está trabajando siempre, buscando nuestra felicidad.

Al tercer día resucitó de entre los muertos:
La muerte era la consecuencia del alejamiento de Dios (el pecado original). Al resucitar, Jesús rompe las cadenas de la muerte para toda la humanidad, abre las puertas del Cielo.
En el Antiguo Testamento, el tercer día suele ser el momento de la intervención salvadora de Dios (por ejemplo, Jonás en el vientre de la ballena o el sacrificio de Isaac). Jesús mismo lo predijo: Destruid este templo y en tres días lo levantaré"""



#EJEMPLO
""""
texto_trozo = trocear_texto(texto,100,20)

query = "¿qué sentimiento tuvo Pilato al saber que Jesús era inocente?"
resultado = client.models.embed_content(
    model="gemini-embedding-001",
    contents=texto_trozo + [query],
    config=types.EmbedContentConfig(output_dimensionality=768))

v = [np.array(e.values) for e in resultado.embeddings[:-1]]
q = np.array(resultado.embeddings[-1].values)

resultados = buscar(q, v, texto_trozo)
for texto, score in resultados[:3]:
    print(f"{score:.4f}  {texto}")
"""

def responder_rag(query, chunks, vectores_chunks):
    resultado_query = client.models.embed_content(
        model="gemini-embedding-001",
        contents=query,
        config=types.EmbedContentConfig(output_dimensionality=768)
    )
    vector_query = np.array(resultado_query.embeddings[0].values)
    resultado = buscar(vector_query, vectores_chunks, chunks)
    contexto = "\n\n".join(texto for texto, score in resultado[:3])

    prompt = f"""Contexto:
    {contexto}

    Pregunta: {query}

    Responde a la pregunta usando solo la información del contexto anterior. 
    Si el contexto no contiene la respuesta, dilo explícitamente en vez de inventar una respuesta."""

    respuesta = client.models.generate_content(model="gemini-3.6-flash",
                                               contents=prompt
                                               )
    return respuesta.text

texto_trozo = trocear_texto(texto,100,20)

resultado = client.models.embed_content(
    model="gemini-embedding-001",
    contents=texto_trozo,
    config=types.EmbedContentConfig(output_dimensionality=768))

v = [np.array(e.values) for e in resultado.embeddings]

# FASE 2 — responder preguntas (se puede repetir muchas veces sin re-indexar)
"""
query1 = "¿qué sentimiento tuvo Pilato al saber que Jesús era inocente?"
print(responder_rag(query1, texto_trozo, v))

query2 = "¿qué significa la Última Cena?"
print(responder_rag(query2, texto_trozo, v))
"""

query3 = "¿Cómo quedo el Barcelona vs Real Madrid de ayer?"
print(responder_rag(query3, texto_trozo, v))





from docx import Document #Obviamos analisis de imagenes en words


# leer_word.py
def procesar_docx(ruta_entrada, ruta_salida):
    doc = Document(ruta_entrada)
    texto = ""
    for parrafo in doc.paragraphs:
        texto += parrafo.text + "\n"

    with open(ruta_salida, "w", encoding="utf-8") as f:
        f.write(texto)

    return texto   # <-- la única línea nueva

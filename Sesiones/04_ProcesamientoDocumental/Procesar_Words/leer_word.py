from docx import Document #Obviamos analisis de imagenes en words


def procesar_docx(ruta_entrada, ruta_salida):
    """
    Extrae el texto de un archivo .docx y lo guarda en un .txt

    Args:
        ruta_entrada: ruta completa al archivo .docx a procesar
        ruta_salida: ruta completa donde guardar el .txt resultante
    """
    doc = Document(ruta_entrada)

    texto = ""
    for parrafo in doc.paragraphs:
        texto += parrafo.text + "\n"

    with open(ruta_salida, "w", encoding="utf-8") as f:
        f.write(texto)

import pymupdf
import os


'''ABRIR SOLO UN DOCUMENTO, NORMALMENTE QUEREMOS TODA UNA CARPETA
pdf_apuntes = pymupdf.open("Documentos/Apuntes.pdf")
#pagina = pdf[0]
#texto = pagina.get_text()

#print(texto)

#for paginas in pdf:
    #print(paginas.get_text())

apuntes = ""

for pagina in pdf_apuntes:
    apuntes += pagina.get_text() + "\n"
with open("texto_extraido.txt", "w", encoding="utf-8") as archivo:
    archivo.write(apuntes)

#print(pdf_apuntes.metadata)
print(pdf_apuntes.metadata.get("author"))
print(pdf_apuntes.metadata.get("title"))
print(pdf_apuntes.page_count)
'''

for archivo in os.listdir("Documentos"):
    pdf = pymupdf.open(f"Documentos/{archivo}")
    texto = ""
    for pagina in pdf:
        texto += pagina.get_text() + "\n"
    nombre_txt = archivo.replace(".pdf", ".txt")

    with open(f"textos/{nombre_txt}", "w", encoding="utf-8") as f:
        f.write(texto)
    pdf.close()


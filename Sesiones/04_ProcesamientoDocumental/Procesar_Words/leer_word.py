from docx import Document
import os
doc = Document("Documentos/Semana_Santa.docx")
'''
texto = ""
for parrafo in doc.paragraphs:
    texto += parrafo.text + "\n"

print(texto)
'''

for archivo in os.listdir("Documentos"):
    doc = Document(f"Documentos/{archivo}")
    texto = ""
    for parrafo in doc.paragraphs:
        texto += parrafo.text + "\n"
    nombre_txt = archivo.replace(".docx", ".txt")
    with open(f"textos/{nombre_txt}", "w", encoding="utf-8") as f:
        f.write(texto)

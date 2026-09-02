import os
import sys
import traceback

from OCR.todo_con_OCR import procesar_pdf
from Procesar_Words.leer_word import procesar_docx
from Procesar_Excel.leer_excel import procesar_excel


# --- Rutas absolutas basadas en la ubicación de este script ---
# Esto evita que el resultado dependa del "working directory" desde el
# que se ejecute main.py (terminal, botón Run del IDE, etc.)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DOCUMENTOS_DIR = os.path.join(BASE_DIR, "z_Docs_final")
TEXTOS_DIR = os.path.join(BASE_DIR, "z_text_final")

os.makedirs(TEXTOS_DIR, exist_ok=True)

if not os.path.isdir(DOCUMENTOS_DIR):
    sys.exit(
        f"ERROR: no existe la carpeta '{DOCUMENTOS_DIR}'.\n"
        f"Crea la carpeta 'Documentos' junto a main.py y coloca ahí los archivos a procesar."
    )

procesados = 0
no_soportados = 0
errores = []  # guardamos (archivo, excepción) en vez de solo contar

for archivo in os.listdir(DOCUMENTOS_DIR):

    ruta = os.path.join(DOCUMENTOS_DIR, archivo)

    if not os.path.isfile(ruta):
        continue  # ignora subcarpetas dentro de Documentos

    nombre_base, extension = os.path.splitext(archivo)
    extension = extension.lower()

    try:
        if extension == ".pdf":
            procesar_pdf(ruta, os.path.join(TEXTOS_DIR, nombre_base + ".txt"))
            procesados += 1

        elif extension == ".docx":
            procesar_docx(ruta, os.path.join(TEXTOS_DIR, nombre_base + ".txt"))
            procesados += 1

        elif extension == ".xlsx":
            procesar_excel(ruta, os.path.join(TEXTOS_DIR, nombre_base + ".txt"))
            procesados += 1

        else:
            print(f"Formato no soportado: {archivo}")
            no_soportados += 1

    except Exception as e:
        print(f"Error procesando {archivo}: {e}")
        errores.append((archivo, traceback.format_exc()))


print("\n==============================")
print("PROCESAMIENTO TERMINADO")
print("==============================")
print(f"Procesados: {procesados}")
print(f"No soportados: {no_soportados}")
print(f"Errores: {len(errores)}")

if errores:
    print("\n--- Detalle de errores ---")
    for archivo, tb in errores:
        print(f"\n>> {archivo}")
        print(tb)
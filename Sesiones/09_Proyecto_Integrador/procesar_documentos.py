"""
Fase A del proyecto integrador (Sesión 9).
"""

import os
import sys
import traceback
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

from modulos_procesamiento.todo_con_OCR import procesar_pdf
from modulos_procesamiento.leer_word import procesar_docx
from modulos_procesamiento.leer_excel import procesar_excel
from modulos_procesamiento.limpieza import limpiar_texto

DOCUMENTOS_DIR = BASE_DIR / "documentos"
TEXTOS_DIR = BASE_DIR / "z_text_final"  # texto crudo, igual que tu main.py original

TEXTOS_DIR.mkdir(exist_ok=True)


def procesar_carpeta(carpeta_documentos: str | Path = DOCUMENTOS_DIR) -> dict[str, str]:
    """
    Recorre `carpeta_documentos`, extrae texto con tus procesadores reales,
    lo limpia con limpieza.limpiar_texto, y devuelve:
        {nombre_archivo: texto_limpio}
    """
    carpeta = Path(carpeta_documentos)

    if not carpeta.is_dir():
        sys.exit(
            f"ERROR: no existe la carpeta '{carpeta}'.\n"
            f"Crea 'documentos/' junto a este script y coloca ahí los archivos."
        )

    resultados: dict[str, str] = {}
    no_soportados = 0
    errores: list[tuple[str, str]] = []

    for archivo in os.listdir(carpeta):
        ruta = carpeta / archivo
        if not ruta.is_file():
            continue

        nombre_base, extension = os.path.splitext(archivo)
        extension = extension.lower()
        ruta_txt_crudo = str(TEXTOS_DIR / (nombre_base + ".txt"))

        try:
            if extension == ".pdf":
                texto_crudo = procesar_pdf(str(ruta), ruta_txt_crudo)
            elif extension == ".docx":
                procesar_docx(str(ruta), ruta_txt_crudo)
                texto_crudo = Path(ruta_txt_crudo).read_text(encoding="utf-8")
            elif extension == ".xlsx":
                procesar_excel(str(ruta), ruta_txt_crudo)
                texto_crudo = Path(ruta_txt_crudo).read_text(encoding="utf-8")
            else:
                print(f"Formato no soportado: {archivo}")
                no_soportados += 1
                continue

            # --- el paso que faltaba conectar ---
            resultados[archivo] = limpiar_texto(texto_crudo)

        except Exception:
            errores.append((archivo, traceback.format_exc()))

    print("\n==============================")
    print("PROCESAMIENTO + LIMPIEZA TERMINADO")
    print("==============================")
    print(f"Procesados y limpios: {len(resultados)}")
    print(f"No soportados: {no_soportados}")
    print(f"Errores: {len(errores)}")

    if errores:
        print("\n--- Detalle de errores ---")
        for archivo, tb in errores:
            print(f"\n>> {archivo}")
            print(tb)

    return resultados


if __name__ == "__main__":
    textos = procesar_carpeta()
    for nombre, texto in textos.items():
        print(f"\n--- {nombre} ({len(texto.split())} palabras) ---")
        print(texto[:200], "...")
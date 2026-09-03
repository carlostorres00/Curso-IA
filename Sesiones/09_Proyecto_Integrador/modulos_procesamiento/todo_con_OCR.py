import io
import logging
import os
from typing import Optional

from PIL import Image
import pytesseract
import pymupdf

logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger(__name__)

# Umbrales para decidir si un OCR "merece" incorporarse al texto final.
# Ajustables según el tipo de documento con el que trabajes.
OCR_MIN_CONFIDENCE = 40.0  # confianza media de Tesseract (0-100)
OCR_MIN_CHARS = 3          # longitud mínima del texto reconocido
OCR_MIN_PIXELS = 30        # ancho/alto mínimo en píxeles (descarta iconos/adornos)

os.makedirs("textos", exist_ok=True)


def guardar_texto(texto: str, nombre_txt: str) -> None:
    ruta_salida = os.path.join("textos", nombre_txt)
    with open(ruta_salida, "w", encoding="utf-8") as f:
        f.write(texto)


def hacer_ocr(imagen: Image.Image) -> tuple[str, float]:
    """Ejecuta OCR sobre una imagen y devuelve (texto, confianza_media).

    Una sola llamada a Tesseract: image_to_data ya devuelve, palabra a
    palabra, tanto el texto reconocido como su confianza, así que no hace
    falta una segunda pasada con image_to_string sobre la misma imagen."""
    if imagen.mode not in ("RGB", "L"):
        imagen = imagen.convert("RGB")

    datos = pytesseract.image_to_data(
        imagen, lang="spa", output_type=pytesseract.Output.DICT
    )

    # Agrupamos las palabras por línea (block_num, par_num, line_num) para
    # reconstruir el texto con sus saltos de línea, igual que hacía
    # image_to_string, pero sin volver a correr el OCR.
    lineas: dict[tuple[int, int, int], list[str]] = {}
    confianzas = []

    for i, palabra in enumerate(datos["text"]):
        conf = float(datos["conf"][i])
        if conf >= 0:
            confianzas.append(conf)

        palabra = palabra.strip()
        if not palabra:
            continue

        clave_linea = (datos["block_num"][i], datos["par_num"][i], datos["line_num"][i])
        lineas.setdefault(clave_linea, []).append(palabra)

    texto = "\n".join(" ".join(palabras) for palabras in lineas.values()).strip()
    confianza_media = sum(confianzas) / len(confianzas) if confianzas else 0.0

    return texto, confianza_media


def ocr_merece_incorporarse(texto: str, confianza: float, imagen: Image.Image) -> bool:
    """Decide si el resultado de un OCR es lo bastante fiable como para
    añadirlo al texto final, en lugar de aceptar cualquier resultado no vacío."""
    if imagen.width < OCR_MIN_PIXELS or imagen.height < OCR_MIN_PIXELS:
        return False
    if len(texto) < OCR_MIN_CHARS:
        return False
    if confianza < OCR_MIN_CONFIDENCE:
        return False
    return True


def procesar_pdf(ruta: str, nombre_txt: str) -> Optional[str]:
    """Extrae texto (digital + OCR) de un PDF conservando el orden real
    de aparición de texto e imágenes."""
    try:
        pdf = pymupdf.open(ruta)
    except Exception as e:
        logger.error(f"No se pudo abrir el PDF '{ruta}': {e}")
        return None

    texto_completo = ""

    try:
        for pagina in pdf:
            try:
                # sort=True ordena los bloques en orden de lectura (arriba->abajo, izq->dcha)
                contenido = pagina.get_text("dict", sort=True)
            except Exception as e:
                logger.error(f"Error extrayendo contenido de la página {pagina.number + 1}: {e}")
                continue

            for bloque in contenido.get("blocks", []):
                tipo = bloque.get("type")

                if tipo == 0:  # bloque de texto digital
                    lineas = []
                    for linea in bloque.get("lines", []):
                        texto_linea = "".join(
                            span["text"] for span in linea.get("spans", [])
                        )
                        if texto_linea:
                            lineas.append(texto_linea)

                    # Las líneas se unen con espacio: un salto de línea dentro
                    # de un bloque (ya sea texto que envuelve o una celda de
                    # tabla nativa) no lleva un carácter de espacio real en el
                    # PDF, así que hay que reponerlo nosotros.
                    texto_bloque = " ".join(lineas)
                    if texto_bloque.strip():
                        texto_completo += texto_bloque + "\n"

                elif tipo == 1:  # bloque de imagen
                    try:
                        imagen = Image.open(io.BytesIO(bloque["image"]))
                    except Exception as e:
                        logger.warning(f"No se pudo decodificar una imagen: {e}")
                        continue

                    try:
                        texto_ocr, confianza = hacer_ocr(imagen)
                    except Exception as e:
                        logger.warning(f"Falló el OCR sobre una imagen: {e}")
                        continue

                    if ocr_merece_incorporarse(texto_ocr, confianza, imagen):
                        texto_completo += texto_ocr + "\n"
    finally:
        pdf.close()

    guardar_texto(texto_completo, nombre_txt)

    return texto_completo


if __name__ == "__main__":
    procesar_pdf("Documentos/ejemplo_ocr.pdf", "ejemplo_ocr.txt")
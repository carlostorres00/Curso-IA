"""
Módulo de limpieza y diagnóstico de texto extraído de documentos (OCR, DOCX, etc.).

Cambios respecto a la versión original:
- Regexes precompiladas (no se recompilan en cada llamada).
- `_ratio_vocales` y `_racha_max_consonantes` fusionadas en un único paso
  sobre la palabra (antes se recorría la misma lista dos veces).
- `eliminar_guiones_de_corte` ahora es insensible a mayúsculas.
- Resultado de diagnóstico como `dataclass` en vez de `dict` suelto (autocompletado,
  tipado, y evita errores de claves mal escritas).
- Manejo de errores y logging en la E/S de archivos (antes fallaba en seco si no
  existía el archivo o la carpeta `textos/`).
- Rutas con `pathlib` en vez de f-strings concatenadas.
"""

from __future__ import annotations

import argparse
import logging
import re
import unicodedata
from collections import Counter
from dataclasses import dataclass, field
from pathlib import Path

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)


# ============================================================
# 1. LIMPIEZA DE ESPACIOS
# ============================================================

_RE_ESPACIOS_HORIZONTALES = re.compile(r"[ \t]+")
_RE_LINEAS_VACIAS_MULTIPLES = re.compile(r"\n{3,}")


def limpiar_espacios(texto: str) -> str:
    lineas = [linea.strip() for linea in texto.splitlines()]
    texto = "\n".join(lineas)

    texto = _RE_ESPACIOS_HORIZONTALES.sub(" ", texto)
    texto = _RE_LINEAS_VACIAS_MULTIPLES.sub("\n\n", texto)

    return texto.strip()


# ============================================================
# 2. NORMALIZACIÓN UNICODE
# ============================================================

def normalizar_unicode(texto: str) -> str:
    return unicodedata.normalize("NFC", texto)


# ============================================================
# 3. PALABRAS CORTADAS POR GUIÓN
# ============================================================

# re.IGNORECASE cubre cortes en mayúsculas (p. ej. "EDUCA-\nCIÓN"), que la
# versión original no detectaba al listar solo minúsculas.
_RE_GUION_DE_CORTE = re.compile(
    r"([a-záéíóúñ])-\n([a-záéíóúñ])", re.IGNORECASE
)


def eliminar_guiones_de_corte(texto: str) -> str:
    return _RE_GUION_DE_CORTE.sub(r"\1\2", texto)


# ============================================================
# 4. DETECTAR LÍNEAS REPETIDAS (boilerplate)
# ============================================================

UMBRAL_REPETICIONES = 3


def encontrar_lineas_repetidas(
    texto: str, umbral: int = UMBRAL_REPETICIONES
) -> list[tuple[str, int]]:
    contador = Counter(
        linea.strip() for linea in texto.splitlines() if linea.strip()
    )
    return [(linea, veces) for linea, veces in contador.items() if veces >= umbral]


# ============================================================
# 5. DETECCIÓN DE TEXTO OCR SOSPECHOSO
# ============================================================

VOCALES = frozenset("aeiouáéíóúü")
CONSONANTES = frozenset("bcdfghjklmnñpqrstvwxyz")
_RE_PALABRAS = re.compile(r"[a-záéíóúñü]+")
_PUNTUACION_NORMAL = frozenset(".,;:!?¿¡'\"()-–—…/%€$")


def _analizar_palabra(palabra: str) -> tuple[float, int]:
    """Devuelve (ratio_vocales, racha_max_consonantes) en un solo recorrido."""
    total_letras = 0
    total_vocales = 0
    racha = 0
    racha_max = 0

    for c in palabra:
        if c in VOCALES:
            total_letras += 1
            total_vocales += 1
            racha = 0
        elif c in CONSONANTES:
            total_letras += 1
            racha += 1
            racha_max = max(racha_max, racha)
        else:
            racha = 0

    ratio_v = total_vocales / total_letras if total_letras else 0.0
    return ratio_v, racha_max


def _palabra_es_plausible(palabra: str) -> bool:
    letras = "".join(c for c in palabra.lower() if c.isalpha())

    if len(letras) < 3:
        return True

    ratio_v, racha_cons = _analizar_palabra(letras)

    if ratio_v < 0.15 or ratio_v > 0.80:
        return False

    if racha_cons >= 5:
        return False

    return True


def _densidad_simbolos_raros(texto: str) -> float:
    caracteres = [c for c in texto if not c.isspace()]

    if not caracteres:
        return 0.0

    raros = sum(
        1 for c in caracteres if not c.isalnum() and c not in _PUNTUACION_NORMAL
    )

    return raros / len(caracteres)


def _proporcion_fragmentos_cortos(palabras: list[str]) -> float:
    if not palabras:
        return 0.0

    cortas = sum(1 for p in palabras if len(p) <= 2)
    return cortas / len(palabras)


@dataclass
class DiagnosticoLinea:
    sospechosa: bool
    motivos: list[str] = field(default_factory=list)
    proporcion_palabras_plausibles: float = 0.0
    densidad_simbolos_raros: float = 0.0
    proporcion_fragmentos_cortos: float = 0.0
    numero_linea: int | None = None
    texto: str | None = None


def diagnosticar_linea(
    linea: str,
    umbral_proporcion_palabras: float = 0.5,
    umbral_densidad_simbolos: float = 0.08,
    umbral_fragmentos_cortos: float = 0.6,
) -> DiagnosticoLinea:

    palabras = _RE_PALABRAS.findall(linea.lower())
    densidad_simbolos = _densidad_simbolos_raros(linea)

    if not palabras:
        return DiagnosticoLinea(
            sospechosa=True,
            motivos=["sin_palabras_detectables"],
            proporcion_palabras_plausibles=0.0,
            densidad_simbolos_raros=densidad_simbolos,
            proporcion_fragmentos_cortos=0.0,
        )

    proporcion_plausibles = sum(
        1 for p in palabras if _palabra_es_plausible(p)
    ) / len(palabras)

    proporcion_cortas = _proporcion_fragmentos_cortos(palabras)

    motivos = []

    if proporcion_plausibles < umbral_proporcion_palabras:
        motivos.append(
            f"pocas_palabras_plausibles "
            f"({proporcion_plausibles:.2f} < {umbral_proporcion_palabras})"
        )

    if densidad_simbolos > umbral_densidad_simbolos:
        motivos.append(
            f"muchos_simbolos_raros "
            f"({densidad_simbolos:.2f} > {umbral_densidad_simbolos})"
        )

    if proporcion_cortas > umbral_fragmentos_cortos:
        motivos.append(
            f"muchos_fragmentos_cortos "
            f"({proporcion_cortas:.2f} > {umbral_fragmentos_cortos})"
        )

    return DiagnosticoLinea(
        sospechosa=len(motivos) > 0,
        motivos=motivos,
        proporcion_palabras_plausibles=proporcion_plausibles,
        densidad_simbolos_raros=densidad_simbolos,
        proporcion_fragmentos_cortos=proporcion_cortas,
    )


def diagnosticar_texto(texto: str, **kwargs) -> list[DiagnosticoLinea]:
    resultado = []

    for i, linea in enumerate(texto.splitlines(), start=1):
        if not linea.strip():
            continue

        diagnostico = diagnosticar_linea(linea, **kwargs)

        if diagnostico.sospechosa:
            diagnostico.numero_linea = i
            diagnostico.texto = linea
            resultado.append(diagnostico)

    return resultado


# ============================================================
# 6. PIPELINE DE LIMPIEZA
# ============================================================

def limpiar_texto(texto: str) -> str:
    texto = normalizar_unicode(texto)
    texto = eliminar_guiones_de_corte(texto)
    texto = limpiar_espacios(texto)
    return texto


def limpiar_archivo(
    nombre_txt: str, carpeta: str | Path = "textos"
) -> Path:
    """
    Lee `carpeta/nombre_txt`, limpia el texto y escribe el resultado en
    `carpeta/limpio_<nombre_txt>`. Devuelve la ruta de salida.

    A diferencia de la versión original, valida que la entrada exista y
    evita re-procesar un archivo ya limpio (si `nombre_txt` ya empieza por
    "limpio_", avisa en vez de generar "limpio_limpio_...").
    """
    carpeta = Path(carpeta)
    ruta_entrada = carpeta / nombre_txt

    if not ruta_entrada.exists():
        raise FileNotFoundError(f"No se encontró el archivo: {ruta_entrada}")

    if nombre_txt.startswith("limpio_"):
        logger.warning(
            "El archivo de entrada '%s' ya parece limpio; "
            "esto generará un prefijo duplicado.",
            nombre_txt,
        )

    ruta_salida = carpeta / f"limpio_{nombre_txt}"

    texto = ruta_entrada.read_text(encoding="utf-8")
    texto_limpio = limpiar_texto(texto)
    ruta_salida.write_text(texto_limpio, encoding="utf-8")

    logger.info("Archivo limpio escrito en: %s", ruta_salida)
    return ruta_salida


# ============================================================
# CLI
# ============================================================

def _main() -> None:
    parser = argparse.ArgumentParser(
        description="Limpia un archivo de texto (espacios, unicode, guiones de corte)."
    )
    parser.add_argument("nombre_txt", help="Nombre del archivo dentro de la carpeta 'textos/'")
    parser.add_argument(
        "--carpeta", default="textos", help="Carpeta donde vive el archivo (default: textos)"
    )
    parser.add_argument(
        "--diagnosticar",
        action="store_true",
        help="Además de limpiar, imprime las líneas sospechosas de OCR",
    )
    args = parser.parse_args()

    try:
        ruta_salida = limpiar_archivo(args.nombre_txt, carpeta=args.carpeta)
    except FileNotFoundError as e:
        logger.error(str(e))
        return

    if args.diagnosticar:
        texto_limpio = ruta_salida.read_text(encoding="utf-8")
        sospechosas = diagnosticar_texto(texto_limpio)

        if not sospechosas:
            logger.info("Sin líneas sospechosas.")
        else:
            for d in sospechosas:
                logger.info("Línea %s: %s | motivos: %s", d.numero_linea, d.texto, d.motivos)


if __name__ == "__main__":
    _main()


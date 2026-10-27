"""Ejecuta la aplicación como caja negra (como lo haría un usuario).

Cada escenario es un archivo con las teclas que escribiría el usuario, una por línea.
Se captura todo lo que la aplicación imprime y el contenido final de datos.json.
Ese par (salida + datos) es el "comportamiento externo" que el refactoring no debe romper.
"""
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

RAIZ_PROYECTO = Path(__file__).resolve().parents[2]
APP = RAIZ_PROYECTO / "app.py"
CARPETA = Path(__file__).resolve().parent
ESCENARIOS = CARPETA / "escenarios"
ESPERADO = CARPETA / "esperado"


def listar_escenarios():
    return sorted(p.stem for p in ESCENARIOS.glob("*.txt"))


def normalizar_datos(datos):
    """La fecha de alta depende del día de ejecución: se reemplaza por un marcador
    salvo en las solicitudes que ya venían cargadas en el archivo inicial."""
    for solicitud in datos.get("solicitudes", []):
        if solicitud.get("fecha", "").startswith("2026-09"):
            continue
        solicitud["fecha"] = "<FECHA_DE_ALTA>"
    return datos


def ejecutar(nombre_escenario):
    entrada = (ESCENARIOS / f"{nombre_escenario}.txt").read_text(encoding="utf-8")
    datos_iniciales = ESCENARIOS / f"{nombre_escenario}.datos_iniciales.json"
    with tempfile.TemporaryDirectory() as carpeta_temporal:
        if datos_iniciales.exists():
            shutil.copy(datos_iniciales, Path(carpeta_temporal) / "datos.json")
        resultado = subprocess.run(
            [sys.executable, str(APP)],
            input=entrada,
            capture_output=True,
            text=True,
            cwd=carpeta_temporal,
            timeout=10,
        )
        archivo_datos = Path(carpeta_temporal) / "datos.json"
        datos = json.loads(archivo_datos.read_text(encoding="utf-8")) if archivo_datos.exists() else None
    return resultado.stdout, normalizar_datos(datos) if datos else None

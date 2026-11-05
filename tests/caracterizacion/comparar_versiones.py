"""Evidencia antes/después: ejecuta cada escenario sobre la versión inicial y la actual.

La versión inicial se extrae del tag `estado-inicial` a una carpeta temporal,
así que no hace falta hacer checkout ni salir de la rama main.

Uso:  python -m tests.caracterizacion.comparar_versiones
"""
import subprocess
import sys
import tempfile
from pathlib import Path

from tests.caracterizacion.ejecutor import APP, RAIZ_PROYECTO, ejecutar, listar_escenarios


def extraer_version_inicial(destino: Path) -> Path:
    codigo = subprocess.run(
        ["git", "show", "estado-inicial:app.py"],
        cwd=RAIZ_PROYECTO, capture_output=True, text=True, encoding="utf-8", check=True,
    ).stdout
    app_inicial = destino / "app.py"
    app_inicial.write_text(codigo, encoding="utf-8")
    return app_inicial


def main() -> int:
    with tempfile.TemporaryDirectory() as carpeta:
        app_inicial = extraer_version_inicial(Path(carpeta))
        print(f"{'Escenario':<28}{'Salida en pantalla':<22}{'datos.json':<14}")
        print("-" * 64)
        diferencias = 0
        for escenario in listar_escenarios():
            salida_antes, datos_antes = ejecutar(escenario, app_inicial)
            salida_despues, datos_despues = ejecutar(escenario, APP)
            misma_salida = salida_antes == salida_despues
            mismos_datos = datos_antes == datos_despues
            diferencias += (not misma_salida) + (not mismos_datos)
            print(
                f"{escenario:<28}"
                f"{'IGUAL' if misma_salida else 'DISTINTA':<22}"
                f"{'IGUAL' if mismos_datos else 'DISTINTO':<14}"
            )
        print("-" * 64)
        print("Sin diferencias." if diferencias == 0 else f"{diferencias} diferencia(s).")
        return 0 if diferencias == 0 else 1


if __name__ == "__main__":
    sys.exit(main())

"""Graba la salida "aprobada" de cada escenario.

Se ejecutó UNA sola vez sobre la versión inicial (tag estado-inicial), antes de refactorizar.
No volver a correrlo durante el refactoring: si lo hacés, estarías aprobando el
comportamiento nuevo en lugar de compararlo contra el original.

Uso: python -m tests.caracterizacion.generar_esperado
"""
import json

from tests.caracterizacion.ejecutor import ESPERADO, ejecutar, listar_escenarios

if __name__ == "__main__":
    ESPERADO.mkdir(exist_ok=True)
    for nombre in listar_escenarios():
        salida, datos = ejecutar(nombre)
        (ESPERADO / f"{nombre}.salida.txt").write_text(salida, encoding="utf-8")
        (ESPERADO / f"{nombre}.datos.json").write_text(
            json.dumps(datos, indent=2, ensure_ascii=False), encoding="utf-8"
        )
        print(f"grabado: {nombre}")

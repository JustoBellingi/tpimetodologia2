"""Re-graba UN escenario cuando un cambio de comportamiento fue revisado y aprobado.

A diferencia de generar_esperado.py (que graba todo), este script muestra la
diferencia contra lo grabado y la guarda en docs/evidencias/ antes de aprobarla.
Solo debe usarse para cambios intencionales documentados en el code review.

Uso:  python -m tests.caracterizacion.aprobar_cambio 03_reglas_estado C1
"""
import difflib
import json
import sys

from tests.caracterizacion.ejecutor import ESPERADO, RAIZ_PROYECTO, ejecutar


def lineas(texto):
    # El prompt del menu y la respuesta quedan en la misma linea: se separan para leer mejor el diff.
    return texto.replace("Opcion: ", "Opcion: \n").splitlines()


def main(escenario, codigo_cambio):
    salida, datos = ejecutar(escenario)
    archivo_salida = ESPERADO / f"{escenario}.salida.txt"
    diferencia = list(difflib.unified_diff(
        lineas(archivo_salida.read_text(encoding="utf-8")), lineas(salida),
        f"{escenario} (antes)", f"{escenario} (despues)", n=1, lineterm="",
    ))
    evidencia = RAIZ_PROYECTO / "docs" / "evidencias" / f"{codigo_cambio}_{escenario}.diff"
    evidencia.write_text("\n".join(diferencia) + "\n", encoding="utf-8")
    archivo_salida.write_text(salida, encoding="utf-8")
    (ESPERADO / f"{escenario}.datos.json").write_text(
        json.dumps(datos, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    print(f"Aprobado {escenario}. Diferencia guardada en {evidencia.relative_to(RAIZ_PROYECTO)}")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])

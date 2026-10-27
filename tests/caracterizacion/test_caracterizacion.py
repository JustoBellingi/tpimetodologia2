"""Tests de caracterización (golden master).

Comparan la versión actual contra lo que hacía la versión inicial,
escenario por escenario: misma salida en pantalla y mismo archivo de datos.
"""
import json

import pytest

from tests.caracterizacion.ejecutor import ESPERADO, ejecutar, listar_escenarios


@pytest.mark.parametrize("escenario", listar_escenarios())
def test_la_salida_por_pantalla_no_cambia(escenario):
    salida, _ = ejecutar(escenario)
    esperado = (ESPERADO / f"{escenario}.salida.txt").read_text(encoding="utf-8")
    assert salida == esperado


@pytest.mark.parametrize("escenario", listar_escenarios())
def test_el_archivo_de_datos_no_cambia(escenario):
    _, datos = ejecutar(escenario)
    esperado = json.loads((ESPERADO / f"{escenario}.datos.json").read_text(encoding="utf-8"))
    assert datos == esperado

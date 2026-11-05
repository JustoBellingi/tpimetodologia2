"""Mejoras de comportamiento intencionales respecto de la versión inicial."""
from solicitudes.consola import Consola
from solicitudes.repositorio import RESPONSABLES_POR_DEFECTO, CatalogoResponsables, RepositorioEnMemoria
from solicitudes.servicio import ServicioSolicitudes, generar_reporte


def ejecutar_consola(entradas):
    pendientes = iter(entradas)
    salida = []

    def leer(prompt):
        try:
            return next(pendientes)
        except StopIteration:
            raise EOFError from None

    catalogo = CatalogoResponsables(RESPONSABLES_POR_DEFECTO)
    repositorio = RepositorioEnMemoria()
    consola = Consola(ServicioSolicitudes(repositorio, catalogo), lambda: generar_reporte(repositorio), leer, salida.append)
    consola.ejecutar()
    return salida


def test_id_no_numerico_da_un_mensaje_claro():
    # Versión inicial: "Ocurrio un error" (except genérico).
    salida = ejecutar_consola(["2", "abc", "0"])
    assert "Error: el ID debe ser numerico" in salida


def test_fin_de_entrada_termina_ordenadamente():
    # Versión inicial: el programa terminaba con un traceback de Python.
    salida = ejecutar_consola(["5"])
    assert salida[-1] == "Hasta luego"


def test_asignar_a_un_id_inexistente_falla_antes_de_pedir_el_responsable():
    # Version inicial: pedia el codigo de responsable y recien despues avisaba el error.
    salida = ejecutar_consola(["3", "99", "0"])
    assert "Error: no existe la solicitud 99" in salida
    assert not any("Ana Gomez" in linea for linea in salida)


def test_cambiar_estado_de_un_id_inexistente_falla_antes_de_pedir_el_estado():
    salida = ejecutar_consola(["2", "99", "0"])
    assert "Error: no existe la solicitud 99" in salida
    assert "Estados: 1-En proceso 2-Resuelta 3-Rechazada" not in salida

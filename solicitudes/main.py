"""Punto de armado: acá (y solo acá) se eligen las implementaciones concretas."""
from pathlib import Path

from solicitudes.consola import Consola
from solicitudes.repositorio import RESPONSABLES_POR_DEFECTO, CatalogoResponsables, RepositorioJSON
from solicitudes.servicio import ServicioSolicitudes, generar_reporte

ARCHIVO_DE_DATOS = Path("datos.json")


def main() -> None:
    catalogo = CatalogoResponsables(RESPONSABLES_POR_DEFECTO)
    repositorio = RepositorioJSON(ARCHIVO_DE_DATOS, catalogo)
    servicio = ServicioSolicitudes(repositorio, catalogo)
    Consola(servicio, reporte=lambda: generar_reporte(repositorio)).ejecutar()

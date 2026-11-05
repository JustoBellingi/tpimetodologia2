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
    avisos = []
    if repositorio.respaldo_de_archivo_danado:
        avisos.append(
            f"Aviso: {ARCHIVO_DE_DATOS} no se pudo leer. Se guardo una copia en "
            f"{repositorio.respaldo_de_archivo_danado} y se empieza con datos vacios."
        )
    Consola(servicio, reporte=lambda: generar_reporte(repositorio)).ejecutar(avisos)

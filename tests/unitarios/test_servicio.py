"""El servicio se prueba con las DOS implementaciones del repositorio:
si ambas pasan los mismos tests, son intercambiables (Liskov)."""
from datetime import date

import pytest

from solicitudes.dominio import (
    DatosSolicitud, Estado, Estudiante, Prioridad, ResponsableInexistente,
    SolicitudInexistente, TipoSolicitud,
)
from solicitudes.filtros import PorEstado, PorLegajo, PorTipo
from solicitudes.repositorio import (
    RESPONSABLES_POR_DEFECTO, CatalogoResponsables, RepositorioEnMemoria, RepositorioJSON,
)
from solicitudes.servicio import ServicioSolicitudes, generar_reporte

CATALOGO = CatalogoResponsables(RESPONSABLES_POR_DEFECTO)
HOY = date(2026, 10, 27)


@pytest.fixture(params=["memoria", "json"])
def repositorio(request, tmp_path):
    if request.param == "memoria":
        return RepositorioEnMemoria()
    return RepositorioJSON(tmp_path / "datos.json", CATALOGO)


@pytest.fixture
def servicio(repositorio):
    return ServicioSolicitudes(repositorio, CATALOGO, hoy=lambda: HOY)


def datos(legajo="1001", tipo=TipoSolicitud.CERTIFICADO, prioridad=Prioridad.ALTA):
    return DatosSolicitud(Estudiante("Juan", legajo, "j@m.com"), tipo, "desc", prioridad)


def test_registrar_asigna_ids_consecutivos_y_la_fecha_del_reloj(servicio):
    primera = servicio.registrar(datos())
    segunda = servicio.registrar(datos())
    assert (primera.id, segunda.id) == (1, 2)
    assert primera.fecha_alta == HOY


def test_asignar_y_avanzar_estado(servicio):
    servicio.registrar(datos())
    responsable = servicio.asignar_responsable(1, "r2")
    servicio.cambiar_estado(1, Estado.EN_PROCESO)
    assert responsable.nombre == "Luis Perez"
    assert servicio.obtener(1).estado is Estado.EN_PROCESO


def test_errores_de_ids_y_codigos_inexistentes(servicio):
    with pytest.raises(SolicitudInexistente):
        servicio.cambiar_estado(99, Estado.EN_PROCESO)
    servicio.registrar(datos())
    with pytest.raises(ResponsableInexistente):
        servicio.asignar_responsable(1, "R9")


def test_buscar_con_distintos_filtros(servicio):
    servicio.registrar(datos(legajo="1"))
    servicio.registrar(datos(legajo="2", tipo=TipoSolicitud.RECLAMO_NOTA))
    assert [s.id for s in servicio.buscar(PorLegajo("2"))] == [2]
    assert [s.id for s in servicio.buscar(PorTipo(TipoSolicitud.CERTIFICADO))] == [1]
    assert len(servicio.buscar(PorEstado(Estado.PENDIENTE))) == 2


def test_reporte_cuenta_por_estado_tipo_y_pendientes_de_alta(servicio, repositorio):
    servicio.registrar(datos(prioridad=Prioridad.ALTA))
    servicio.registrar(datos(prioridad=Prioridad.BAJA, tipo=TipoSolicitud.EQUIVALENCIA))
    reporte = generar_reporte(repositorio)
    assert reporte.total == 2
    assert reporte.por_estado[Estado.PENDIENTE] == 2
    assert reporte.por_tipo[TipoSolicitud.EQUIVALENCIA] == 1
    assert [s.id for s in reporte.pendientes_alta] == [1]


def test_el_repositorio_json_recupera_lo_guardado(tmp_path):
    ruta = tmp_path / "datos.json"
    servicio = ServicioSolicitudes(RepositorioJSON(ruta, CATALOGO), CATALOGO, hoy=lambda: HOY)
    servicio.registrar(datos())
    servicio.asignar_responsable(1, "R3")
    recargado = RepositorioJSON(ruta, CATALOGO).obtener(1)
    assert recargado.responsable.area == "Tesoreria"
    assert recargado.fecha_alta == HOY

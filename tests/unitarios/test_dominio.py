import pytest

from solicitudes.dominio import (
    DatosSolicitud, Estado, Estudiante, Prioridad, Responsable, Solicitud,
    TipoSolicitud, TransicionInvalida,
)
from datetime import date

RESPONSABLE = Responsable("R1", "Ana Gomez", "Alumnos")


def solicitud_nueva():
    datos = DatosSolicitud(Estudiante("Juan", "1001", "j@m.com"), TipoSolicitud.CERTIFICADO, "desc", Prioridad.ALTA)
    return Solicitud.nueva(1, datos, date(2026, 10, 1))


def test_una_solicitud_nueva_arranca_pendiente_y_sin_responsable():
    solicitud = solicitud_nueva()
    assert solicitud.estado is Estado.PENDIENTE
    assert solicitud.responsable is None


def test_no_pasa_a_en_proceso_sin_responsable():
    with pytest.raises(TransicionInvalida, match="debe tener responsable"):
        solicitud_nueva().cambiar_estado(Estado.EN_PROCESO)


def test_flujo_feliz_pendiente_en_proceso_resuelta():
    solicitud = solicitud_nueva()
    solicitud.asignar_responsable(RESPONSABLE)
    solicitud.cambiar_estado(Estado.EN_PROCESO)
    solicitud.cambiar_estado(Estado.RESUELTA)
    assert solicitud.estado is Estado.RESUELTA


def test_no_se_puede_resolver_sin_pasar_por_en_proceso():
    with pytest.raises(TransicionInvalida, match="de PENDIENTE a RESUELTA"):
        solicitud_nueva().cambiar_estado(Estado.RESUELTA)


@pytest.mark.parametrize("estado_final", [Estado.RESUELTA, Estado.RECHAZADA])
def test_una_solicitud_cerrada_no_se_modifica(estado_final):
    solicitud = solicitud_nueva()
    solicitud.estado = estado_final
    with pytest.raises(TransicionInvalida, match="cerrada"):
        solicitud.cambiar_estado(Estado.EN_PROCESO)
    with pytest.raises(TransicionInvalida, match="cerrada"):
        solicitud.asignar_responsable(RESPONSABLE)


def test_estado_se_reconstruye_desde_su_codigo_de_archivo():
    assert Estado.desde_codigo("X") is Estado.RECHAZADA
    with pytest.raises(ValueError):
        Estado.desde_codigo("Z")

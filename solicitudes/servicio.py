"""Casos de uso del sistema. Coordina dominio y persistencia; no imprime nada."""
from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from datetime import date
from typing import Callable

from solicitudes.dominio import (
    DatosSolicitud,
    Estado,
    Responsable,
    ResponsableInexistente,
    Solicitud,
    SolicitudInexistente,
    TipoSolicitud,
)
from solicitudes.filtros import Filtro, PendientesDePrioridadAlta
from solicitudes.repositorio import (
    CatalogoResponsables,
    FuenteDeSolicitudes,
    RepositorioSolicitudes,
)


class ServicioSolicitudes:
    def __init__(
        self,
        repositorio: RepositorioSolicitudes,
        catalogo: CatalogoResponsables,
        hoy: Callable[[], date] = date.today,
    ):
        self._repositorio = repositorio
        self._catalogo = catalogo
        self._hoy = hoy

    def registrar(self, datos: DatosSolicitud) -> Solicitud:
        solicitud = Solicitud.nueva(self._repositorio.proximo_id(), datos, self._hoy())
        self._repositorio.guardar(solicitud)
        return solicitud

    def obtener(self, id_solicitud: int) -> Solicitud:
        solicitud = self._repositorio.obtener(id_solicitud)
        if solicitud is None:
            raise SolicitudInexistente(id_solicitud)
        return solicitud

    def cambiar_estado(self, id_solicitud: int, nuevo_estado: Estado) -> Solicitud:
        solicitud = self.obtener(id_solicitud)
        solicitud.cambiar_estado(nuevo_estado)
        self._repositorio.guardar(solicitud)
        return solicitud

    def asignar_responsable(self, id_solicitud: int, codigo_responsable: str) -> Responsable:
        solicitud = self.obtener(id_solicitud)
        solicitud.verificar_que_esta_abierta()
        responsable = self._catalogo.buscar(codigo_responsable)
        if responsable is None:
            raise ResponsableInexistente(codigo_responsable)
        solicitud.asignar_responsable(responsable)
        self._repositorio.guardar(solicitud)
        return responsable

    def buscar(self, filtro: Filtro) -> list[Solicitud]:
        return [s for s in self._repositorio.listar() if filtro.cumple(s)]

    def responsables(self) -> list[Responsable]:
        return self._catalogo.todos()


@dataclass(frozen=True)
class Reporte:
    total: int
    por_estado: dict[Estado, int]
    por_tipo: dict[TipoSolicitud, int]
    pendientes_alta: list[Solicitud]


def generar_reporte(fuente: FuenteDeSolicitudes) -> Reporte:
    """Solo necesita listar: depende de la interfaz de lectura, no del repositorio completo (ISP)."""
    solicitudes = fuente.listar()
    estados = Counter(s.estado for s in solicitudes)
    tipos = Counter(s.tipo for s in solicitudes)
    pendientes_alta = PendientesDePrioridadAlta()
    return Reporte(
        total=len(solicitudes),
        por_estado={estado: estados[estado] for estado in Estado},
        por_tipo={tipo: tipos[tipo] for tipo in TipoSolicitud},
        pendientes_alta=[s for s in solicitudes if pendientes_alta.cumple(s)],
    )

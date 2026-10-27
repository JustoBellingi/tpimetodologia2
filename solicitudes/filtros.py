"""Criterios de búsqueda.

Cada criterio es una clase con el método `cumple` (Replace Conditional with Polymorphism).
Para agregar un criterio nuevo se crea una clase nueva; el servicio no se modifica (OCP).
"""
from dataclasses import dataclass
from typing import Protocol

from solicitudes.dominio import Estado, Prioridad, Solicitud, TipoSolicitud


class Filtro(Protocol):
    def cumple(self, solicitud: Solicitud) -> bool: ...


@dataclass(frozen=True)
class PorEstado:
    estado: Estado

    def cumple(self, solicitud: Solicitud) -> bool:
        return solicitud.estado is self.estado


@dataclass(frozen=True)
class PorTipo:
    tipo: TipoSolicitud

    def cumple(self, solicitud: Solicitud) -> bool:
        return solicitud.tipo is self.tipo


@dataclass(frozen=True)
class PorLegajo:
    legajo: str

    def cumple(self, solicitud: Solicitud) -> bool:
        return solicitud.estudiante.legajo == self.legajo


@dataclass(frozen=True)
class PendientesDePrioridadAlta:
    def cumple(self, solicitud: Solicitud) -> bool:
        return solicitud.estado is Estado.PENDIENTE and solicitud.prioridad is Prioridad.ALTA

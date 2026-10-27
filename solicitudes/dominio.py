"""Modelo de dominio: entidades, valores permitidos y reglas de negocio.

No conoce la consola ni el archivo JSON: solo las reglas del negocio.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from enum import Enum
from typing import Optional


# ---------------------------------------------------------------- errores
class ErrorDeNegocio(Exception):
    """Base de todos los errores que el usuario puede provocar con datos o acciones inválidas."""


class DatosInvalidos(ErrorDeNegocio):
    pass


class SolicitudInexistente(ErrorDeNegocio):
    def __init__(self, id_solicitud: int):
        super().__init__(f"no existe la solicitud {id_solicitud}")


class ResponsableInexistente(ErrorDeNegocio):
    def __init__(self, codigo: str):
        super().__init__(f"no existe el responsable {codigo}")


class TransicionInvalida(ErrorDeNegocio):
    pass


# ---------------------------------------------------------------- valores
class Estado(Enum):
    """Cada estado conoce su código de persistencia y su texto para mostrar."""

    PENDIENTE = ("P", "PENDIENTE")
    EN_PROCESO = ("E", "EN PROCESO")
    RESUELTA = ("R", "RESUELTA")
    RECHAZADA = ("X", "RECHAZADA")

    def __init__(self, codigo: str, etiqueta: str):
        self.codigo = codigo
        self.etiqueta = etiqueta

    @property
    def es_final(self) -> bool:
        return self in (Estado.RESUELTA, Estado.RECHAZADA)

    @classmethod
    def desde_codigo(cls, codigo: str) -> "Estado":
        for estado in cls:
            if estado.codigo == codigo:
                return estado
        raise ValueError(f"codigo de estado desconocido: {codigo!r}")


TRANSICIONES_PERMITIDAS = {
    Estado.PENDIENTE: {Estado.EN_PROCESO, Estado.RECHAZADA},
    Estado.EN_PROCESO: {Estado.RESUELTA, Estado.RECHAZADA},
    Estado.RESUELTA: set(),
    Estado.RECHAZADA: set(),
}


class TipoSolicitud(Enum):
    """El valor es la opción que elige el usuario en el menú."""

    CERTIFICADO = "1"
    EQUIVALENCIA = "2"
    CAMBIO_COMISION = "3"
    RECLAMO_NOTA = "4"


class Prioridad(Enum):
    ALTA = "alta"
    MEDIA = "media"
    BAJA = "baja"


# ---------------------------------------------------------------- entidades
@dataclass(frozen=True)
class Estudiante:
    nombre: str
    legajo: str
    email: str


@dataclass(frozen=True)
class Responsable:
    codigo: str
    nombre: str
    area: str


@dataclass(frozen=True)
class DatosSolicitud:
    """Parameter Object: todo lo necesario para dar de alta una solicitud, ya validado."""

    estudiante: Estudiante
    tipo: TipoSolicitud
    descripcion: str
    prioridad: Prioridad


@dataclass
class Solicitud:
    id: int
    estudiante: Estudiante
    tipo: TipoSolicitud
    descripcion: str
    prioridad: Prioridad
    fecha_alta: date
    estado: Estado = Estado.PENDIENTE
    responsable: Optional[Responsable] = None

    @classmethod
    def nueva(cls, id_solicitud: int, datos: DatosSolicitud, fecha_alta: date) -> "Solicitud":
        return cls(
            id=id_solicitud,
            estudiante=datos.estudiante,
            tipo=datos.tipo,
            descripcion=datos.descripcion,
            prioridad=datos.prioridad,
            fecha_alta=fecha_alta,
        )

    def verificar_que_esta_abierta(self) -> None:
        if self.estado.es_final:
            raise TransicionInvalida("la solicitud esta cerrada y no puede modificarse")

    def asignar_responsable(self, responsable: Responsable) -> None:
        self.verificar_que_esta_abierta()
        self.responsable = responsable

    def cambiar_estado(self, nuevo_estado: Estado) -> None:
        self.verificar_que_esta_abierta()
        if nuevo_estado is self.estado:
            raise TransicionInvalida(f"la solicitud ya esta {nuevo_estado.etiqueta}")
        if nuevo_estado not in TRANSICIONES_PERMITIDAS[self.estado]:
            raise TransicionInvalida(
                f"no se puede pasar de {self.estado.etiqueta} a {nuevo_estado.etiqueta}"
            )
        if nuevo_estado is Estado.EN_PROCESO and self.responsable is None:
            raise TransicionInvalida(
                "la solicitud debe tener responsable para pasar a EN PROCESO"
            )
        self.estado = nuevo_estado

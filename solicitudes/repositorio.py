"""Persistencia de solicitudes.

El servicio depende de la abstracción `RepositorioSolicitudes` (DIP), no de un archivo.
Hay dos implementaciones intercambiables (LSP): JSON para producción y memoria para tests.
El reporte solo necesita leer, así que depende de la interfaz más chica `FuenteDeSolicitudes` (ISP).
"""
from __future__ import annotations

import json
import os
from datetime import date
from pathlib import Path
from typing import Optional, Protocol

from solicitudes.dominio import (
    Estado,
    Estudiante,
    Prioridad,
    Responsable,
    Solicitud,
    TipoSolicitud,
)


# ---------------------------------------------------------------- abstracciones
class FuenteDeSolicitudes(Protocol):
    def listar(self) -> list[Solicitud]: ...


class RepositorioSolicitudes(FuenteDeSolicitudes, Protocol):
    def obtener(self, id_solicitud: int) -> Optional[Solicitud]: ...

    def proximo_id(self) -> int: ...

    def guardar(self, solicitud: Solicitud) -> None: ...


# ---------------------------------------------------------------- catálogo
class CatalogoResponsables:
    def __init__(self, responsables: list[Responsable]):
        self._responsables = list(responsables)

    def todos(self) -> list[Responsable]:
        return list(self._responsables)

    def buscar(self, codigo: str) -> Optional[Responsable]:
        for responsable in self._responsables:
            if responsable.codigo == codigo.upper():
                return responsable
        return None


RESPONSABLES_POR_DEFECTO = [
    Responsable("R1", "Ana Gomez", "Alumnos"),
    Responsable("R2", "Luis Perez", "Academica"),
    Responsable("R3", "Marta Diaz", "Tesoreria"),
]


# ---------------------------------------------------------------- implementaciones
class RepositorioEnMemoria:
    def __init__(self, ultimo_id: int = 0):
        self._solicitudes: dict[int, Solicitud] = {}
        self._ultimo_id = ultimo_id

    @property
    def ultimo_id(self) -> int:
        return self._ultimo_id

    def listar(self) -> list[Solicitud]:
        return sorted(self._solicitudes.values(), key=lambda s: s.id)

    def obtener(self, id_solicitud: int) -> Optional[Solicitud]:
        return self._solicitudes.get(id_solicitud)

    def proximo_id(self) -> int:
        return self._ultimo_id + 1

    def guardar(self, solicitud: Solicitud) -> None:
        self._solicitudes[solicitud.id] = solicitud
        self._ultimo_id = max(self._ultimo_id, solicitud.id)


class RepositorioJSON:
    """Mantiene el mismo formato de archivo que la versión inicial (compatibilidad de datos)."""

    def __init__(self, ruta: Path, catalogo: CatalogoResponsables):
        self._ruta = Path(ruta)
        self._catalogo = catalogo
        self._memoria = RepositorioEnMemoria()
        self.respaldo_de_archivo_danado: Optional[Path] = None
        self._cargar()

    def listar(self) -> list[Solicitud]:
        return self._memoria.listar()

    def obtener(self, id_solicitud: int) -> Optional[Solicitud]:
        return self._memoria.obtener(id_solicitud)

    def proximo_id(self) -> int:
        return self._memoria.proximo_id()

    def guardar(self, solicitud: Solicitud) -> None:
        self._memoria.guardar(solicitud)
        self._escribir_archivo()

    # -- lectura / escritura del archivo
    def _cargar(self) -> None:
        if not self._ruta.exists():
            return
        try:
            contenido = json.loads(self._ruta.read_text(encoding="utf-8"))
            self._memoria = RepositorioEnMemoria(ultimo_id=contenido["contador"])
            for registro in contenido["solicitudes"]:
                self._memoria.guardar(self._desde_registro(registro))
        except (json.JSONDecodeError, KeyError, TypeError, ValueError):
            # El archivo no se puede leer: se aparta para no sobrescribirlo y se arranca vacío.
            self._memoria = RepositorioEnMemoria()
            self.respaldo_de_archivo_danado = self._apartar_archivo_danado()

    def _apartar_archivo_danado(self) -> Path:
        respaldo = self._ruta.with_name(self._ruta.name + ".danado")
        numero = 1
        while respaldo.exists():
            numero += 1
            respaldo = self._ruta.with_name(f"{self._ruta.name}.danado{numero}")
        self._ruta.rename(respaldo)
        return respaldo

    def _escribir_archivo(self) -> None:
        """Escribe primero en un archivo temporal y después lo reemplaza: si el programa
        se corta a mitad de la escritura, el datos.json anterior queda intacto."""
        contenido = {
            "contador": self._memoria.ultimo_id,
            "solicitudes": [self._a_registro(s) for s in self._memoria.listar()],
        }
        temporal = self._ruta.with_name(self._ruta.name + ".tmp")
        temporal.write_text(json.dumps(contenido, indent=2, ensure_ascii=False), encoding="utf-8")
        os.replace(temporal, self._ruta)

    # -- traducción entre objetos de dominio y el formato histórico del archivo
    @staticmethod
    def _a_registro(solicitud: Solicitud) -> dict:
        return {
            "id": solicitud.id,
            "nom": solicitud.estudiante.nombre,
            "leg": solicitud.estudiante.legajo,
            "mail": solicitud.estudiante.email,
            "tipo": solicitud.tipo.name,
            "desc": solicitud.descripcion,
            "prio": solicitud.prioridad.value,
            "est": solicitud.estado.codigo,
            "resp": solicitud.responsable.codigo if solicitud.responsable else None,
            "fecha": solicitud.fecha_alta.isoformat(),
        }

    def _desde_registro(self, registro: dict) -> Solicitud:
        codigo_responsable = registro["resp"]
        return Solicitud(
            id=registro["id"],
            estudiante=Estudiante(registro["nom"], registro["leg"], registro["mail"]),
            tipo=TipoSolicitud[registro["tipo"]],
            descripcion=registro["desc"],
            prioridad=Prioridad(registro["prio"]),
            fecha_alta=date.fromisoformat(registro["fecha"]),
            estado=Estado.desde_codigo(registro["est"]),
            responsable=self._catalogo.buscar(codigo_responsable) if codigo_responsable else None,
        )

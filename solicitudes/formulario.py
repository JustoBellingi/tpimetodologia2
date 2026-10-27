"""Formulario de alta: agrupa los textos que escribe el usuario y los valida.

Reemplaza los 6 parámetros sueltos de `registrar(nom, leg, mail, tipo, desc, prio)`
(Introduce Parameter Object) y divide la validación en métodos chicos (Extract Method).
"""
from dataclasses import dataclass

from solicitudes.dominio import (
    DatosInvalidos,
    DatosSolicitud,
    Estudiante,
    Prioridad,
    TipoSolicitud,
)


@dataclass(frozen=True)
class FormularioSolicitud:
    nombre: str
    legajo: str
    email: str
    opcion_tipo: str
    descripcion: str
    prioridad: str

    def validar(self) -> DatosSolicitud:
        """Devuelve los datos tipados o lanza DatosInvalidos con el primer error encontrado."""
        estudiante = Estudiante(
            nombre=self._nombre_valido(),
            legajo=self._legajo_valido(),
            email=self._email_valido(),
        )
        tipo = self._tipo_valido()
        descripcion = self._descripcion_valida()
        prioridad = self._prioridad_valida()
        return DatosSolicitud(estudiante, tipo, descripcion, prioridad)

    def _nombre_valido(self) -> str:
        nombre = self.nombre.strip()
        if not nombre:
            raise DatosInvalidos("el nombre es obligatorio")
        return nombre

    def _legajo_valido(self) -> str:
        if not self.legajo.isdigit():
            raise DatosInvalidos("el legajo debe ser numerico")
        return self.legajo

    def _email_valido(self) -> str:
        if "@" not in self.email or "." not in self.email:
            raise DatosInvalidos("el email no es valido")
        return self.email

    def _tipo_valido(self) -> TipoSolicitud:
        try:
            return TipoSolicitud(self.opcion_tipo)
        except ValueError:
            raise DatosInvalidos("tipo de solicitud invalido") from None

    def _descripcion_valida(self) -> str:
        descripcion = self.descripcion.strip()
        if not descripcion:
            raise DatosInvalidos("la descripcion es obligatoria")
        return descripcion

    def _prioridad_valida(self) -> Prioridad:
        try:
            return Prioridad(self.prioridad)
        except ValueError:
            raise DatosInvalidos("la prioridad debe ser alta, media o baja") from None

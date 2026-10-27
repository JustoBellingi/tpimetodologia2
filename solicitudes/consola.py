"""Interfaz de consola: lee lo que escribe el usuario, llama al servicio y muestra resultados.

Es la única parte del sistema que usa input() y print().
"""
from __future__ import annotations

from typing import Callable

from solicitudes.dominio import DatosInvalidos, ErrorDeNegocio, Estado, Solicitud, TipoSolicitud
from solicitudes.filtros import Filtro, PorEstado, PorLegajo, PorTipo
from solicitudes.formulario import FormularioSolicitud
from solicitudes.servicio import Reporte, ServicioSolicitudes, generar_reporte

ESTADOS_PARA_CAMBIAR = {"1": Estado.EN_PROCESO, "2": Estado.RESUELTA, "3": Estado.RECHAZADA}
ESTADOS_PARA_BUSCAR = {"1": Estado.PENDIENTE, "2": Estado.EN_PROCESO, "3": Estado.RESUELTA, "4": Estado.RECHAZADA}

MENU = [
    "",
    "=== GESTION DE SOLICITUDES ACADEMICAS ===",
    "1. Registrar solicitud",
    "2. Cambiar estado",
    "3. Asignar responsable",
    "4. Buscar solicitudes",
    "5. Reporte",
    "0. Salir",
]


def formatear_solicitud(solicitud: Solicitud) -> str:
    """Formato único de una línea de listado (antes estaba copiado en buscar y reporte)."""
    responsable = solicitud.responsable.nombre if solicitud.responsable else "sin asignar"
    return (
        f"#{solicitud.id} [{solicitud.tipo.name}] {solicitud.estudiante.nombre} "
        f"(legajo {solicitud.estudiante.legajo}) - prioridad {solicitud.prioridad.value} "
        f"- {solicitud.estado.etiqueta} - responsable: {responsable}"
    )


class Consola:
    def __init__(
        self,
        servicio: ServicioSolicitudes,
        reporte: Callable[[], Reporte],
        leer: Callable[[str], str] = input,
        mostrar: Callable[[str], None] = print,
    ):
        self._servicio = servicio
        self._reporte = reporte
        self._leer = leer
        self._mostrar = mostrar
        self._acciones = {
            "1": self._registrar,
            "2": self._cambiar_estado,
            "3": self._asignar_responsable,
            "4": self._buscar,
            "5": self._mostrar_reporte,
        }

    def ejecutar(self) -> None:
        while True:
            for linea in MENU:
                self._mostrar(linea)
            try:
                opcion = self._leer("Opcion: ")
            except EOFError:
                self._mostrar("Hasta luego")
                return
            if opcion == "0":
                self._mostrar("Hasta luego")
                return
            accion = self._acciones.get(opcion)
            if accion is None:
                self._mostrar("Opcion invalida")
                continue
            self._ejecutar_accion(accion)

    def _ejecutar_accion(self, accion: Callable[[], None]) -> None:
        """Único lugar donde se traducen errores de negocio a mensajes para el usuario."""
        try:
            accion()
        except ErrorDeNegocio as error:
            self._mostrar(f"Error: {error}")
        except EOFError:
            self._mostrar("Error: la entrada termino antes de completar la operacion")

    # ------------------------------------------------------------ acciones del menú
    def _registrar(self) -> None:
        formulario = FormularioSolicitud(
            nombre=self._leer("Nombre del estudiante: "),
            legajo=self._leer("Legajo: "),
            email=self._leer("Email: "),
            opcion_tipo=self._leer_tipo(),
            descripcion=self._leer("Descripcion: "),
            prioridad=self._leer("Prioridad (alta/media/baja): "),
        )
        solicitud = self._servicio.registrar(formulario.validar())
        self._mostrar(f"Solicitud registrada con ID {solicitud.id}")

    def _cambiar_estado(self) -> None:
        id_solicitud = self._leer_id()
        self._mostrar("Estados: 1-En proceso 2-Resuelta 3-Rechazada")
        opcion = self._leer("Nuevo estado: ")
        self._servicio.obtener(id_solicitud)  # primero se informa si la solicitud no existe
        nuevo_estado = self._elegir(ESTADOS_PARA_CAMBIAR, opcion, "opcion de estado invalida")
        solicitud = self._servicio.cambiar_estado(id_solicitud, nuevo_estado)
        self._mostrar(f"Solicitud {solicitud.id} actualizada a {solicitud.estado.etiqueta}")

    def _asignar_responsable(self) -> None:
        id_solicitud = self._leer_id()
        for responsable in self._servicio.responsables():
            self._mostrar(f"  {responsable.codigo} - {responsable.nombre} ({responsable.area})")
        codigo = self._leer("Codigo de responsable: ")
        responsable = self._servicio.asignar_responsable(id_solicitud, codigo)
        self._mostrar(
            f"Responsable {responsable.nombre} ({responsable.area}) "
            f"asignado a la solicitud {id_solicitud}"
        )

    def _buscar(self) -> None:
        self._mostrar("Criterios: 1-Estado 2-Tipo 3-Legajo")
        criterio = self._leer("Criterio: ")
        valor = self._leer("Valor: ")
        encontradas = self._servicio.buscar(self._crear_filtro(criterio, valor))
        if not encontradas:
            self._mostrar("No se encontraron solicitudes")
        for solicitud in encontradas:
            self._mostrar(formatear_solicitud(solicitud))

    def _mostrar_reporte(self) -> None:
        reporte = self._reporte()
        self._mostrar("==== REPORTE DE SOLICITUDES ====")
        self._mostrar(f"Total: {reporte.total}")
        self._mostrar("Por estado:")
        for estado, cantidad in reporte.por_estado.items():
            self._mostrar(f"  {estado.etiqueta}: {cantidad}")
        self._mostrar("Por tipo:")
        for tipo, cantidad in reporte.por_tipo.items():
            self._mostrar(f"  {tipo.name}: {cantidad}")
        self._mostrar("Pendientes de prioridad alta:")
        for solicitud in reporte.pendientes_alta:
            self._mostrar(f"  {formatear_solicitud(solicitud)}")
        if not reporte.pendientes_alta:
            self._mostrar("  (ninguna)")
        self._mostrar("================================")

    # ------------------------------------------------------------ auxiliares
    def _leer_tipo(self) -> str:
        self._mostrar("Tipos: 1-Certificado 2-Equivalencia 3-Cambio de comision 4-Reclamo de nota")
        return self._leer("Tipo: ")

    def _leer_id(self) -> int:
        texto = self._leer("ID de la solicitud: ")
        try:
            return int(texto)
        except ValueError:
            raise DatosInvalidos("el ID debe ser numerico") from None

    def _crear_filtro(self, criterio: str, valor: str) -> Filtro:
        if criterio == "1":
            return PorEstado(self._elegir(ESTADOS_PARA_BUSCAR, valor, "estado invalido"))
        if criterio == "2":
            return PorTipo(self._elegir_tipo(valor))
        if criterio == "3":
            return PorLegajo(valor)
        raise DatosInvalidos("criterio invalido")

    @staticmethod
    def _elegir(opciones: dict[str, Estado], clave: str, mensaje_error: str) -> Estado:
        elegido = opciones.get(clave)
        if elegido is None:
            raise DatosInvalidos(mensaje_error)
        return elegido

    @staticmethod
    def _elegir_tipo(opcion: str) -> TipoSolicitud:
        try:
            return TipoSolicitud(opcion)
        except ValueError:
            raise DatosInvalidos("tipo de solicitud invalido") from None

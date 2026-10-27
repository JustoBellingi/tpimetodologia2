import pytest

from solicitudes.dominio import DatosInvalidos, Prioridad, TipoSolicitud
from solicitudes.formulario import FormularioSolicitud

VALIDO = dict(nombre="  Ana  ", legajo="1001", email="ana@mail.com", opcion_tipo="2", descripcion=" Equivalencia ", prioridad="media")


def test_un_formulario_valido_devuelve_datos_tipados_y_limpios():
    datos = FormularioSolicitud(**VALIDO).validar()
    assert datos.estudiante.nombre == "Ana"
    assert datos.descripcion == "Equivalencia"
    assert datos.tipo is TipoSolicitud.EQUIVALENCIA
    assert datos.prioridad is Prioridad.MEDIA


@pytest.mark.parametrize("campo, valor, mensaje", [
    ("nombre", "   ", "el nombre es obligatorio"),
    ("legajo", "12a", "el legajo debe ser numerico"),
    ("email", "anamail", "el email no es valido"),
    ("opcion_tipo", "9", "tipo de solicitud invalido"),
    ("descripcion", "", "la descripcion es obligatoria"),
    ("prioridad", "urgente", "la prioridad debe ser alta, media o baja"),
])
def test_cada_campo_invalido_informa_su_error(campo, valor, mensaje):
    with pytest.raises(DatosInvalidos, match=mensaje):
        FormularioSolicitud(**{**VALIDO, campo: valor}).validar()

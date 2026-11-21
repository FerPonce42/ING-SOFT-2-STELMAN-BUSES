from unittest.mock import MagicMock

import pytest

from app.errors import ReglaNegocioError
from app.services.incidencia_service import IncidenciaService

MENSAJE_NO_ENCONTRADA = "La incidencia no existe o no pertenece a tu ruta."
ID_SUPERVISOR = 1
ID_RUTA = 7
ID_INCIDENCIA = 55


@pytest.fixture
def incidencias():
    return MagicMock(name="incidencias_repo")


@pytest.fixture
def service(incidencias):
    rutas = MagicMock(name="ruta_service")
    rutas.exigir_ruta_activa.return_value = ID_RUTA
    return IncidenciaService(incidencias, MagicMock(name="buses_repo"), rutas)


# ---------- incidencia inexistente o de otra ruta ----------
def test_actualizar_disciplinaria_inexistente_lanza_error(service, incidencias):
    # Arrange
    incidencias.obtener_disciplinaria.return_value = None
    form = {"id_incidencia": str(ID_INCIDENCIA)}
    # Act
    with pytest.raises(ReglaNegocioError) as error:
        service.actualizar_disciplinaria(ID_SUPERVISOR, form)
    # Assert
    assert str(error.value) == MENSAJE_NO_ENCONTRADA
    incidencias.obtener_disciplinaria.assert_called_once_with(ID_INCIDENCIA, ID_RUTA)
    incidencias.actualizar_disciplinaria.assert_not_called()


def test_actualizar_operativa_inexistente_lanza_error(service, incidencias):
    incidencias.obtener_operativa.return_value = None
    form = {"id_incidencia": str(ID_INCIDENCIA)}

    with pytest.raises(ReglaNegocioError) as error:
        service.actualizar_operativa(ID_SUPERVISOR, form)

    assert str(error.value) == MENSAJE_NO_ENCONTRADA
    incidencias.obtener_operativa.assert_called_once_with(ID_INCIDENCIA, ID_RUTA)
    incidencias.actualizar_operativa.assert_not_called()


def test_eliminar_disciplinaria_inexistente_lanza_error(service, incidencias):
    incidencias.obtener_disciplinaria.return_value = None

    with pytest.raises(ReglaNegocioError) as error:
        service.eliminar_disciplinaria(ID_SUPERVISOR, ID_INCIDENCIA)

    assert str(error.value) == MENSAJE_NO_ENCONTRADA
    incidencias.eliminar_disciplinaria.assert_not_called()
    incidencias.commit.assert_not_called()


def test_eliminar_operativa_inexistente_lanza_error(service, incidencias):
    incidencias.obtener_operativa.return_value = None

    with pytest.raises(ReglaNegocioError) as error:
        service.eliminar_operativa(ID_SUPERVISOR, ID_INCIDENCIA)

    assert str(error.value) == MENSAJE_NO_ENCONTRADA
    incidencias.eliminar_operativa.assert_not_called()
    incidencias.commit.assert_not_called()


# ---------- eliminación correcta y transacción ----------
def test_eliminar_disciplinaria_existente_elimina_y_confirma(service, incidencias):
    incidencias.obtener_disciplinaria.return_value = {"id_incidencia": ID_INCIDENCIA}

    service.eliminar_disciplinaria(ID_SUPERVISOR, ID_INCIDENCIA)

    incidencias.eliminar_disciplinaria.assert_called_once_with(ID_INCIDENCIA)
    incidencias.commit.assert_called_once()
    incidencias.rollback.assert_not_called()


def test_eliminar_operativa_existente_elimina_y_confirma(service, incidencias):
    incidencias.obtener_operativa.return_value = {"id_incidencia": ID_INCIDENCIA}

    service.eliminar_operativa(ID_SUPERVISOR, ID_INCIDENCIA)

    incidencias.eliminar_operativa.assert_called_once_with(ID_INCIDENCIA)
    incidencias.commit.assert_called_once()
    incidencias.rollback.assert_not_called()


def test_eliminar_con_fallo_hace_rollback_y_propaga_error(service, incidencias):
    incidencias.obtener_operativa.return_value = {"id_incidencia": ID_INCIDENCIA}
    incidencias.eliminar_operativa.side_effect = RuntimeError("fallo de BD")

    with pytest.raises(RuntimeError):
        service.eliminar_operativa(ID_SUPERVISOR, ID_INCIDENCIA)

    incidencias.rollback.assert_called_once()
    incidencias.commit.assert_not_called()


# ---------- validaciones de entrada ----------
def test_registrar_operativa_con_gravedad_invalida_lanza_error(service, incidencias):
    form = {"fecha": "2025-11-20", "descripcion": "Llanta baja", "estado": "Pendiente",
            "id_bus": "3", "gravedad": "Critica"}

    with pytest.raises(ReglaNegocioError) as error:
        service.registrar_operativa(ID_SUPERVISOR, form)

    assert str(error.value) == "La gravedad seleccionada no es válida."
    incidencias.crear_operativa.assert_not_called()


def test_registrar_disciplinaria_con_estado_invalido_lanza_error(service, incidencias):
    form = {"fecha": "2025-11-20", "descripcion": "Falta", "estado": "Archivada", "id_bus": "3"}

    with pytest.raises(ReglaNegocioError) as error:
        service.registrar_disciplinaria(ID_SUPERVISOR, form)

    assert str(error.value) == "El estado seleccionado no es válido."
    incidencias.crear_disciplinaria.assert_not_called()


# ---------- refactor: constante del mensaje ----------
def test_mensaje_no_encontrada_esta_definido_como_constante():
    from app.services import incidencia_service as modulo

    assert modulo.MSG_INCIDENCIA_NO_ENCONTRADA == MENSAJE_NO_ENCONTRADA

"""Composition root: arma servicios con la conexión del request actual."""
from flask import current_app

from app.db import get_db
from app.repositories.bus_repository import BusRepository
from app.repositories.caja_repository import CajaRepository
from app.repositories.chofer_repository import ChoferRepository
from app.repositories.cuenta_repository import CuentaRepository
from app.repositories.esquema_repository import EsquemaRepository
from app.repositories.incidencia_repository import IncidenciaRepository
from app.repositories.ruta_repository import RutaRepository
from app.services.auth_service import AuthService
from app.services.bus_service import BusService
from app.services.caja_service import CajaService
from app.services.chofer_service import ChoferService
from app.services.incidencia_service import IncidenciaService
from app.services.reporte_service import ReporteService
from app.services.ruta_service import RutaService


def auth_service():
    return AuthService(CuentaRepository(get_db()))


def ruta_service():
    return RutaService(RutaRepository(get_db()))


def bus_service():
    return BusService(BusRepository(get_db()), ruta_service(),
                      current_app.config["ALMACEN_POR_DEFECTO"])


def chofer_service():
    return ChoferService(ChoferRepository(get_db()), ruta_service())


def incidencia_service():
    return IncidenciaService(IncidenciaRepository(get_db()), BusRepository(get_db()), ruta_service())


def caja_service():
    return CajaService(CajaRepository(get_db()), ChoferRepository(get_db()),
                       BusRepository(get_db()), ruta_service())


def reporte_service():
    return ReporteService(EsquemaRepository(get_db()))

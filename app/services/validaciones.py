"""Validaciones compartidas entre servicios (sin acceso a BD)."""
from datetime import date, datetime
from decimal import Decimal, InvalidOperation

from app.errors import ReglaNegocioError

FECHA_MINIMA = date(2000, 1, 1)


def texto_requerido(valor, etiqueta, maximo=None):
    texto = (valor or "").strip()
    if not texto:
        raise ReglaNegocioError(f"{etiqueta} es obligatorio.")
    if maximo and len(texto) > maximo:
        raise ReglaNegocioError(f"{etiqueta} no puede superar {maximo} caracteres.")
    return texto


def texto_opcional(valor):
    texto = (valor or "").strip()
    return texto or None


def entero(valor, etiqueta):
    try:
        return int(valor)
    except (TypeError, ValueError):
        raise ReglaNegocioError(f"{etiqueta} no es válido.")


def decimal(valor, etiqueta, minimo=Decimal("0"), permitir_igual=True):
    try:
        numero = Decimal(str(valor).strip())
    except (InvalidOperation, AttributeError):
        raise ReglaNegocioError(f"{etiqueta} no es un número válido.")
    if numero < minimo or (not permitir_igual and numero == minimo):
        raise ReglaNegocioError(f"{etiqueta} debe ser {'mayor o igual' if permitir_igual else 'mayor'} que {minimo}.")
    return numero


def fecha(valor, etiqueta="La fecha", minimo=FECHA_MINIMA, permitir_futuro=False):
    try:
        resultado = datetime.strptime((valor or "").strip(), "%Y-%m-%d").date()
    except ValueError:
        raise ReglaNegocioError(f"{etiqueta} es inválida. Usa el formato AAAA-MM-DD.")
    if resultado < minimo or (not permitir_futuro and resultado > date.today()):
        limite = "hoy" if not permitir_futuro else "el futuro"
        raise ReglaNegocioError(f"{etiqueta} está fuera del rango permitido ({minimo.isoformat()} hasta {limite}).")
    return resultado


def a_fecha_iso(valor):
    """Los <input type=date> solo aceptan AAAA-MM-DD, no un datetime completo."""
    if isinstance(valor, datetime):
        return valor.date().isoformat()
    if isinstance(valor, date):
        return valor.isoformat()
    return valor

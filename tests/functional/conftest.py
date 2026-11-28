"""Configuración compartida de las pruebas funcionales (Selenium).

- Con STELMAN_HEADLESS=1 (Jenkins) todos los Chrome se abren sin ventana.
- Fixture `driver` para test_caja.py: sesión iniciada y formulario de caja listo.
"""
import os

import pytest
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

BASE_URL = os.environ.get("STELMAN_URL", "http://localhost:5000")
USUARIO = "aperez_sup"
CLAVE = "stelman123"
FORMULARIO_CAJA = "form[action$='registrar_caja']"

_CHROME_ORIGINAL = webdriver.Chrome
_ARGUMENTOS_CI = (
    "--headless=new",
    "--no-sandbox",
    "--disable-dev-shm-usage",
    "--window-size=1440,1000",
)


def _chrome_headless(*args, options=None, **kwargs):
    options = options or webdriver.ChromeOptions()
    if os.environ.get("CHROME_BIN"):
        options.binary_location = os.environ["CHROME_BIN"]
    for argumento in _ARGUMENTOS_CI:
        options.add_argument(argumento)
    return _CHROME_ORIGINAL(*args, options=options, **kwargs)


@pytest.fixture(scope="session", autouse=True)
def _navegador_sin_ventana_en_ci():
    """Activa el modo headless solo cuando STELMAN_HEADLESS=1."""
    if os.environ.get("STELMAN_HEADLESS") != "1":
        yield
        return
    with pytest.MonkeyPatch.context() as parche:
        parche.setattr(webdriver, "Chrome", _chrome_headless)
        yield


@pytest.fixture
def driver():
    """Navegador con sesión iniciada y el formulario 'Registrar Recaudación' visible."""
    navegador = webdriver.Chrome()
    espera = WebDriverWait(navegador, 10)
    try:
        navegador.get(f"{BASE_URL}/login")
        navegador.find_element(By.ID, "usuario").send_keys(USUARIO)
        navegador.find_element(By.ID, "password").send_keys(CLAVE)
        navegador.find_element(By.CSS_SELECTOR, "button.btn-submit").click()
        espera.until(EC.url_contains("/panel"))

        navegador.get(f"{BASE_URL}/panel/caja")
        try:
            WebDriverWait(navegador, 3).until(
                EC.visibility_of_element_located((By.CSS_SELECTOR, FORMULARIO_CAJA)))
        except TimeoutException:
            navegador.find_element(By.PARTIAL_LINK_TEXT, "Registrar Recaudación").click()
            espera.until(EC.visibility_of_element_located((By.CSS_SELECTOR, FORMULARIO_CAJA)))
        yield navegador
    finally:
        navegador.quit()


import pytest
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


FORMULARIO = "form[action$='registrar_caja']"


def _verificar_bloqueo_del_formulario(driver, campo, valor):
    elemento = driver.find_element(By.NAME, campo)
    elemento.clear()
    elemento.send_keys(valor)

    # Comprobar que el navegador detecta el valor inválido
    resultado = driver.execute_script(
        "return arguments[0].validity.rangeUnderflow;",
        elemento
    )
    assert resultado is True


class TestRegistrarRecaudacion:

    def _mensaje(self, driver):
        return WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.CLASS_NAME, "alert"))
        ).text

    def test_cp03_monto_cero(self, driver):
        driver.find_element(By.NAME, "monto").clear()
        _verificar_bloqueo_del_formulario(driver, "monto", "0")

    def test_cp04_monto_negativo(self, driver):
        driver.find_element(By.NAME, "monto").clear()
        _verificar_bloqueo_del_formulario(driver, "monto", "-10")

    def test_cp05_campos_obligatorios(self, driver):
        campo = driver.find_element(By.NAME, "monto")
        campo.clear()

        resultado = driver.execute_script(
            "return arguments[0].validity.valueMissing;",
            campo
        )
        assert resultado is True

    def test_cp09_fecha_anterior_al_minimo(self, driver):
        """La fecha 1999-12-31 (debajo del mínimo 2000-01-01) la rechaza el servidor."""
        campo_fecha = driver.find_element(By.NAME, "fecha")
        # send_keys en <input type="date"> depende del idioma del navegador
        driver.execute_script("arguments[0].value = arguments[1];", campo_fecha, "1999-12-31")
        campo_monto = driver.find_element(By.NAME, "monto")
        campo_monto.clear()
        campo_monto.send_keys("100.00")

        boton = driver.find_element(By.CSS_SELECTOR, f"{FORMULARIO} button[type='submit']")
        driver.execute_script(
            "arguments[0].scrollIntoView({block: 'center'}); arguments[0].click();", boton)

        assert "fuera del rango permitido" in self._mensaje(driver)

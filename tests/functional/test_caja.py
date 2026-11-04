"""Issue #25 - Pruebas funcionales (Selenium + unittest/xUnit): Registrar recaudación (módulo Caja).

Requisitos: la app corriendo en http://localhost:5000 (docker compose up --build)
y las librerías instaladas:  py -m pip install selenium pytest

Ejecutar:  py -m pytest tests/functional/test_caja.py -v
"""
import unittest
from datetime import date, timedelta

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select, WebDriverWait

BASE_URL = "http://localhost:5000"
USUARIO = "aperez_sup"
CLAVE = "stelman123"

FORMULARIO = "form[action$='registrar_caja']"


class RegistrarRecaudacionTest(unittest.TestCase):
    """Funcionalidad: Caja > Registrar Recaudación (1 método por caso de prueba)."""

    def setUp(self):
        self.driver = webdriver.Chrome()
        self.driver.maximize_window()
        self.wait = WebDriverWait(self.driver, 10)
        self._iniciar_sesion()
        self.driver.get(f"{BASE_URL}/panel/caja")
        self.filas_antes = self._contar_filas()
        self.driver.find_element(By.LINK_TEXT, "Registrar Recaudación").click()
        self.wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, FORMULARIO)))
        self.hoy = self._fecha_de_hoy_segun_la_app()

    def tearDown(self):
        self.driver.quit()

    # ---------- utilidades ----------
    def _iniciar_sesion(self):
        self.driver.get(f"{BASE_URL}/login")
        self.driver.find_element(By.ID, "usuario").send_keys(USUARIO)
        self.driver.find_element(By.ID, "password").send_keys(CLAVE)
        self.driver.find_element(By.CSS_SELECTOR, "button.btn-submit").click()
        self.wait.until(EC.url_contains("/panel"))

    def _contar_filas(self):
        """Filas de datos del historial (la fila 'No hay recaudaciones' no cuenta)."""
        return len(self.driver.find_elements(By.XPATH, "//table//tr[count(td)=5]"))

    def _fecha_de_hoy_segun_la_app(self):
        """El campo Fecha trae max=hoy (calculado por el servidor)."""
        campo = self.driver.find_element(By.NAME, "fecha")
        return date.fromisoformat(campo.get_attribute("max"))

    def _llenar(self, fecha, monto, observacion=""):
        campo_fecha = self.driver.find_element(By.NAME, "fecha")
        self.driver.execute_script("arguments[0].value = arguments[1];", campo_fecha, fecha.isoformat())
        campo_monto = self.driver.find_element(By.NAME, "monto")
        campo_monto.clear()
        campo_monto.send_keys(monto)
        campo_obs = self.driver.find_element(By.NAME, "observacion")
        campo_obs.clear()
        campo_obs.send_keys(observacion)
        # Chofer y Bus: se deja seleccionada la primera opción de cada lista
        self.assertGreater(len(Select(self.driver.find_element(By.NAME, "id_empleado")).options), 0)
        self.assertGreater(len(Select(self.driver.find_element(By.NAME, "id_bus")).options), 0)

    def _guardar(self):
        boton = self.driver.find_element(By.CSS_SELECTOR, f"{FORMULARIO} button[type='submit']")
        # El formulario queda al final de la página y otro elemento puede taparlo:
        # se centra el botón en pantalla y se hace clic desde JavaScript.
        self.driver.execute_script(
            "arguments[0].scrollIntoView({block: 'center'}); arguments[0].click();", boton)

    def _mensaje(self):
        return self.wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, ".alert")))

    def _verificar_registro_exitoso(self):
        alerta = self._mensaje()
        self.assertIn("alert-success", alerta.get_attribute("class"))
        self.assertIn("Recaudación registrada correctamente", alerta.text)
        self.assertTrue(self.driver.current_url.endswith("/panel/caja"))
        self.assertEqual(self._contar_filas(), self.filas_antes + 1)

    def _verificar_rechazo_del_servidor(self, texto_error):
        alerta = self._mensaje()
        self.assertIn("alert-danger", alerta.get_attribute("class"))
        self.assertIn(texto_error, alerta.text)
        self.assertEqual(self._contar_filas(), self.filas_antes)

    def _verificar_bloqueo_del_formulario(self):
        """La validación HTML5 impide el envío: sigue en el formulario y no se guarda nada."""
        formulario = self.driver.find_element(By.CSS_SELECTOR, FORMULARIO)
        self.assertFalse(self.driver.execute_script("return arguments[0].checkValidity();", formulario))
        self.assertTrue(formulario.is_displayed())
        self.assertIn("nuevo_caja", self.driver.current_url)
        self.assertEqual(len(self.driver.find_elements(By.CSS_SELECTOR, ".alert")), 0)
        self.assertEqual(self._contar_filas(), self.filas_antes)

    # ---------- casos de prueba ----------
    def test_cp01_datos_validos(self):
        """CP01: datos válidos (clase válida)."""
        self._llenar(self.hoy - timedelta(days=1), "150.50", "CP01 Selenium")
        self._guardar()
        self._verificar_registro_exitoso()
        self.assertIn("S/. 150.50", self.driver.find_element(By.TAG_NAME, "table").text)

    def test_cp02_monto_limite_inferior_valido(self):
        """CP02: monto 0.01, primer valor válido (valor límite)."""
        self._llenar(self.hoy, "0.01")
        self._guardar()
        self._verificar_registro_exitoso()
        self.assertIn("S/. 0.01", self.driver.find_element(By.TAG_NAME, "table").text)

    def test_cp03_monto_cero(self):
        """CP03: monto 0, valor límite inválido."""
        self._llenar(self.hoy, "0")
        self._guardar()
        self._verificar_rechazo_del_servidor("El monto debe ser mayor que 0.")

    def test_cp04_monto_negativo(self):
        """CP04: monto negativo (clase inválida)."""
        self._llenar(self.hoy, "-10")
        self._guardar()
        self._verificar_rechazo_del_servidor("El monto debe ser mayor que 0.")

    def test_cp05_monto_vacio(self):
        """CP05: monto vacío (campo obligatorio)."""
        self._llenar(self.hoy, "")
        self._guardar()
        self._verificar_bloqueo_del_formulario()

    def test_cp06_fecha_futura(self):
        """CP06: fecha de mañana, supera el máximo (valor límite inválido)."""
        self._llenar(self.hoy + timedelta(days=1), "100.00")
        self._guardar()
        self._verificar_bloqueo_del_formulario()
        campo_fecha = self.driver.find_element(By.NAME, "fecha")
        self.assertTrue(self.driver.execute_script("return arguments[0].validity.rangeOverflow;", campo_fecha))

    def test_cp07_fecha_de_hoy(self):
        """CP07: fecha de hoy, máximo permitido (valor límite válido)."""
        self._llenar(self.hoy, "100.00")
        self._guardar()
        self._verificar_registro_exitoso()

    def test_cp08_fecha_minima_permitida(self):
        """CP08: fecha 2000-01-01, mínimo permitido (valor límite válido)."""
        self._llenar(date(2000, 1, 1), "100.00")
        self._guardar()
        self._verificar_registro_exitoso()

    def test_cp09_fecha_anterior_al_minimo(self):
        """CP09: fecha 1999-12-31, por debajo del mínimo (valor límite inválido)."""
        self._llenar(date(1999, 12, 31), "100.00")
        self._guardar()
        self._verificar_rechazo_del_servidor("fuera del rango permitido")

    def test_cp10_observacion_vacia(self):
        """CP10: observación vacía (campo opcional, clase válida)."""
        self._llenar(self.hoy, "75.00", "")
        self._guardar()
        self._verificar_registro_exitoso()


if __name__ == "__main__":
    unittest.main()


import unittest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class TestModuloBuses(unittest.TestCase):

    URL_LOGIN = "http://localhost:5000/login"
    URL_BUSES = "http://localhost:5000/panel/buses"

    def setUp(self):
        self.driver = webdriver.Chrome()
        self.wait = WebDriverWait(self.driver, 10)

        self.driver.get(self.URL_LOGIN)

        usuario = self.wait.until(
            EC.visibility_of_element_located((By.NAME, "username"))
        )

        usuario.send_keys("aperez_sup")

        self.driver.find_element(
            By.NAME, "password"
        ).send_keys("stelman123")

        self.driver.find_element(
            By.XPATH, "//button[@type='submit']"
        ).click()

        self.wait.until(
            lambda driver: "login" not in driver.current_url.lower()
        )

    def abrir_modulo_buses(self):
        self.driver.get(self.URL_BUSES)

        self.wait.until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )

    # CP01: Verificar pantalla de gestión de buses
    def test_cp01_verificar_pantalla_buses(self):
        self.abrir_modulo_buses()

        self.assertIn(
            "Gestión de Buses",
            self.driver.page_source
        )

    # CP02: Verificar tabla de registros
    def test_cp02_verificar_tabla_registros(self):
        self.abrir_modulo_buses()

        tablas = self.driver.find_elements(
            By.TAG_NAME, "table"
        )

        self.assertTrue(
            len(tablas) > 0 or "ABC-1234" in self.driver.page_source,
            "No se encontró la tabla ni un registro de buses."
        )

    # CP03: Verificar apertura del formulario
    def test_cp03_abrir_formulario_nuevo(self):
        self.abrir_modulo_buses()

        boton_nuevo = self.wait.until(
            EC.element_to_be_clickable((
                By.XPATH,
                "//*[contains(normalize-space(), 'Nuevo')]"
            ))
        )

        boton_nuevo.click()

        self.wait.until(
            lambda driver:
            len(driver.find_elements(By.TAG_NAME, "form")) > 0
            or "placa" in driver.page_source.lower()
        )

        self.assertTrue(
            len(self.driver.find_elements(By.TAG_NAME, "form")) > 0
            or "placa" in self.driver.page_source.lower()
        )

    # CP04: Verificar cancelación del formulario
    def test_cp04_cancelar_formulario_registro(self):
        self.abrir_modulo_buses()

        boton_nuevo = self.wait.until(
            EC.element_to_be_clickable((
                By.XPATH,
                "//*[contains(normalize-space(), 'Nuevo')]"
            ))
        )

        boton_nuevo.click()

        boton_cancelar = self.wait.until(
            EC.element_to_be_clickable((
                By.XPATH,
                "//button[contains(., 'Cancelar')]"
                " | //a[contains(., 'Cancelar')]"
                " | //button[contains(., 'Volver')]"
                " | //a[contains(., 'Volver')]"
            ))
        )

        boton_cancelar.click()

        self.wait.until(
            lambda driver:
            "Gestión de Buses" in driver.page_source
        )

        self.assertIn(
            "Gestión de Buses",
            self.driver.page_source
        )

    # CP05: Verificar presencia del campo placa
    def test_cp05_validar_presencia_campo_placa(self):
        self.abrir_modulo_buses()

        self.assertIn(
            "PLACA",
            self.driver.page_source.upper()
        )

    # CP06: Verificar presencia del campo modelo
    def test_cp06_validar_presencia_campo_modelo(self):
        self.abrir_modulo_buses()

        self.assertIn(
            "MODELO",
            self.driver.page_source.upper()
        )

    # CP07: Verificar botón editar
    def test_cp07_verificar_boton_editar(self):
        self.abrir_modulo_buses()

        botones_editar = self.driver.find_elements(
            By.XPATH,
            "//*[contains(normalize-space(), 'Editar')]"
        )

        self.assertTrue(
            len(botones_editar) > 0,
            "No se encontró el botón Editar."
        )

    # CP08: Verificar botón desasignar
    def test_cp08_verificar_boton_desasignar(self):
        self.abrir_modulo_buses()

        botones_desasignar = self.driver.find_elements(
            By.XPATH,
            "//*[contains(normalize-space(), 'Desasignar')]"
        )

        self.assertTrue(
            len(botones_desasignar) > 0,
            "No se encontró el botón Desasignar."
        )

    # CP09: Verificar navegación al módulo de buses
    def test_cp09_navegacion_sidebar_buses(self):
        self.abrir_modulo_buses()

        self.assertTrue(
            self.driver.current_url.endswith("/panel/buses"),
            "No se accedió correctamente al módulo de buses."
        )

    # CP10: Verificar persistencia del módulo
    def test_cp10_verificar_persistencia_modulo(self):
        self.abrir_modulo_buses()

        self.driver.refresh()

        self.wait.until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )

        self.assertIn(
            "Gestión de Buses",
            self.driver.page_source
        )

    def tearDown(self):
        if hasattr(self, "driver"):
            self.driver.quit()


if __name__ == "__main__":
    unittest.main(verbosity=2)

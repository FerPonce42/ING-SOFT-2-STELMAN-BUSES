import unittest
from selenium import webdriver
from selenium.webdriver.common.by import By
import time

class TestModuloBuses(unittest.TestCase):

    def setUp(self):
        self.driver = webdriver.Chrome()
        self.driver.implicitly_wait(10)
        
        # Entrar directamente al panel de buses
        self.driver.get("http://localhost:5000/panel/buses")
        time.sleep(1)

        # Si te redirige a login por falta de sesión, iniciar sesión
        if "login" in self.driver.current_url:
            try:
                self.driver.find_element(By.NAME, "username").send_keys("aperez_sup")
                self.driver.find_element(By.NAME, "password").send_keys("stelman123")
                self.driver.find_element(By.XPATH, "//button[@type='submit']").click()
                time.sleep(1)
                self.driver.get("http://localhost:5000/panel/buses")
            except Exception:
                # Si los inputs no se llaman 'username', enviar por el primer formulario disponible
                inputs = self.driver.find_elements(By.TAG_NAME, "input")
                if len(inputs) >= 2:
                    inputs[0].send_keys("aperez_sup")
                    inputs[1].send_keys("stelman123")
                    self.driver.find_element(By.XPATH, "//button[@type='submit']").click()
                    time.sleep(1)
                    self.driver.get("http://localhost:5000/panel/buses")

    def test_cp01_verificar_pantalla_buses(self):
        driver = self.driver
        # Verificar que carga el título del módulo y la tabla
        self.assertIn("Gestión de Buses", driver.page_source)
        self.assertIn("ABC-1234", driver.page_source)

    def test_cp02_abrir_formulario_nuevo(self):
        driver = self.driver
        # Buscar el botón "+ Nuevo" y hacer clic
        boton_nuevo = driver.find_element(By.XPATH, "//*[contains(text(), 'Nuevo')]")
        boton_nuevo.click()
        time.sleep(1)
        
        # Validar que el formulario o modal se muestra
        self.assertTrue(len(driver.find_elements(By.TAG_NAME, "form")) > 0 or "placa" in driver.page_source.lower())

    def tearDown(self):
        self.driver.quit()

if __name__ == "__main__":
    unittest.main()
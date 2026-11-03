import unittest

from selenium import webdriver
from selenium.common.exceptions import TimeoutException, WebDriverException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

BASE_URL = "http://localhost:5000"
URL_LOGIN = f"{BASE_URL}/login"
RUTA_CHOFERES = "/panel/personal/choferes"
URL_CHOFERES = f"{BASE_URL}{RUTA_CHOFERES}"

USUARIO = "aperez_sup"
CLAVE = "stelman123"

# Selectores tomados de las plantillas reales
CAMPO_USUARIO = (By.ID, "usuario")
CAMPO_CLAVE = (By.ID, "password")
BOTON_ENTRAR = (By.CSS_SELECTOR, "button.btn-submit")
TITULO_CHOFERES = (By.TAG_NAME, "h1")


def crear_navegador():
    try:
        return webdriver.Chrome()
    except WebDriverException:
        return webdriver.Edge()


class ChoferesFuncionalTest(unittest.TestCase):

    def setUp(self):
        self.driver = crear_navegador()
        self.driver.maximize_window()
        self.wait = WebDriverWait(self.driver, 10)

    def tearDown(self):
        self.driver.quit()

    # ---------- Helpers ----------
    def login(self):
        d = self.driver
        d.get(URL_LOGIN)
        self.wait.until(EC.visibility_of_element_located(CAMPO_USUARIO)).send_keys(USUARIO)
        d.find_element(*CAMPO_CLAVE).send_keys(CLAVE)
        # OJO: el primer <button> de la página es el del navbar/toggle, no el de entrar.
        d.find_element(*BOTON_ENTRAR).click()
        try:
            self.wait.until(EC.url_contains("/panel"))
        except TimeoutException:
            alertas = d.find_elements(By.CSS_SELECTOR, ".alert")
            detalle = alertas[0].text if alertas else "sin mensaje en pantalla"
            self.fail(f"El login no llegó a /panel. URL actual: {d.current_url}. Mensaje: {detalle}")

    def ir_a_choferes(self):
        self.driver.get(URL_CHOFERES)
        self.wait.until(EC.visibility_of_element_located(TITULO_CHOFERES))

    def filas_con_datos(self):
        """Filas de chofer: tienen varias <td>. Se excluyen el encabezado (<th>)
        y la fila de 'No hay choferes disponibles' (una sola <td colspan=5>)."""
        filas = self.driver.find_elements(By.CSS_SELECTOR, "table tr")
        return [f for f in filas if len(f.find_elements(By.TAG_NAME, "td")) > 1]

    def mensaje_sin_choferes(self):
        return self.driver.find_elements(By.CSS_SELECTOR, "table td[colspan='5']")

    # ---------- Casos de prueba ----------
    def test_cp01_listar_choferes_clase_valida(self):
        """Clase válida: supervisor con ruta activa ve el listado de choferes."""
        self.login()
        self.ir_a_choferes()

        self.assertIn(RUTA_CHOFERES, self.driver.current_url)
        self.assertIn("Gestión de Choferes", self.driver.find_element(*TITULO_CHOFERES).text)
        self.assertIn("Se muestran los choferes que pertenecen a tu ruta",
                      self.driver.find_element(By.TAG_NAME, "body").text)
        self.assertGreater(len(self.filas_con_datos()), 0,
                           "Se esperaba al menos un chofer en el listado")

    def test_cp02_listar_choferes_valor_limite_cero(self):
        """Valor límite 0: con 0 choferes se muestra el aviso; con N>0 se muestran N filas.
        Nunca puede quedar la tabla en blanco."""
        self.login()
        self.ir_a_choferes()

        filas = self.filas_con_datos()
        aviso = self.mensaje_sin_choferes()

        if len(filas) == 0:
            self.assertEqual(len(aviso), 1, "Con 0 choferes debe verse 'No hay choferes disponibles'")
            self.assertIn("No hay choferes disponibles", aviso[0].text)
        else:
            self.assertEqual(len(aviso), 0, "Con choferes listados no debe verse el aviso de vacío")

    def test_cp03_acceso_sin_login_redirige_a_login(self):
        """Clase inválida: sin sesión iniciada se redirige al login."""
        self.driver.get(URL_CHOFERES)
        self.wait.until(EC.url_contains("/login"))
        self.assertIn("/login", self.driver.current_url)
        self.assertNotIn("/panel", self.driver.current_url)


if __name__ == "__main__":
    unittest.main()
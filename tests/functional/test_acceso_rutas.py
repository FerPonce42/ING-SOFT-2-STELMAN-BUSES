import time
import unittest

from selenium import webdriver
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

URL_LOGIN = "http://localhost:5000/login"
MENSAJE_ERROR = "Usuario o contraseña incorrectos"

CAMPO_USUARIO = (By.ID, "usuario")
CAMPO_CLAVE = (By.CSS_SELECTOR, "input[type='password']")
BOTON_ENTRAR = (By.CSS_SELECTOR, "button.btn-submit")


def crear_navegador():
    try:
        return webdriver.Chrome()
    except WebDriverException:
        return webdriver.Edge()


class PruebasIniciarSesion(unittest.TestCase):

    def setUp(self):
        self.navegador = crear_navegador()
        self.navegador.implicitly_wait(2)
        self.espera = WebDriverWait(self.navegador, 5)
        self.navegador.get(URL_LOGIN)

    def tearDown(self):
        self.navegador.quit()

    def llenar_y_enviar(self, usuario, clave):
        self.navegador.find_element(*CAMPO_USUARIO).send_keys(usuario)
        self.navegador.find_element(*CAMPO_CLAVE).send_keys(clave)
        self.navegador.find_element(*BOTON_ENTRAR).click()

    def texto_pagina(self):
        return self.navegador.find_element(By.TAG_NAME, "body").text

    def verificar_no_entra(self):
        self.assertIn("/login", self.navegador.current_url)
        self.assertNotIn("/panel", self.navegador.current_url)

    def verificar_sin_error_500(self):
        self.assertNotIn("Internal Server Error", self.navegador.page_source)

    def test_cp01_credenciales_validas(self):
        self.llenar_y_enviar("aperez_sup", "stelman123")
        self.espera.until(EC.url_contains("/panel"))
        self.assertIn("Bienvenido, aperez_sup", self.texto_pagina())

    def test_cp02_clave_incorrecta(self):
        self.llenar_y_enviar("aperez_sup", "clave_mala")
        self.espera.until(EC.text_to_be_present_in_element((By.TAG_NAME, "body"), MENSAJE_ERROR))
        self.verificar_no_entra()

    def test_cp03_usuario_inexistente(self):
        self.llenar_y_enviar("usuario_x", "stelman123")
        self.espera.until(EC.text_to_be_present_in_element((By.TAG_NAME, "body"), MENSAJE_ERROR))
        self.verificar_no_entra()

    def test_cp04_usuario_vacio(self):
        self.llenar_y_enviar("", "stelman123")
        time.sleep(1)
        self.verificar_no_entra()

    def test_cp05_clave_vacia(self):
        self.llenar_y_enviar("aperez_sup", "")
        time.sleep(1)
        self.verificar_no_entra()

    def test_cp06_ambos_vacios(self):
        self.llenar_y_enviar("", "")
        time.sleep(1)
        self.verificar_no_entra()

    def test_cp07_texto_muy_largo(self):
        self.llenar_y_enviar("a" * 300, "b" * 300)
        time.sleep(1)
        self.verificar_no_entra()
        self.verificar_sin_error_500()

    def test_cp08_espacios_alrededor_del_usuario(self):
        self.llenar_y_enviar(" aperez_sup ", "stelman123")
        time.sleep(1)
        self.verificar_sin_error_500()


if __name__ == "__main__":
    unittest.main()
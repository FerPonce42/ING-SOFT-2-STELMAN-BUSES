"""Pruebas funcionales Selenium para Registrar Incidencia (Firefox).

Ejecutar:
    py -m pip install -U selenium pytest
    py -m pytest tests/functional/test_incidencias.py -v -s

La aplicación debe estar levantada en http://localhost:5000.
Selenium Manager descarga/ubica geckodriver automáticamente.
"""

import unittest
from datetime import date, timedelta

from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select, WebDriverWait


BASE_URL = "http://localhost:5000"
USUARIO = "aperez_sup"
CLAVE = "stelman123"


class TestRegistrarIncidencia(unittest.TestCase):

    def setUp(self):
        options = webdriver.FirefoxOptions()
        self.driver = webdriver.Firefox(options=options)
        self.driver.set_window_size(1440, 1000)
        self.wait = WebDriverWait(self.driver, 15)
        self.registros_creados = []

        self.driver.get(f"{BASE_URL}/login")
        self.wait.until(EC.visibility_of_element_located((By.ID, "usuario"))).send_keys(USUARIO)
        self.driver.find_element(By.ID, "password").send_keys(CLAVE)
        self.driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
        self.wait.until(EC.url_contains("/panel"))

    def tearDown(self):
        # Se intenta retirar únicamente los registros creados por esta prueba.
        # Si la aplicación no permite eliminarlos, no se oculta el resultado del test.
        for tipo, descripcion in self.registros_creados:
            try:
                ruta = (
                    "/panel/incidencias/disciplinarias"
                    if tipo == "disciplinaria"
                    else "/panel/incidencias/operativas"
                )
                self.driver.get(BASE_URL + ruta)
                fila = self.wait.until(EC.presence_of_element_located((
                    By.XPATH,
                    f"//tr[.//td[contains(normalize-space(.), '{descripcion}')]]"
                )))
                enlace = fila.find_element(By.XPATH, ".//a[contains(@href, 'eliminar')]")
                self.driver.execute_script("arguments[0].scrollIntoView({block:'center'});", enlace)
                self.driver.execute_script("arguments[0].click();", enlace)
                self.wait.until(EC.alert_is_present()).accept()
            except Exception:
                pass
        self.driver.quit()

    def abrir_formulario(self, tipo):
        ruta = (
            "/panel/incidencias/disciplinarias?nuevo_incidencia=true"
            if tipo == "disciplinaria"
            else "/panel/incidencias/operativas?nuevo_incidencia=true"
        )
        self.driver.get(BASE_URL + ruta)
        return self.wait.until(EC.presence_of_element_located((
            By.CSS_SELECTOR, "#modal-nueva form[method='post']"
        )))

    def seleccionar_primera_opcion(self, form, campo):
        select = Select(form.find_element(By.NAME, campo))
        opciones = [op for op in select.options if op.get_attribute("value")]
        self.assertTrue(opciones, f"No hay opciones disponibles para {campo}")
        select.select_by_value(opciones[0].get_attribute("value"))

    def llenar_datos_base(self, form, descripcion):
        form.find_element(By.NAME, "fecha").send_keys(date.today().isoformat())
        form.find_element(By.NAME, "descripcion").send_keys(descripcion)
        self.seleccionar_primera_opcion(form, "id_bus")
        self.seleccionar_primera_opcion(form, "estado")

    def enviar_formulario(self, form):
        boton = form.find_element(By.CSS_SELECTOR, "button[type='submit']")
        self.driver.execute_script(
            "arguments[0].scrollIntoView({block:'center'});", boton
        )
        self.wait.until(lambda d: boton.is_displayed() and boton.is_enabled())
        # Ejecuta el clic sobre el botón real. Evita overlays y cabeceras fijas
        # que pueden interceptar el punto de clic en Firefox.
        self.driver.execute_script("arguments[0].click();", boton)
        self.wait.until(lambda d: d.execute_script(
            "return document.readyState"
        ) == "complete")

    def assert_mensaje(self, texto):
        self.wait.until(lambda d: texto in d.page_source)
        self.assertIn(texto, self.driver.page_source)

    def test_cp01_registrar_incidencia_disciplinaria_valida(self):
        descripcion = "SELENIUM-DISC-CP01"
        form = self.abrir_formulario("disciplinaria")
        self.llenar_datos_base(form, descripcion)
        self.seleccionar_primera_opcion(form, "id_tipo_disciplinaria")
        form.find_element(By.NAME, "sancion").send_keys("Amonestación de prueba")
        self.enviar_formulario(form)
        self.assert_mensaje("Incidencia disciplinaria registrada.")
        self.assertIn(descripcion, self.driver.page_source)
        self.registros_creados.append(("disciplinaria", descripcion))

    def test_cp02_descripcion_disciplinaria_vacia(self):
        form = self.abrir_formulario("disciplinaria")
        self.llenar_datos_base(form, "")
        self.seleccionar_primera_opcion(form, "id_tipo_disciplinaria")
        form.find_element(By.NAME, "sancion").send_keys("Amonestación")
        campo = form.find_element(By.NAME, "descripcion")
        self.assertFalse(self.driver.execute_script(
            "return arguments[0].checkValidity()", campo
        ))

    def test_cp03_fecha_disciplinaria_futura(self):
        """El servidor debe rechazar una fecha del siguiente año."""
        form = self.abrir_formulario("disciplinaria")
        campo = form.find_element(By.NAME, "fecha")

        # Se elimina el límite HTML para probar la validación del servidor.
        self.driver.execute_script(
            "arguments[0].removeAttribute('max');", campo
        )

        # Fecha del siguiente año.
        campo.send_keys(f"{date.today().year + 1}-01-15")

        form.find_element(By.NAME, "descripcion").send_keys("SELENIUM-DISC-CP03")
        self.seleccionar_primera_opcion(form, "id_bus")
        self.seleccionar_primera_opcion(form, "estado")
        self.seleccionar_primera_opcion(form, "id_tipo_disciplinaria")
        form.find_element(By.NAME, "sancion").send_keys("Amonestación de prueba")

        self.enviar_formulario(form)

        # Verificar que el servidor rechace la fecha futura.
        self.wait.until(lambda d: "fuera del rango permitido" in d.page_source.lower())

        self.assertNotIn(
            "Incidencia disciplinaria registrada.",
            self.driver.find_element(By.TAG_NAME, "body").text
        )

    def test_cp04_descripcion_disciplinaria_supera_500_caracteres(self):
        descripcion = "D" * 501
        form = self.abrir_formulario("disciplinaria")
        self.llenar_datos_base(form, descripcion)
        self.seleccionar_primera_opcion(form, "id_tipo_disciplinaria")
        form.find_element(By.NAME, "sancion").send_keys("Amonestación")
        self.enviar_formulario(form)
        self.assert_mensaje("La descripción no puede superar 500 caracteres.")
        self.assertNotIn("Incidencia disciplinaria registrada.", self.driver.page_source)

    def test_cp05_sancion_disciplinaria_vacia(self):
        form = self.abrir_formulario("disciplinaria")
        self.llenar_datos_base(form, "SELENIUM-DISC-CP05")
        self.seleccionar_primera_opcion(form, "id_tipo_disciplinaria")
        campo = form.find_element(By.NAME, "sancion")
        self.assertFalse(self.driver.execute_script(
            "return arguments[0].checkValidity()", campo
        ))

    def test_cp06_registrar_incidencia_operativa_valida(self):
        descripcion = "SELENIUM-OPER-CP06"
        form = self.abrir_formulario("operativa")
        self.llenar_datos_base(form, descripcion)
        Select(form.find_element(By.NAME, "gravedad")).select_by_visible_text("Moderada")
        form.find_element(By.NAME, "costo").send_keys("150.00")
        seguro = form.find_element(By.NAME, "requiere_seguro")
        self.driver.execute_script("arguments[0].click();", seguro)
        self.enviar_formulario(form)
        self.assert_mensaje("Incidencia operativa registrada.")
        self.assertIn(descripcion, self.driver.page_source)
        self.registros_creados.append(("operativa", descripcion))

    def test_cp07_costo_operativo_vacio_se_acepta_como_cero(self):
        descripcion = "SELENIUM-OPER-CP07"
        form = self.abrir_formulario("operativa")
        self.llenar_datos_base(form, descripcion)
        Select(form.find_element(By.NAME, "gravedad")).select_by_visible_text("Leve")
        form.find_element(By.NAME, "costo").clear()
        self.enviar_formulario(form)
        self.assert_mensaje("Incidencia operativa registrada.")
        self.assertIn(descripcion, self.driver.page_source)
        self.registros_creados.append(("operativa", descripcion))

    def test_cp08_gravedad_operativa_limite_inferior_leve(self):
        descripcion = "SELENIUM-OPER-CP08"
        form = self.abrir_formulario("operativa")
        self.llenar_datos_base(form, descripcion)
        Select(form.find_element(By.NAME, "gravedad")).select_by_visible_text("Leve")
        self.enviar_formulario(form)
        self.assert_mensaje("Incidencia operativa registrada.")
        self.assertIn(descripcion, self.driver.page_source)
        self.registros_creados.append(("operativa", descripcion))

    def test_cp09_gravedad_operativa_limite_superior_grave(self):
        descripcion = "SELENIUM-OPER-CP09"
        form = self.abrir_formulario("operativa")
        self.llenar_datos_base(form, descripcion)
        Select(form.find_element(By.NAME, "gravedad")).select_by_visible_text("Grave")
        self.enviar_formulario(form)
        self.assert_mensaje("Incidencia operativa registrada.")
        self.assertIn(descripcion, self.driver.page_source)
        self.registros_creados.append(("operativa", descripcion))

    def test_cp10_descripcion_operativa_vacia(self):
        form = self.abrir_formulario("operativa")
        self.llenar_datos_base(form, "")
        Select(form.find_element(By.NAME, "gravedad")).select_by_visible_text("Leve")
        campo = form.find_element(By.NAME, "descripcion")
        self.assertFalse(self.driver.execute_script(
            "return arguments[0].checkValidity()", campo
        ))

    def test_cp11_costo_operativo_negativo(self):
        form = self.abrir_formulario("operativa")
        self.llenar_datos_base(form, "SELENIUM-OPER-CP11")
        Select(form.find_element(By.NAME, "gravedad")).select_by_visible_text("Moderada")
        costo = form.find_element(By.NAME, "costo")
        costo.send_keys("-1")
        self.enviar_formulario(form)
        self.assert_mensaje("El costo debe ser mayor o igual que 0.")
        self.assertNotIn("Incidencia operativa registrada.", self.driver.page_source)


if __name__ == "__main__":
    unittest.main(verbosity=2)

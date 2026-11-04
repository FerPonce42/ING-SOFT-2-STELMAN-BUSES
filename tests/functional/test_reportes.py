"""Pruebas funcionales (Selenium + unittest) de: Reportes > Generar documentación Excel.

Requisitos (en la PC de cada integrante, fuera de Docker):
    py -m pip install selenium pytest
    docker compose up --build      # la app debe estar en http://localhost:5000

Ejecutar:
    py -m pytest tests/functional/test_reportes.py -v
"""
import os
import re
import shutil
import tempfile
import time
import unittest
import urllib.request
import xml.etree.ElementTree as ET
import zipfile

import pytest

pytest.importorskip("selenium", reason="Selenium no está instalado (py -m pip install selenium)")

from selenium import webdriver  # noqa: E402
from selenium.webdriver.common.by import By  # noqa: E402
from selenium.webdriver.support import expected_conditions as EC  # noqa: E402
from selenium.webdriver.support.ui import WebDriverWait  # noqa: E402

BASE_URL = os.environ.get("STELMAN_URL", "http://localhost:5000")
USUARIO = "aperez_sup"
CLAVE = "stelman123"
PATRON_NOMBRE = re.compile(r"^DOCUMENTACION_BD_.+_\d{8}_\d{4}\.xlsx$")
HOJAS_FIJAS = ["PORTADA", "Índice", "CREATE", "ERD_TEXTUAL"]
NS = "{http://schemas.openxmlformats.org/spreadsheetml/2006/main}"


def hojas_del_excel(ruta):
    """Nombres de las hojas de un .xlsx, leídos sin librerías externas."""
    with zipfile.ZipFile(ruta) as z:
        raiz = ET.fromstring(z.read("xl/workbook.xml"))
    return [h.get("name") for h in raiz.iter(f"{NS}sheet")]


class PruebasGenerarDocumentacionExcel(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        try:
            urllib.request.urlopen(f"{BASE_URL}/login", timeout=5)
        except Exception as exc:  # la app no está levantada
            raise unittest.SkipTest(
                f"La app no responde en {BASE_URL} (docker compose up --build): {exc}")

    def setUp(self):
        self.carpeta = tempfile.mkdtemp(prefix="stelman_descargas_")
        opciones = webdriver.ChromeOptions()
        opciones.add_experimental_option("prefs", {
            "download.default_directory": self.carpeta,
            "download.prompt_for_download": False,
            "profile.default_content_setting_values.automatic_downloads": 1,
        })
        if os.environ.get("STELMAN_HEADLESS") == "1":
            opciones.add_argument("--headless=new")
        self.driver = webdriver.Chrome(options=opciones)
        self.espera = WebDriverWait(self.driver, 15)

    def tearDown(self):
        self.driver.quit()
        shutil.rmtree(self.carpeta, ignore_errors=True)
        self.driver = self.carpeta = None

    # ---------- ayudas ----------
    def _iniciar_sesion(self):
        self.driver.get(f"{BASE_URL}/login")
        self.driver.find_element(By.ID, "usuario").send_keys(USUARIO)
        self.driver.find_element(By.ID, "password").send_keys(CLAVE)
        self.driver.find_element(By.CSS_SELECTOR, "button.btn-submit").click()
        self.espera.until(EC.url_contains("/panel"))

    def _abrir_reportes_desde_el_menu(self):
        self.driver.find_element(By.CSS_SELECTOR, 'a[href="/panel/reportes"]').click()
        self.espera.until(EC.url_contains("/panel/reportes"))

    def _clic_en_exportar(self):
        enlace = self.espera.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'a[href="/exportar_excel"]')))
        # reportes.css define html { scroll-behavior: smooth }: sin scroll instantáneo,
        # Selenium hace clic mientras la página aún se desplaza (ElementClickIntercepted).
        self.driver.execute_script(
            "arguments[0].scrollIntoView({block: 'center', behavior: 'instant'});", enlace)
        self.espera.until(EC.element_to_be_clickable(enlace)).click()

    def _archivos_descargados(self):
        return sorted(f for f in os.listdir(self.carpeta)
                      if not f.endswith((".crdownload", ".tmp")))

    def _esperar_descargas(self, cantidad=1, segundos=30):
        limite = time.time() + segundos
        while time.time() < limite:
            hay_parcial = any(f.endswith(".crdownload") for f in os.listdir(self.carpeta))
            if not hay_parcial and len(self._archivos_descargados()) >= cantidad:
                break
            time.sleep(0.5)
        return [os.path.join(self.carpeta, f) for f in self._archivos_descargados()]

    def _exportar_y_esperar(self):
        self._iniciar_sesion()
        self._abrir_reportes_desde_el_menu()
        self._clic_en_exportar()
        archivos = self._esperar_descargas(1)
        self.assertEqual(len(archivos), 1, "No se descargó el archivo Excel")
        return archivos[0]

    # ---------- casos de prueba ----------
    def test_cp01_abrir_reportes_desde_el_menu(self):
        self._iniciar_sesion()
        self._abrir_reportes_desde_el_menu()
        self.assertIn("/panel/reportes", self.driver.current_url)
        self.assertIn("Reportes del Sistema", self.driver.find_element(By.TAG_NAME, "h1").text)
        boton = self.driver.find_element(By.CSS_SELECTOR, 'a[href="/exportar_excel"]')
        self.assertTrue(boton.is_displayed())
        self.assertIn("Exportar Estructura Completa", boton.text)

    def test_cp02_exportar_descarga_un_xlsx_con_nombre_valido(self):
        ruta = self._exportar_y_esperar()
        self.assertRegex(os.path.basename(ruta), PATRON_NOMBRE)

    def test_cp03_el_excel_trae_las_hojas_fijas(self):
        ruta = self._exportar_y_esperar()
        hojas = hojas_del_excel(ruta)
        for hoja in HOJAS_FIJAS:
            self.assertIn(hoja, hojas)

    def test_cp04_limite_inferior_archivo_no_vacio_y_con_hojas_de_tablas(self):
        ruta = self._exportar_y_esperar()
        self.assertGreater(os.path.getsize(ruta), 0)
        self.assertGreater(len(hojas_del_excel(ruta)), len(HOJAS_FIJAS))

    def test_cp05_exportar_dos_veces_seguidas_sin_error(self):
        self._iniciar_sesion()
        self._abrir_reportes_desde_el_menu()
        self._clic_en_exportar()
        self._esperar_descargas(1)
        self._clic_en_exportar()
        archivos = self._esperar_descargas(2)
        self.assertEqual(len(archivos), 2)
        self.assertIn("/panel/reportes", self.driver.current_url)
        self.assertNotIn("Internal Server Error", self.driver.page_source)

    def test_cp06_sin_sesion_reportes_redirige_al_login(self):
        self.driver.get(f"{BASE_URL}/panel/reportes")
        self.espera.until(EC.url_contains("/login"))
        self.assertNotIn("/panel", self.driver.current_url)
        self.assertEqual(self.driver.find_elements(By.CSS_SELECTOR, 'a[href="/exportar_excel"]'), [])

    def test_cp07_sin_sesion_exportar_redirige_al_login_y_no_descarga(self):
        self.driver.get(f"{BASE_URL}/exportar_excel")
        self.espera.until(EC.url_contains("/login"))
        time.sleep(3)
        self.assertEqual(self._archivos_descargados(), [])

    def test_cp08_sesion_cerrada_exportar_ya_no_descarga(self):
        self._iniciar_sesion()
        self.driver.get(f"{BASE_URL}/logout")
        self.espera.until(EC.url_contains("/login"))
        self.driver.get(f"{BASE_URL}/exportar_excel")
        self.espera.until(EC.url_contains("/login"))
        time.sleep(3)
        self.assertEqual(self._archivos_descargados(), [])


if __name__ == "__main__":
    unittest.main()
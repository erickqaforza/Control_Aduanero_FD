import re

import allure
from playwright.sync_api import Page, expect


class ControlAduaneroPage:
    def __init__(self, page: Page):
        self.page = page

    def _take_screenshot(self, name: str) -> None:
        try:
            screenshot = self.page.screenshot(type="png")
            allure.attach(screenshot, name=name, attachment_type=allure.attachment_type.PNG)
        except Exception as error:
            print(f"No se pudo adjuntar screenshot: {error}")

    @allure.step("Abrir Control Aduanero FD")
    def abrir(self, url: str) -> None:
        self.page.goto(url, wait_until="domcontentloaded", timeout=120000)
        self._take_screenshot("abrir_control_aduanero")

    @allure.step("Validar titulo de pagina")
    def validar_titulo(self, titulo_esperado: str) -> None:
        expect(self.page).to_have_title(titulo_esperado, timeout=30000)
        self._take_screenshot("validar_titulo")

    @allure.step("Iniciar sesion")
    def login(self, pais: str, usuario: str, password: str) -> None:
        self.seleccionar_pais(pais)
        self.page.get_by_role("textbox", name=re.compile("correo|email", re.I)).fill(usuario)
        self.page.get_by_role("textbox", name=re.compile("contrase|password", re.I)).fill(password)
        self.page.get_by_role("button", name=re.compile("iniciar sesi[oó]n", re.I)).click()
        self.page.wait_for_load_state("networkidle")
        self._take_screenshot("login")

    @allure.step("Seleccionar pais")
    def seleccionar_pais(self, pais: str) -> None:
        selector_pais = self.page.get_by_role("combobox").first
        if selector_pais.count() > 0:
            try:
                selector_pais.select_option(label=pais)
                return
            except Exception:
                selector_pais.click()

        self.page.get_by_text(pais, exact=True).click(timeout=30000)
        self._take_screenshot(f"pais_{pais}")

    @allure.step("Aceptar modal informativo")
    def aceptar_modal_entendido(self) -> None:
        self.page.get_by_role("button", name=re.compile("entendido", re.I)).click(timeout=30000)
        self.page.wait_for_load_state("networkidle")
        self._take_screenshot("modal_entendido")

    @allure.step("Validar login exitoso")
    def validar_login_exitoso(self, nombre_usuario: str) -> None:
        expect(self.page.get_by_role("heading", name=re.compile("gu[ií]as madre", re.I))).to_be_visible(timeout=60000)
        expect(self.page.get_by_text(re.compile("gesti[oó]n de manifiestos", re.I))).to_be_visible()
        expect(self.page.get_by_text("Manifiestos", exact=True)).to_be_visible()
        expect(self.page.get_by_text(nombre_usuario, exact=True)).to_be_visible()
        self._take_screenshot("login_exitoso")

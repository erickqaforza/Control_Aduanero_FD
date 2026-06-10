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
    def login(self, usuario: str, password: str) -> None:
        self.page.get_by_role("textbox", name="Usuario").fill(usuario)
        self.page.get_by_role("textbox", name="Password").fill(password)
        self.page.get_by_role("button", name="Iniciar sesion").click()
        self.page.wait_for_load_state("networkidle")
        self._take_screenshot("login")
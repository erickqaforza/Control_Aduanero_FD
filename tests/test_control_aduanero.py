import os

from pytest_bdd import given, parsers, scenarios, then

from pages.control_aduanero_page import ControlAduaneroPage

scenarios("../features/control_aduanero.feature")


@given("el usuario abre Control Aduanero FD")
def abrir_control_aduanero(control_aduanero_page: ControlAduaneroPage):
    url = os.getenv("BASE_URL")
    if not url:
        raise ValueError("Configura BASE_URL en el archivo .env")
    control_aduanero_page.abrir(url)


@then(parsers.parse('el titulo de la pagina debe ser "{titulo}"'))
def validar_titulo(control_aduanero_page: ControlAduaneroPage, titulo: str):
    control_aduanero_page.validar_titulo(titulo)
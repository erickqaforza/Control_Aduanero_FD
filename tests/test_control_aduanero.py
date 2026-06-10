import os

from pytest_bdd import given, parsers, scenarios, then, when

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


@when(parsers.parse('el usuario inicia sesion en el pais "{pais}"'))
def iniciar_sesion(control_aduanero_page: ControlAduaneroPage, pais: str):
    usuario = os.getenv("CONTROL_ADUANERO_USER")
    password = os.getenv("CONTROL_ADUANERO_PASSWORD")
    if not usuario or not password:
        raise ValueError(
            "Configura CONTROL_ADUANERO_USER y CONTROL_ADUANERO_PASSWORD en el archivo .env"
        )
    control_aduanero_page.login(pais=pais, usuario=usuario, password=password)


@when("acepta el modal informativo")
def aceptar_modal(control_aduanero_page: ControlAduaneroPage):
    control_aduanero_page.aceptar_modal_entendido()


@then(parsers.parse('debe visualizar la pantalla de guias madre para el usuario "{nombre_usuario}"'))
def validar_login_exitoso(control_aduanero_page: ControlAduaneroPage, nombre_usuario: str):
    control_aduanero_page.validar_login_exitoso(nombre_usuario)

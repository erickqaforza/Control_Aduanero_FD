import os
import random
import string

import pytest
from pytest_bdd import given, parsers, scenarios, then, when

from pages.control_aduanero_page import ControlAduaneroPage, GuiaMadre

scenarios("../features/control_aduanero.feature")


@pytest.fixture
def contexto_aduana():
    return {}


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


@when(parsers.parse('el usuario intenta iniciar sesion en el pais "{pais}" con "{tipo_error}"'))
def iniciar_sesion_credenciales_invalidas(
    control_aduanero_page: ControlAduaneroPage,
    pais: str,
    tipo_error: str,
):
    usuario = os.getenv("CONTROL_ADUANERO_USER")
    password = os.getenv("CONTROL_ADUANERO_PASSWORD")
    if not usuario or not password:
        raise ValueError(
            "Configura CONTROL_ADUANERO_USER y CONTROL_ADUANERO_PASSWORD en el archivo .env"
        )

    credenciales_invalidas = {
        "correo_incorrecto": {
            "usuario": f"qa.invalid.{usuario}",
            "password": password,
        },
        "contrasena_incorrecta": {
            "usuario": usuario,
            "password": "PasswordIncorrecta#123",
        },
    }
    if tipo_error not in credenciales_invalidas:
        raise ValueError(f"Tipo de error no soportado: {tipo_error}")

    credenciales = credenciales_invalidas[tipo_error]
    control_aduanero_page.login(
        pais=pais,
        usuario=credenciales["usuario"],
        password=credenciales["password"],
    )


@when("acepta el modal informativo")
def aceptar_modal(control_aduanero_page: ControlAduaneroPage):
    control_aduanero_page.aceptar_modal_entendido()


@then(parsers.parse('debe visualizar la pantalla de guias madre para el usuario "{nombre_usuario}"'))
def validar_login_exitoso(control_aduanero_page: ControlAduaneroPage, nombre_usuario: str):
    control_aduanero_page.validar_login_exitoso(nombre_usuario)


@then("debe visualizar un mensaje de credenciales invalidas")
def validar_login_fallido(control_aduanero_page: ControlAduaneroPage):
    control_aduanero_page.validar_credenciales_invalidas()


@when(parsers.parse('crea una guia madre con moneda "{moneda}"'))
def crear_guia_madre(
    control_aduanero_page: ControlAduaneroPage,
    contexto_aduana: dict,
    moneda: str,
):
    guia_madre = generar_guia_madre(moneda)
    contexto_aduana["guia_madre"] = guia_madre
    control_aduanero_page.abrir_formulario_guia_madre()
    control_aduanero_page.crear_guia_madre(guia_madre)


@then("debe visualizar el mensaje de guia madre creada")
def validar_guia_madre_creada(
    control_aduanero_page: ControlAduaneroPage,
    contexto_aduana: dict,
):
    guia_madre = contexto_aduana["guia_madre"]
    control_aduanero_page.validar_guia_madre_creada(guia_madre.numero_guia)


def generar_guia_madre(moneda: str) -> GuiaMadre:
    origenes_destinos = ["GT", "HN", "RC", "MIAMI", "FRA"]
    origen = random.choice(origenes_destinos)
    destino = random.choice([valor for valor in origenes_destinos if valor != origen])
    return GuiaMadre(
        numero_guia=f"AUTO{_alfanumerico(8)}",
        numero_vuelo=f"V{_alfanumerico(7)}",
        origen=origen,
        destino=destino,
        total_cajas=_numero_4_digitos(),
        total_guias_individuales=_numero_4_digitos(),
        peso_declarado=_numero_4_digitos(),
        valor_declarado=f"{random.randint(1000, 9999)}.{random.randint(0, 99):02d}",
        moneda=moneda,
    )


def _alfanumerico(longitud: int) -> str:
    caracteres = string.ascii_uppercase + string.digits
    return "".join(random.choice(caracteres) for _ in range(longitud))


def _numero_4_digitos() -> str:
    return str(random.randint(1000, 9999))

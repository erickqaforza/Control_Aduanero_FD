import os
import random
import string
from pathlib import Path

import allure
import pytest
from pytest_bdd import given, parsers, scenarios, then, when

from pages.control_aduanero_page import Consolidado, ControlAduaneroPage, GuiaMadre

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
def iniciar_sesion(
    control_aduanero_page: ControlAduaneroPage,
    contexto_aduana: dict,
    pais: str,
):
    contexto_aduana["pais"] = pais
    allure.dynamic.parameter("pais", pais)
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
    contexto_aduana: dict,
    pais: str,
    tipo_error: str,
):
    contexto_aduana["pais"] = pais
    allure.dynamic.title(f"Login fallido - {tipo_error}")
    allure.dynamic.feature("Login")
    allure.dynamic.story("Validar credenciales invalidas")
    allure.dynamic.suite("Control Aduanero FD")
    allure.dynamic.severity(allure.severity_level.NORMAL)
    allure.dynamic.parameter("pais", pais)
    allure.dynamic.parameter("tipo_error", tipo_error)

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
def validar_login_exitoso(
    control_aduanero_page: ControlAduaneroPage,
    contexto_aduana: dict,
    nombre_usuario: str,
):
    pais = contexto_aduana.get("pais", "Guatemala")
    allure.dynamic.title(f"Login exitoso - {pais}")
    allure.dynamic.feature("Login")
    allure.dynamic.story("Login exitoso por pais")
    allure.dynamic.suite("Control Aduanero FD")
    allure.dynamic.severity(allure.severity_level.CRITICAL)
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
    pais = contexto_aduana.get("pais", "Guatemala")
    guia_madre = generar_guia_madre(moneda)
    contexto_aduana["guia_madre"] = guia_madre
    allure.dynamic.title(f"Crear guia madre - {pais} - {moneda}")
    allure.dynamic.feature("Guias madre")
    allure.dynamic.story("Crear guia madre por pais y moneda")
    allure.dynamic.suite("Control Aduanero FD")
    allure.dynamic.sub_suite("Manifiestos")
    allure.dynamic.severity(allure.severity_level.CRITICAL)
    allure.dynamic.parameter("pais", pais)
    allure.dynamic.parameter("moneda", moneda)
    allure.dynamic.parameter("numero_guia", guia_madre.numero_guia)
    allure.dynamic.parameter("numero_vuelo", guia_madre.numero_vuelo)
    allure.dynamic.parameter("origen", guia_madre.origen)
    allure.dynamic.parameter("destino", guia_madre.destino)
    allure.dynamic.parameter("valor_declarado", guia_madre.valor_declarado)

    allure.attach(
        (
            f"Pais: {pais}\n"
            f"Moneda: {moneda}\n"
            f"No. Guia: {guia_madre.numero_guia}\n"
            f"Numero de vuelo: {guia_madre.numero_vuelo}\n"
            f"Origen: {guia_madre.origen}\n"
            f"Destino: {guia_madre.destino}\n"
            f"Total cajas: {guia_madre.total_cajas}\n"
            f"Total guias individuales: {guia_madre.total_guias_individuales}\n"
            f"Peso declarado: {guia_madre.peso_declarado}\n"
            f"Valor declarado: {guia_madre.valor_declarado}\n"
        ),
        name="Datos de guia madre",
        attachment_type=allure.attachment_type.TEXT,
    )

    control_aduanero_page.abrir_formulario_guia_madre()
    control_aduanero_page.crear_guia_madre(guia_madre)


@then("debe visualizar el mensaje de guia madre creada")
def validar_guia_madre_creada(
    control_aduanero_page: ControlAduaneroPage,
    contexto_aduana: dict,
):
    guia_madre = contexto_aduana["guia_madre"]
    control_aduanero_page.validar_guia_madre_creada(guia_madre.numero_guia)


@when(parsers.parse('intenta crear una guia madre sin completar el campo "{campo}"'))
def intentar_crear_guia_madre_sin_campo(
    control_aduanero_page: ControlAduaneroPage,
    contexto_aduana: dict,
    campo: str,
):
    pais = contexto_aduana.get("pais", "Guatemala")
    guia_madre = generar_guia_madre("GTQ")
    contexto_aduana["guia_madre"] = guia_madre
    contexto_aduana["campo_obligatorio"] = campo

    allure.dynamic.title(f"Validar campo obligatorio - Guia madre - {campo}")
    allure.dynamic.feature("Guias madre")
    allure.dynamic.story("Validar campos obligatorios")
    allure.dynamic.suite("Control Aduanero FD")
    allure.dynamic.sub_suite("Manifiestos")
    allure.dynamic.severity(allure.severity_level.NORMAL)
    allure.dynamic.parameter("pais", pais)
    allure.dynamic.parameter("campo_obligatorio", campo)
    allure.dynamic.parameter("moneda", guia_madre.moneda)

    control_aduanero_page.abrir_formulario_guia_madre()
    control_aduanero_page.intentar_crear_guia_madre_sin_campo(guia_madre, campo)


@then(parsers.parse('debe validar que el campo "{campo}" es obligatorio'))
def validar_campo_obligatorio(control_aduanero_page: ControlAduaneroPage, campo: str):
    control_aduanero_page.validar_campo_obligatorio(campo)


@when("entrega a aduana la primera guia madre disponible")
def entregar_guia_madre_a_aduana(
    control_aduanero_page: ControlAduaneroPage,
    contexto_aduana: dict,
):
    pais = contexto_aduana.get("pais", "Guatemala")
    allure.dynamic.title(f"Entregar guia madre a aduana - {pais}")
    allure.dynamic.feature("Guias madre")
    allure.dynamic.story("Entrega a aduana")
    allure.dynamic.suite("Control Aduanero FD")
    allure.dynamic.sub_suite("Manifiestos")
    allure.dynamic.severity(allure.severity_level.CRITICAL)
    allure.dynamic.parameter("pais", pais)

    numero_guia = control_aduanero_page.entregar_primera_guia_madre_disponible()
    contexto_aduana["numero_guia_entregada"] = numero_guia
    allure.dynamic.parameter("numero_guia", numero_guia)


@then(parsers.parse('debe visualizar la guia madre en estado "{estado}"'))
def validar_entrega_aduana(
    control_aduanero_page: ControlAduaneroPage,
    contexto_aduana: dict,
    estado: str,
):
    numero_guia = contexto_aduana["numero_guia_entregada"]
    control_aduanero_page.validar_estado_guia_madre(numero_guia, estado)


@when("abre el detalle de una guia madre en estado arribo a aduana")
def abrir_detalle_guia_arribo_aduana(
    control_aduanero_page: ControlAduaneroPage,
    contexto_aduana: dict,
):
    pais = contexto_aduana.get("pais", "Guatemala")
    allure.dynamic.title(f"Agregar consolidados - {pais}")
    allure.dynamic.feature("Guias madre")
    allure.dynamic.story("Agregar consolidado")
    allure.dynamic.suite("Control Aduanero FD")
    allure.dynamic.sub_suite("Manifiestos")
    allure.dynamic.severity(allure.severity_level.CRITICAL)
    allure.dynamic.parameter("pais", pais)

    numero_guia = control_aduanero_page.abrir_detalle_primera_guia_en_arribo_aduana()
    contexto_aduana["numero_guia_consolidado"] = numero_guia
    allure.dynamic.parameter("numero_guia", numero_guia)


@when("agrega los consolidados verde rojo y amarillo")
def agregar_consolidados(
    control_aduanero_page: ControlAduaneroPage,
    contexto_aduana: dict,
):
    consolidados = generar_consolidados()
    contexto_aduana["consolidados"] = consolidados

    for consolidado in consolidados:
        allure.dynamic.parameter(
            f"archivo_{consolidado.selectivo.lower()}",
            consolidado.archivo.name,
        )
        allure.attach(
            (
                f"Selectivo: {consolidado.selectivo}\n"
                f"Nombre: {consolidado.nombre}\n"
                f"Descripcion: {consolidado.descripcion}\n"
                f"Archivo: {consolidado.archivo}\n"
            ),
            name=f"Datos consolidado {consolidado.selectivo}",
            attachment_type=allure.attachment_type.TEXT,
        )
        control_aduanero_page.agregar_consolidado(consolidado)


@then("debe visualizar los consolidados cargados en el detalle")
def validar_consolidados_cargados(
    control_aduanero_page: ControlAduaneroPage,
    contexto_aduana: dict,
):
    for consolidado in contexto_aduana["consolidados"]:
        control_aduanero_page.validar_consolidado_cargado(consolidado)


@when("abre el detalle de una guia madre en estado carga de selectivos")
def abrir_detalle_guia_carga_selectivos(
    control_aduanero_page: ControlAduaneroPage,
    contexto_aduana: dict,
):
    pais = contexto_aduana.get("pais", "Guatemala")
    allure.dynamic.title(f"Despachar cajas - {pais}")
    allure.dynamic.feature("Guias madre")
    allure.dynamic.story("Despacho de cajas")
    allure.dynamic.suite("Control Aduanero FD")
    allure.dynamic.sub_suite("Manifiestos")
    allure.dynamic.severity(allure.severity_level.CRITICAL)
    allure.dynamic.parameter("pais", pais)

    numero_guia = control_aduanero_page.abrir_detalle_primera_guia_en_carga_selectivos()
    contexto_aduana["numero_guia_despacho"] = numero_guia
    allure.dynamic.parameter("numero_guia", numero_guia)


@when("abre el detalle del primer consolidado disponible")
def abrir_detalle_consolidado_disponible(
    control_aduanero_page: ControlAduaneroPage,
    contexto_aduana: dict,
):
    nombre_consolidado = control_aduanero_page.abrir_detalle_primer_consolidado_disponible()
    contexto_aduana["nombre_consolidado_despacho"] = nombre_consolidado
    allure.dynamic.parameter("nombre_consolidado", nombre_consolidado)


@when("despacha las cajas del consolidado")
def despachar_cajas(control_aduanero_page: ControlAduaneroPage):
    control_aduanero_page.despachar_cajas()


@then("debe visualizar la guia madre despachada en estado completado")
def validar_guia_madre_despachada(
    control_aduanero_page: ControlAduaneroPage,
    contexto_aduana: dict,
):
    control_aduanero_page.validar_guia_madre_completada(contexto_aduana["numero_guia_despacho"])


@then("debe validar que agregar consolidado esta bloqueado")
def validar_agregar_consolidado_bloqueado(
    control_aduanero_page: ControlAduaneroPage,
    contexto_aduana: dict,
):
    control_aduanero_page.validar_agregar_consolidado_bloqueado(contexto_aduana["numero_guia_despacho"])


@when(parsers.parse('crea una guia madre de flujo completo con moneda "{moneda}"'))
def crear_guia_madre_flujo_completo(
    control_aduanero_page: ControlAduaneroPage,
    contexto_aduana: dict,
    moneda: str,
):
    pais = contexto_aduana.get("pais", "Guatemala")
    guia_madre = generar_guia_madre(moneda)
    contexto_aduana["guia_madre"] = guia_madre
    contexto_aduana["numero_guia_despacho"] = guia_madre.numero_guia
    allure.dynamic.title(f"Flujo completo Control Aduanero - {pais}")
    allure.dynamic.feature("Flujo completo")
    allure.dynamic.story("Login a despacho de cajas")
    allure.dynamic.suite("Control Aduanero FD")
    allure.dynamic.sub_suite("End to end")
    allure.dynamic.severity(allure.severity_level.BLOCKER)
    allure.dynamic.parameter("pais", pais)
    allure.dynamic.parameter("moneda", moneda)
    allure.dynamic.parameter("numero_guia", guia_madre.numero_guia)

    control_aduanero_page.abrir_formulario_guia_madre()
    control_aduanero_page.crear_guia_madre(guia_madre)


@then(parsers.parse('debe visualizar la guia madre creada en estado "{estado}"'))
def validar_estado_guia_madre_creada(
    control_aduanero_page: ControlAduaneroPage,
    contexto_aduana: dict,
    estado: str,
):
    guia_madre = contexto_aduana["guia_madre"]
    control_aduanero_page.validar_estado_guia_madre(guia_madre.numero_guia, estado)


@when("entrega a aduana la guia madre creada")
def entregar_guia_madre_creada_a_aduana(
    control_aduanero_page: ControlAduaneroPage,
    contexto_aduana: dict,
):
    guia_madre = contexto_aduana["guia_madre"]
    control_aduanero_page.entregar_guia_madre_a_aduana(guia_madre.numero_guia)


@when("abre el detalle de la guia madre creada")
def abrir_detalle_guia_madre_creada(
    control_aduanero_page: ControlAduaneroPage,
    contexto_aduana: dict,
):
    guia_madre = contexto_aduana["guia_madre"]
    contexto_aduana["numero_guia_consolidado"] = guia_madre.numero_guia
    contexto_aduana["numero_guia_despacho"] = guia_madre.numero_guia
    control_aduanero_page.abrir_detalle_guia_madre(guia_madre.numero_guia)


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


def generar_consolidados() -> list[Consolidado]:
    archivos_dir = Path(os.getenv("CONSOLIDADO_FILES_DIR", Path.home() / "Downloads"))
    descripcion = "Documento de prueba de automatizacion"
    datos = [
        ("Verde", "Archivo_de_prueba_con_una_hoja_verde.xlsx"),
        ("Rojo", "Archivo_de_prueba_con_una_hoja_rojo.xlsx"),
        ("Amarillo", "Archivo_de_prueba_con_una_hoja_amarillo.xlsx"),
    ]
    return [
        Consolidado(
            selectivo=selectivo,
            nombre=f"Prueba de automatizacion_{indice}",
            descripcion=descripcion,
            archivo=archivos_dir / archivo,
        )
        for indice, (selectivo, archivo) in enumerate(datos, start=1)
    ]

import re
from dataclasses import dataclass

import allure
from playwright.sync_api import Page, expect


@dataclass
class GuiaMadre:
    numero_guia: str
    numero_vuelo: str
    origen: str
    destino: str
    total_cajas: str
    total_guias_individuales: str
    peso_declarado: str
    valor_declarado: str
    moneda: str


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

    @allure.step("Validar mensaje de credenciales invalidas")
    def validar_credenciales_invalidas(self) -> None:
        mensaje_error = re.compile(
            "credenciales|incorrect|inv[aá]lid|usuario|contrase|correo|error",
            re.I,
        )
        posibles_mensajes = self.page.get_by_text(mensaje_error)
        expect(posibles_mensajes.first).to_be_visible(timeout=30000)
        expect(self.page.get_by_role("heading", name=re.compile("gu[ií]as madre", re.I))).not_to_be_visible()
        self._take_screenshot("credenciales_invalidas")

    @allure.step("Abrir formulario de guia madre")
    def abrir_formulario_guia_madre(self) -> None:
        self.page.get_by_role("button", name=re.compile("agregar gu[ií]a madre", re.I)).click(timeout=30000)
        expect(self.page.get_by_role("button", name=re.compile("crear gu[ií]a madre", re.I))).to_be_visible(
            timeout=30000
        )
        self._take_screenshot("formulario_guia_madre")

    @allure.step("Crear guia madre")
    def crear_guia_madre(self, guia_madre: GuiaMadre) -> None:
        self._llenar_campo("No. Guia", guia_madre.numero_guia)
        self._llenar_campo("Numero de vuelo", guia_madre.numero_vuelo)
        self._llenar_campo("Origen", guia_madre.origen)
        self._llenar_campo("Destino", guia_madre.destino)
        self._llenar_campo("Total cajas", guia_madre.total_cajas)
        self._llenar_campo("Total de guias individuales", guia_madre.total_guias_individuales)
        self._llenar_campo("Peso declarado", guia_madre.peso_declarado)
        self._llenar_campo("Valor declarado", guia_madre.valor_declarado)
        self._seleccionar_moneda(guia_madre.moneda)
        self._take_screenshot(f"datos_guia_madre_{guia_madre.moneda}")
        self.page.get_by_role("button", name=re.compile("crear gu[ií]a madre", re.I)).click()

    @allure.step("Intentar crear guia madre omitiendo campo obligatorio")
    def intentar_crear_guia_madre_sin_campo(self, guia_madre: GuiaMadre, campo_omitido: str) -> None:
        campos = {
            "No. Guia": guia_madre.numero_guia,
            "Numero de vuelo": guia_madre.numero_vuelo,
            "Origen": guia_madre.origen,
            "Destino": guia_madre.destino,
            "Total cajas": guia_madre.total_cajas,
            "Total de guias individuales": guia_madre.total_guias_individuales,
            "Peso declarado": guia_madre.peso_declarado,
            "Valor declarado": guia_madre.valor_declarado,
        }
        for nombre, valor in campos.items():
            if self._normalizar_texto(nombre) == self._normalizar_texto(campo_omitido):
                continue
            self._llenar_campo(nombre, valor)

        self._seleccionar_moneda(guia_madre.moneda)
        self._take_screenshot(f"guia_madre_sin_{self._normalizar_texto(campo_omitido)}")
        self.page.get_by_role("button", name=re.compile("crear gu[ií]a madre", re.I)).click()

    @allure.step("Validar guia madre creada")
    def validar_guia_madre_creada(self, numero_guia: str) -> None:
        mensaje_exito = self.page.get_by_text(
            re.compile(rf"manifiesto:\s*{re.escape(numero_guia)}.*creado con [eé]xito", re.I)
        )
        expect(mensaje_exito).to_be_visible(timeout=30000)
        self._take_screenshot("guia_madre_creada")
        self.page.get_by_role("button", name=re.compile("entendido", re.I)).click(timeout=30000)
        expect(self.page.get_by_role("heading", name=re.compile("gu[ií]as madre", re.I))).to_be_visible()
        expect(self.page.get_by_text(numero_guia, exact=True)).to_be_visible(timeout=30000)

    @allure.step("Validar campo obligatorio")
    def validar_campo_obligatorio(self, campo: str) -> None:
        campo_locator = self._obtener_campo(campo).first
        expect(campo_locator).to_be_visible(timeout=10000)
        valor_actual = campo_locator.input_value()
        assert self._valor_omitido(valor_actual), (
            f"El campo '{campo}' no quedo omitido durante la validacion. "
            f"Valor actual: '{valor_actual}'."
        )
        expect(self.page.get_by_text(re.compile("creado con [eé]xito", re.I))).not_to_be_visible()
        expect(self.page.get_by_role("button", name=re.compile("crear gu[ií]a madre", re.I))).to_be_visible()
        self._take_screenshot(f"campo_obligatorio_{self._normalizar_texto(campo)}")

    @allure.step("Entregar primera guia madre disponible a aduana")
    def entregar_primera_guia_madre_disponible(self) -> str:
        self.page.get_by_role("heading", name=re.compile("gu[ií]as madre", re.I)).wait_for(timeout=30000)
        filas = self.page.locator("tbody tr")
        total_filas = filas.count()
        if total_filas == 0:
            raise AssertionError("No hay guias madre disponibles en la tabla.")

        for indice in range(total_filas):
            fila = filas.nth(indice)
            boton = fila.get_by_role("button", name=re.compile("entregar a aduana", re.I))
            if boton.count() == 0:
                continue
            if boton.first.is_disabled():
                continue

            numero_guia = fila.locator("td").first.inner_text().strip()
            estado_previo = fila.get_by_text(re.compile("arribo al pa[ií]s", re.I))
            expect(estado_previo).to_be_visible(timeout=10000)
            self._take_screenshot(f"entrega_aduana_previo_{self._normalizar_texto(numero_guia)}")

            boton.first.click()
            self._confirmar_entrega_aduana()
            self._take_screenshot(f"entrega_aduana_realizada_{self._normalizar_texto(numero_guia)}")
            return numero_guia

        raise AssertionError("No se encontro una guia madre con boton 'Entregar a aduana' habilitado.")

    @allure.step("Validar estado de guia madre")
    def validar_estado_guia_madre(self, numero_guia: str, estado: str) -> None:
        fila = self.page.locator("tbody tr").filter(has_text=numero_guia).first
        expect(fila).to_be_visible(timeout=30000)
        expect(fila.get_by_text(re.compile(re.escape(estado), re.I))).to_be_visible(timeout=30000)
        self._take_screenshot(f"estado_{self._normalizar_texto(estado)}_{self._normalizar_texto(numero_guia)}")

    def _confirmar_entrega_aduana(self) -> None:
        boton_cambiar_estado = self.page.get_by_role("button", name=re.compile("cambiar estado", re.I))
        expect(boton_cambiar_estado).to_be_visible(timeout=30000)
        self._take_screenshot("modal_entrega_aduana")
        boton_cambiar_estado.click()

        boton_entendido = self.page.get_by_role("button", name=re.compile("entendido", re.I))
        expect(boton_entendido).to_be_visible(timeout=30000)
        self._take_screenshot("modal_entrega_aduana_exito")
        boton_entendido.click()
        self.page.wait_for_load_state("networkidle")

    def _llenar_campo(self, nombre: str, valor: str) -> None:
        self._obtener_campo(nombre).first.fill(valor)

    def _obtener_campo(self, nombre: str):
        patron = self._patron_campo(nombre)
        campo = self.page.get_by_label(patron)
        if campo.count() == 0:
            campo = self.page.get_by_role("textbox", name=patron)
        if campo.count() == 0:
            campo = self.page.get_by_placeholder(patron)
        return campo

    def _seleccionar_moneda(self, moneda: str) -> None:
        select_moneda = self.page.get_by_label(re.compile("moneda de valor declarado", re.I))
        if select_moneda.count() > 0:
            selected = select_moneda.first.evaluate(
                """
                (select, currency) => {
                    const option = [...select.options].find((item) =>
                        item.textContent.toLowerCase().includes(currency.toLowerCase()) ||
                        item.value.toLowerCase().includes(currency.toLowerCase())
                    );
                    if (!option) {
                        return false;
                    }
                    select.value = option.value;
                    select.dispatchEvent(new Event('input', { bubbles: true }));
                    select.dispatchEvent(new Event('change', { bubbles: true }));
                    return true;
                }
                """,
                moneda,
            )
            if selected:
                return

        self.page.get_by_text(re.compile("moneda de valor declarado", re.I)).first.click(timeout=10000)
        self.page.get_by_text(re.compile(re.escape(moneda), re.I)).click(timeout=10000)

    def _patron_texto(self, texto: str) -> re.Pattern:
        reemplazos = {
            "a": "[aá]",
            "e": "[eé]",
            "i": "[ií]",
            "o": "[oó]",
            "u": "[uú]",
        }
        patron = re.escape(texto.lower())
        for letra, expresion in reemplazos.items():
            patron = patron.replace(letra, expresion)
        patron = patron.replace(r"\ ", r"\s+")
        return re.compile(patron, re.I)

    def _patron_campo(self, nombre: str) -> re.Pattern:
        patrones = {
            "No. Guia": r"^No\.?\s*Gu[ií]a\s*\*?$",
            "Numero de vuelo": r"^N[uú]mero\s+de\s+vuelo\s*\*?$",
            "Origen": r"^Origen\s*\*?$",
            "Destino": r"^Destino\s*\*?$",
            "Total cajas": r"^Total\s+Cajas\s*\*?$",
            "Total de guias individuales": r"^Total\s+de\s+gu[ií]as\s+individuales\s*\*?$",
            "Peso declarado": r"^Peso\s+declarado(?:\s+en\s+KG)?\s*\*?$",
            "Valor declarado": r"^Valor\s+declarado\s*\*?$",
        }
        return re.compile(patrones.get(nombre, self._patron_texto(nombre).pattern), re.I)

    def _normalizar_texto(self, texto: str) -> str:
        return re.sub(r"[^a-z0-9]+", "_", texto.lower()).strip("_")

    def _valor_omitido(self, valor: str) -> bool:
        valor_normalizado = valor.strip()
        if valor_normalizado == "":
            return True
        try:
            return float(valor_normalizado) == 0
        except ValueError:
            return False

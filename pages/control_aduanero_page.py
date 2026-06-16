import re
from dataclasses import dataclass
from pathlib import Path

import allure
from playwright.sync_api import Page, TimeoutError as PlaywrightTimeoutError, expect


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


@dataclass
class Consolidado:
    selectivo: str
    nombre: str
    descripcion: str
    archivo: Path


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
        self._click_boton_crear_guia_madre()

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
        self._click_boton_crear_guia_madre()

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
        fila = self._buscar_guia_madre_en_listado(numero_guia)
        expect(fila).to_be_visible(timeout=30000)
        expect(fila.get_by_text(re.compile(re.escape(estado), re.I))).to_be_visible(timeout=30000)
        self._take_screenshot(f"estado_{self._normalizar_texto(estado)}_{self._normalizar_texto(numero_guia)}")

    @allure.step("Entregar guia madre creada a aduana")
    def entregar_guia_madre_a_aduana(self, numero_guia: str) -> None:
        fila = self._buscar_guia_madre_en_listado(numero_guia)
        expect(fila.get_by_text(re.compile("arribo al pa[ií]s", re.I))).to_be_visible(timeout=30000)
        boton = fila.get_by_role("button", name=re.compile("entregar a aduana", re.I)).first
        expect(boton).to_be_enabled(timeout=30000)
        self._take_screenshot(f"entrega_aduana_previo_{self._normalizar_texto(numero_guia)}")
        boton.click()
        self._confirmar_entrega_aduana()
        self._take_screenshot(f"entrega_aduana_realizada_{self._normalizar_texto(numero_guia)}")

    @allure.step("Abrir detalle de guia madre")
    def abrir_detalle_guia_madre(self, numero_guia: str) -> None:
        fila = self._buscar_guia_madre_en_listado(numero_guia)
        boton_detalle = fila.locator("button").first
        expect(boton_detalle).to_be_visible(timeout=30000)
        self._take_screenshot(f"detalle_previo_{self._normalizar_texto(numero_guia)}")
        boton_detalle.click()
        expect(self.page.get_by_role("button", name=re.compile("agregar consolidado", re.I))).to_be_visible(
            timeout=30000
        )
        self._take_screenshot(f"detalle_guia_{self._normalizar_texto(numero_guia)}")

    @allure.step("Abrir detalle de guia madre en arribo a aduana")
    def abrir_detalle_primera_guia_en_arribo_aduana(self) -> str:
        return self._abrir_detalle_primera_guia_por_estado("Arribo a aduana")

    @allure.step("Abrir detalle de guia madre en carga de selectivos")
    def abrir_detalle_primera_guia_en_carga_selectivos(self) -> str:
        return self._abrir_detalle_primera_guia_por_estado("Carga de selectivos")

    def _abrir_detalle_primera_guia_por_estado(self, estado: str) -> str:
        self.page.get_by_role("heading", name=re.compile("gu[ií]as madre", re.I)).wait_for(timeout=30000)
        patron_estado = re.compile(re.escape(estado), re.I)
        paginas_revisadas = 0
        while paginas_revisadas < 20:
            filas = self.page.locator("tbody tr")
            total_filas = filas.count()
            if total_filas == 0:
                raise AssertionError("No hay guias madre disponibles en la tabla.")

            for indice in range(total_filas):
                fila = filas.nth(indice)
                if fila.get_by_text(patron_estado).count() == 0:
                    continue

                numero_guia = fila.locator("td").first.inner_text().strip()
                boton_detalle = fila.locator("td").nth(9).locator("button").first
                if boton_detalle.count() == 0:
                    boton_detalle = fila.locator("button").first
                expect(boton_detalle).to_be_visible(timeout=10000)
                self._take_screenshot(f"detalle_previo_{self._normalizar_texto(numero_guia)}")
                boton_detalle.click()
                expect(self.page.get_by_role("button", name=re.compile("agregar consolidado", re.I))).to_be_visible(
                    timeout=30000
                )
                self._take_screenshot(f"detalle_guia_{self._normalizar_texto(numero_guia)}")
                return numero_guia

            paginas_revisadas += 1
            if not self._ir_siguiente_pagina_tabla():
                break

        raise AssertionError(f"No se encontro una guia madre en estado '{estado}'.")

    @allure.step("Agregar consolidado")
    def agregar_consolidado(self, consolidado: Consolidado) -> None:
        if not consolidado.archivo.exists():
            raise AssertionError(f"No existe el archivo de consolidado: {consolidado.archivo}")

        self.page.get_by_role("button", name=re.compile("agregar consolidado", re.I)).click(timeout=30000)
        expect(self.page.get_by_role("button", name=re.compile("cargar consolidado", re.I))).to_be_visible(
            timeout=30000
        )
        self._seleccionar_selectivo(consolidado.selectivo)
        self._llenar_campo("Nombre consolidado", consolidado.nombre)
        self._llenar_campo("Descripcion", consolidado.descripcion)
        self._cargar_archivo_consolidado(consolidado.archivo)
        self._take_screenshot(f"consolidado_{self._normalizar_texto(consolidado.selectivo)}")
        self._click_boton_cargar_consolidado()
        self._confirmar_modal_entendido("consolidado_cargado")

    @allure.step("Validar consolidado cargado")
    def validar_consolidado_cargado(self, consolidado: Consolidado) -> None:
        expect(self.page.get_by_text(re.compile(re.escape(consolidado.nombre), re.I))).to_be_visible(timeout=30000)
        self._take_screenshot(f"validar_consolidado_{self._normalizar_texto(consolidado.selectivo)}")

    @allure.step("Abrir detalle del primer consolidado disponible")
    def abrir_detalle_primer_consolidado_disponible(self) -> str:
        filas = self.page.locator("tbody tr")
        expect(filas.first).to_be_visible(timeout=30000)
        total_filas = filas.count()
        for indice in range(total_filas):
            fila = filas.nth(indice)
            boton_detalle = fila.locator("button").first
            if boton_detalle.count() == 0:
                continue

            nombre_consolidado = fila.locator("td").first.inner_text().strip()
            self._take_screenshot(f"detalle_consolidado_previo_{self._normalizar_texto(nombre_consolidado)}")
            boton_detalle.click()
            self._esperar_carga_visual()
            boton_despachar = self.page.get_by_role("button", name=re.compile("^despachar$", re.I)).first
            expect(boton_despachar).to_be_visible(timeout=30000)
            if boton_despachar.is_disabled():
                self._take_screenshot(f"consolidado_ya_despachado_{self._normalizar_texto(nombre_consolidado)}")
                self._regresar_a_consolidados()
                filas = self.page.locator("tbody tr")
                continue

            self._take_screenshot(f"detalle_consolidado_{self._normalizar_texto(nombre_consolidado)}")
            return nombre_consolidado

        raise AssertionError("No se encontro un consolidado con boton 'Despachar' habilitado.")

    @allure.step("Despachar cajas")
    def despachar_cajas(self) -> None:
        self._despachar_consolidado_actual()
        while True:
            self._regresar_a_consolidados()
            try:
                self.abrir_detalle_primer_consolidado_disponible()
            except AssertionError:
                break
            self._despachar_consolidado_actual()

    def _despachar_consolidado_actual(self) -> None:
        self._esperar_carga_visual()
        boton_despachar = self.page.get_by_role("button", name=re.compile("^despachar$", re.I)).first
        expect(boton_despachar).to_be_enabled(timeout=30000)
        boton_despachar.click(timeout=30000)
        boton_despachar_cajas = self.page.get_by_role("button", name=re.compile("despachar cajas", re.I))
        expect(boton_despachar_cajas).to_be_visible(timeout=30000)
        self._take_screenshot("modal_despachar_cajas")
        boton_despachar_cajas.click()

        boton_confirmar = self.page.get_by_role("button", name=re.compile("s[ií],?\\s*confirmar", re.I))
        expect(boton_confirmar).to_be_visible(timeout=30000)
        self._take_screenshot("modal_confirmar_despacho_cajas")
        boton_confirmar.click()

        expect(self.page.get_by_text(re.compile("operaci[oó]n completad[ao] con [eé]xito", re.I))).to_be_visible(
            timeout=30000
        )
        self._confirmar_modal_entendido("despacho_cajas_exitoso")
        self._validar_boton_despachar_bloqueado()

    @allure.step("Validar guia madre completada")
    def validar_guia_madre_completada(self, numero_guia: str) -> None:
        fila = self._buscar_guia_madre_en_listado(numero_guia)
        expect(fila).to_be_visible(timeout=30000)
        expect(fila.get_by_text(re.compile("completado", re.I))).to_be_visible(timeout=30000)
        self._take_screenshot(f"guia_madre_completada_{self._normalizar_texto(numero_guia)}")

    @allure.step("Validar agregar consolidado bloqueado")
    def validar_agregar_consolidado_bloqueado(self, numero_guia: str) -> None:
        fila = self._buscar_guia_madre_en_listado(numero_guia)
        expect(fila).to_be_visible(timeout=30000)
        boton_detalle = fila.locator("button").first
        boton_detalle.click()
        boton_agregar = self.page.get_by_role("button", name=re.compile("agregar consolidado", re.I)).first
        expect(boton_agregar).to_be_visible(timeout=30000)
        expect(boton_agregar).to_be_disabled(timeout=30000)
        self._take_screenshot(f"agregar_consolidado_bloqueado_{self._normalizar_texto(numero_guia)}")

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

    def _click_boton_crear_guia_madre(self) -> None:
        boton = self.page.get_by_role("button", name=re.compile("crear gu[ií]a madre", re.I)).first
        try:
            boton.scroll_into_view_if_needed(timeout=10000)
            boton.click(timeout=30000)
        except PlaywrightTimeoutError:
            boton.click(timeout=30000, force=True)

    def _click_boton_cargar_consolidado(self) -> None:
        boton = self.page.get_by_role("button", name=re.compile("cargar consolidado", re.I)).first
        try:
            boton.scroll_into_view_if_needed(timeout=10000)
            boton.click(timeout=30000)
        except PlaywrightTimeoutError:
            boton.click(timeout=30000, force=True)

    def _confirmar_modal_entendido(self, nombre_captura: str) -> None:
        boton_entendido = self.page.get_by_role("button", name=re.compile("entendido", re.I))
        expect(boton_entendido).to_be_visible(timeout=30000)
        self._take_screenshot(nombre_captura)
        boton_entendido.click()
        self.page.wait_for_load_state("networkidle")

    def _validar_boton_despachar_bloqueado(self) -> None:
        boton_despachar = self.page.get_by_role("button", name=re.compile("^despachar$", re.I)).first
        expect(boton_despachar).to_be_visible(timeout=30000)
        expect(boton_despachar).to_be_disabled(timeout=30000)
        self._take_screenshot("boton_despachar_bloqueado")

    def _regresar_hasta_guias_madre(self) -> None:
        for _ in range(3):
            if self.page.get_by_role("heading", name=re.compile("gu[ií]as madre", re.I)).count() > 0:
                return
            boton_regresar = self.page.get_by_role("button", name=re.compile("regresar", re.I)).first
            if boton_regresar.count() == 0:
                self.page.go_back(wait_until="networkidle")
            else:
                boton_regresar.click()
                self.page.wait_for_load_state("networkidle")

        expect(self.page.get_by_role("heading", name=re.compile("gu[ií]as madre", re.I))).to_be_visible(timeout=30000)

    def _buscar_guia_madre_en_listado(self, numero_guia: str):
        self._regresar_hasta_guias_madre()
        campo_buscar = self.page.get_by_role("textbox", name=re.compile("buscar", re.I)).first
        expect(campo_buscar).to_be_visible(timeout=30000)
        campo_buscar.fill(numero_guia)
        boton_filtrar = self.page.get_by_role("button", name=re.compile("filtrar", re.I)).first
        if boton_filtrar.count() > 0 and boton_filtrar.is_enabled():
            boton_filtrar.click()
            self.page.wait_for_load_state("networkidle")
        fila = self.page.locator("tbody tr").filter(has_text=numero_guia).first
        expect(fila).to_be_visible(timeout=30000)
        return fila

    def _regresar_a_consolidados(self) -> None:
        boton_regresar = self.page.get_by_role("button", name=re.compile("regresar", re.I)).first
        if boton_regresar.count() == 0:
            self.page.go_back(wait_until="networkidle")
        else:
            boton_regresar.click()
            self.page.wait_for_load_state("networkidle")
        self._esperar_carga_visual()
        expect(self.page.get_by_role("button", name=re.compile("agregar consolidado", re.I))).to_be_visible(
            timeout=30000
        )

    def _ir_siguiente_pagina_tabla(self) -> bool:
        primera_fila = self.page.locator("tbody tr").first
        texto_primera_fila = primera_fila.inner_text().strip() if primera_fila.count() > 0 else ""
        candidatos = [
            self.page.get_by_role("button", name=re.compile("siguiente|next", re.I)).last,
            self.page.locator("button[aria-label*='iguiente' i], button[aria-label*='next' i]").last,
            self.page.locator("button").filter(has_text=re.compile(r"^>$|»", re.I)).last,
        ]

        for boton in candidatos:
            if boton.count() == 0 or not boton.is_visible() or boton.is_disabled():
                continue
            boton.click()
            self.page.wait_for_load_state("networkidle")
            try:
                expect(primera_fila).not_to_have_text(texto_primera_fila, timeout=10000)
            except AssertionError:
                pass
            self._take_screenshot("siguiente_pagina_tabla")
            return True

        return False

    def _esperar_carga_visual(self) -> None:
        overlay = self.page.locator(".fullscreen-overlay")
        if overlay.count() > 0:
            try:
                expect(overlay).to_be_hidden(timeout=30000)
            except AssertionError:
                pass
        self.page.wait_for_load_state("networkidle")

    def _seleccionar_selectivo(self, selectivo: str) -> None:
        patron_label = re.compile("selectivo.*cargar|selectivo.*carga", re.I)
        combo = self.page.get_by_label(patron_label)
        if combo.count() == 0:
            combo = self.page.get_by_role("combobox", name=patron_label)
        if combo.count() > 0:
            try:
                selected = combo.first.evaluate(
                    """
                    (select, optionText) => {
                        if (!select.options) {
                            return false;
                        }
                        const option = [...select.options].find((item) =>
                            item.textContent.toLowerCase().includes(optionText.toLowerCase()) ||
                            item.value.toLowerCase().includes(optionText.toLowerCase())
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
                    selectivo,
                )
                if selected:
                    return
            except Exception:
                combo.first.click()

        self.page.get_by_text(re.compile("selectivo.*cargar|selectivo.*carga", re.I)).first.click(timeout=10000)
        self.page.get_by_text(re.compile(selectivo, re.I)).click(timeout=10000)

    def _cargar_archivo_consolidado(self, archivo: Path) -> None:
        file_input = self.page.locator("input[type='file']").first
        if file_input.count() == 0:
            self.page.get_by_text(re.compile("arrastra tu documento|arrastre tu documento|documento hasta aqu[ií]", re.I)).click(
                timeout=10000
            )
            file_input = self.page.locator("input[type='file']").first
        file_input.set_input_files(str(archivo))

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
            "Nombre consolidado": r"^Nombre\s+consolidado\s*\*?$",
            "Descripcion": r"^Descripci[oó]n(?:\s+consolidado)?\s*\*?$",
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

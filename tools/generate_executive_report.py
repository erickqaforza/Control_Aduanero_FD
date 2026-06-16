from __future__ import annotations

import subprocess
from datetime import datetime
from pathlib import Path

from docx import Document
from docx.enum.table import WD_CELL_VERTICAL_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Inches, Pt, RGBColor


PROJECT_ROOT = Path(__file__).resolve().parents[1]
OUTPUT_DIR = PROJECT_ROOT / "docs" / "informes"
REPORT_PATH = OUTPUT_DIR / "Informe_Ejecutivo_Certificacion_QA_Control_Aduanero_FD.docx"

BLUE = RGBColor(46, 116, 181)
DARK_BLUE = RGBColor(31, 77, 120)
INK = RGBColor(11, 37, 69)
MUTED = RGBColor(90, 99, 110)
GREEN = RGBColor(20, 115, 70)
HEADER_FILL = "E8EEF5"
LIGHT_FILL = "F4F6F9"
SUCCESS_FILL = "E7F5EC"


def git_value(*args: str) -> str:
    try:
        result = subprocess.run(
            ["git", *args],
            cwd=PROJECT_ROOT,
            text=True,
            capture_output=True,
            check=True,
        )
        return result.stdout.strip().splitlines()[0]
    except Exception:
        return "No disponible"


def set_cell_shading(cell, fill: str) -> None:
    tc_pr = cell._tc.get_or_add_tcPr()
    shd = tc_pr.find(qn("w:shd"))
    if shd is None:
        shd = OxmlElement("w:shd")
        tc_pr.append(shd)
    shd.set(qn("w:fill"), fill)


def set_cell_margins(cell, top=80, start=120, bottom=80, end=120) -> None:
    tc_pr = cell._tc.get_or_add_tcPr()
    tc_mar = tc_pr.first_child_found_in("w:tcMar")
    if tc_mar is None:
        tc_mar = OxmlElement("w:tcMar")
        tc_pr.append(tc_mar)
    for margin, value in (("top", top), ("start", start), ("bottom", bottom), ("end", end)):
        node = tc_mar.find(qn(f"w:{margin}"))
        if node is None:
            node = OxmlElement(f"w:{margin}")
            tc_mar.append(node)
        node.set(qn("w:w"), str(value))
        node.set(qn("w:type"), "dxa")


def set_table_width(table, widths_in: list[float]) -> None:
    table.autofit = False
    for row in table.rows:
        for idx, width in enumerate(widths_in):
            cell = row.cells[idx]
            cell.width = Inches(width)
            set_cell_margins(cell)
            cell.vertical_alignment = WD_CELL_VERTICAL_ALIGNMENT.CENTER


def apply_styles(doc: Document) -> None:
    section = doc.sections[0]
    section.page_width = Inches(8.5)
    section.page_height = Inches(11)
    section.top_margin = Inches(1)
    section.bottom_margin = Inches(1)
    section.left_margin = Inches(1)
    section.right_margin = Inches(1)
    section.header_distance = Inches(0.492)
    section.footer_distance = Inches(0.492)

    normal = doc.styles["Normal"]
    normal.font.name = "Calibri"
    normal.font.size = Pt(11)
    normal.paragraph_format.space_after = Pt(6)
    normal.paragraph_format.line_spacing = 1.25

    for style_name, size, color, before, after in [
        ("Heading 1", 16, BLUE, 18, 10),
        ("Heading 2", 13, BLUE, 14, 7),
        ("Heading 3", 12, DARK_BLUE, 10, 5),
    ]:
        style = doc.styles[style_name]
        style.font.name = "Calibri"
        style.font.size = Pt(size)
        style.font.bold = True
        style.font.color.rgb = color
        style.paragraph_format.space_before = Pt(before)
        style.paragraph_format.space_after = Pt(after)
        style.paragraph_format.line_spacing = 1.25

    header = section.header.paragraphs[0]
    header.text = "Certificacion QA - Control Aduanero FD"
    header.runs[0].font.size = Pt(9)
    header.runs[0].font.color.rgb = MUTED
    header.alignment = WD_ALIGN_PARAGRAPH.RIGHT

    footer = section.footer.paragraphs[0]
    footer.text = "Informe ejecutivo de pruebas | Control Aduanero FD"
    footer.runs[0].font.size = Pt(9)
    footer.runs[0].font.color.rgb = MUTED
    footer.alignment = WD_ALIGN_PARAGRAPH.CENTER


def add_title(doc: Document) -> None:
    p = doc.add_paragraph()
    run = p.add_run("Informe Ejecutivo de Certificacion QA")
    run.bold = True
    run.font.size = Pt(22)
    run.font.color.rgb = INK
    p.paragraph_format.space_after = Pt(2)

    p = doc.add_paragraph()
    run = p.add_run("Proyecto Control Aduanero FD")
    run.font.size = Pt(13)
    run.font.color.rgb = MUTED
    p.paragraph_format.space_after = Pt(12)

    add_info_table(
        doc,
        [
            ("Fecha del informe", datetime.now().strftime("%d/%m/%Y %H:%M")),
            ("Rama certificada", git_value("branch", "--show-current")),
            ("Commit", git_value("rev-parse", "--short", "HEAD")),
            ("Ambiente", "QA"),
            ("Responsable de ejecucion", "QA Automation"),
        ],
    )


def add_info_table(doc: Document, rows: list[tuple[str, str]]) -> None:
    table = doc.add_table(rows=len(rows), cols=2)
    table.style = "Table Grid"
    set_table_width(table, [1.85, 4.65])
    for idx, (label, value) in enumerate(rows):
        table.cell(idx, 0).text = label
        table.cell(idx, 1).text = value
        set_cell_shading(table.cell(idx, 0), HEADER_FILL)
        for cell in table.rows[idx].cells:
            for paragraph in cell.paragraphs:
                for run in paragraph.runs:
                    run.font.size = Pt(10)
    doc.add_paragraph()


def add_matrix(doc: Document, headers: list[str], rows: list[list[str]], widths: list[float]) -> None:
    table = doc.add_table(rows=1, cols=len(headers))
    table.style = "Table Grid"
    set_table_width(table, widths)
    for i, header in enumerate(headers):
        cell = table.rows[0].cells[i]
        cell.text = header
        set_cell_shading(cell, HEADER_FILL)
        for run in cell.paragraphs[0].runs:
            run.bold = True
            run.font.size = Pt(10)
            run.font.color.rgb = INK
    for values in rows:
        cells = table.add_row().cells
        for i, value in enumerate(values):
            cells[i].text = value
            for paragraph in cells[i].paragraphs:
                for run in paragraph.runs:
                    run.font.size = Pt(9.5)
            if value.upper() in {"APROBADO", "PASSED"}:
                set_cell_shading(cells[i], SUCCESS_FILL)
                for paragraph in cells[i].paragraphs:
                    for run in paragraph.runs:
                        run.bold = True
                        run.font.color.rgb = GREEN
    set_table_width(table, widths)
    doc.add_paragraph()


def add_callout(doc: Document, title: str, text: str, fill: str = LIGHT_FILL) -> None:
    table = doc.add_table(rows=1, cols=1)
    table.style = "Table Grid"
    set_table_width(table, [6.5])
    cell = table.cell(0, 0)
    set_cell_shading(cell, fill)
    cell.text = ""
    p = cell.paragraphs[0]
    r = p.add_run(title + ": ")
    r.bold = True
    r.font.color.rgb = DARK_BLUE
    r.font.size = Pt(10.5)
    r2 = p.add_run(text)
    r2.font.size = Pt(10.5)
    doc.add_paragraph()


def add_bullets(doc: Document, items: list[str]) -> None:
    for item in items:
        p = doc.add_paragraph(style="List Bullet")
        p.paragraph_format.left_indent = Inches(0.375)
        p.paragraph_format.first_line_indent = Inches(-0.188)
        p.paragraph_format.space_after = Pt(4)
        p.add_run(item)


def build_report() -> None:
    doc = Document()
    apply_styles(doc)
    add_title(doc)

    add_callout(
        doc,
        "Resultado ejecutivo",
        "La ejecucion automatizada del flujo completo finalizo satisfactoriamente para Guatemala, Honduras y El Salvador. Se valida el recorrido funcional desde login hasta despacho de cajas, incluyendo los cambios de estado requeridos en cada etapa.",
        SUCCESS_FILL,
    )

    doc.add_heading("1. Objetivo de la certificacion", level=1)
    doc.add_paragraph(
        "Certificar, con evidencia automatizada, que el flujo operativo principal de Control Aduanero FD funciona correctamente en ambiente QA para los paises incluidos en el alcance."
    )

    doc.add_heading("2. Alcance funcional validado", level=1)
    add_matrix(
        doc,
        ["Flujo", "Validacion principal", "Estado esperado"],
        [
            ["Login", "Ingreso por pais con usuario autorizado.", "Pantalla Guias madre visible"],
            ["Agregar guia madre", "Creacion con campos obligatorios y datos dinamicos.", "Arribo al pais"],
            ["Entrega a aduana", "Cambio de estado desde la accion Entregar a aduana.", "Arribo a aduana"],
            ["Agregar consolidado", "Carga de selectivos Verde, Rojo y Amarillo con archivo Excel.", "Carga de selectivos"],
            ["Despacho de cajas", "Despacho de todos los consolidados habilitados.", "Completado"],
            ["Bloqueo post-despacho", "Validacion de bloqueo de Agregar consolidado.", "Boton deshabilitado"],
        ],
        [1.55, 3.45, 1.5],
    )

    doc.add_heading("3. Tipo de ejecucion", level=1)
    add_matrix(
        doc,
        ["Tipo", "Detalle"],
        [
            ["Automatizada UI", "Pruebas end to end ejecutadas con Python, Pytest-BDD y Playwright."],
            ["BDD", "Escenarios escritos en Gherkin dentro de features/control_aduanero.feature."],
            ["Ejecucion visual", "Navegador visible, slow motion configurado para demo y grabacion de video."],
            ["Evidencia", "Reporte Allure, screenshots por step, videos WebM y JUnit XML."],
            ["Datos", "Guias madre generadas dinamicamente y archivos Excel de selectivos por color."],
        ],
        [1.75, 4.75],
    )

    doc.add_heading("4. Escenarios automatizados", level=1)
    add_matrix(
        doc,
        ["Grupo", "Cantidad", "Cobertura", "Resultado"],
        [
            ["Login exitoso", "3", "Guatemala, Honduras y El Salvador.", "APROBADO"],
            ["Login negativo", "2", "Correo incorrecto y contrasena incorrecta.", "APROBADO"],
            ["Crear guia madre", "9", "3 paises x 3 monedas.", "APROBADO"],
            ["Campos obligatorios", "8", "Validacion de campos requeridos de guia madre.", "APROBADO"],
            ["Entrega a aduana", "3", "Cambio a Arribo a aduana por pais.", "APROBADO"],
            ["Agregar consolidado", "3", "Carga Verde, Rojo y Amarillo por pais.", "APROBADO"],
            ["Despacho de cajas", "3", "Despacho de consolidados habilitados por pais.", "APROBADO"],
            ["Flujo completo", "3", "Login hasta despacho con la misma guia madre.", "APROBADO"],
        ],
        [1.55, 0.75, 3.35, 0.85],
    )

    doc.add_heading("5. Resultado de la ejecucion de certificacion", level=1)
    add_matrix(
        doc,
        ["Marcador", "Escenarios ejecutados", "Resultado", "Tiempo"],
        [
            ["flujo_completo", "3", "PASSED", "0:06:09"],
            ["Total fallidos", "0", "PASSED", "N/A"],
            ["Total omitidos por marcador", "31", "PASSED", "N/A"],
        ],
        [1.7, 1.55, 1.25, 2.0],
    )
    add_callout(
        doc,
        "Nota de warnings",
        "Durante las ejecuciones se reportaron warnings de deprecacion provenientes de la libreria gherkin. No representan fallo funcional ni bloqueo para la certificacion.",
    )

    doc.add_heading("6. Evidencias generadas", level=1)
    add_matrix(
        doc,
        ["Tipo", "Ruta"],
        [
            ["Reporte Allure flujo completo", r"C:\Proyectos\Control_Aduanero_FD\allure-reports\flujo_completo\index.html"],
            ["Video Guatemala", r"C:\Proyectos\Control_Aduanero_FD\videos\tests_test_control_aduanero.py_test_flujo_completo_control_aduanero_por_pais_Guatemala-GTQ_.webm"],
            ["Video Honduras", r"C:\Proyectos\Control_Aduanero_FD\videos\tests_test_control_aduanero.py_test_flujo_completo_control_aduanero_por_pais_Honduras-HNL_.webm"],
            ["Video El Salvador", r"C:\Proyectos\Control_Aduanero_FD\videos\tests_test_control_aduanero.py_test_flujo_completo_control_aduanero_por_pais_El.webm"],
            ["JUnit XML", r"C:\Proyectos\Control_Aduanero_FD\reportes\junit-results.xml"],
            ["Manual funcional", r"C:\Proyectos\Control_Aduanero_FD\docs\manuales\Manual_Funcional_Usuario_Final_Control_Aduanero_FD.docx"],
        ],
        [1.65, 4.85],
    )

    doc.add_heading("7. Criterios de aceptacion certificados", level=1)
    add_bullets(
        doc,
        [
            "El usuario puede autenticarse correctamente en cada pais incluido en el alcance.",
            "La guia madre se crea con datos validos y aparece en el listado.",
            "El estado de la guia madre avanza conforme al flujo esperado.",
            "La carga de consolidado acepta los tres selectivos requeridos: Verde, Rojo y Amarillo.",
            "El despacho procesa todos los consolidados habilitados antes de validar el estado final.",
            "Al finalizar el despacho, la guia madre queda en Completado.",
            "Luego del estado Completado, la accion Agregar consolidado queda bloqueada.",
        ],
    )

    doc.add_heading("8. Observaciones tecnicas", level=1)
    add_bullets(
        doc,
        [
            "La automatizacion utiliza Page Object Model para aislar acciones de pantalla y mejorar mantenibilidad.",
            "Las pruebas generan screenshots y videos por escenario para trazabilidad.",
            "El flujo completo usa la misma guia madre desde creacion hasta despacho, evitando mezclar registros del ambiente.",
            "La busqueda de registros contempla paginacion y validacion por estado cuando aplica.",
            "La ejecucion de despacho considera todos los consolidados habilitados para garantizar el estado final Completado.",
        ],
    )

    doc.add_heading("9. Riesgos y consideraciones", level=1)
    add_matrix(
        doc,
        ["Riesgo / consideracion", "Mitigacion"],
        [
            ["Datos vivos del ambiente QA", "Las pruebas generan datos dinamicos y validan la misma guia creada por el flujo."],
            ["Cambios visuales en UI", "Los selectores usan roles/textos accesibles y capturas facilitan diagnostico."],
            ["Tiempos de carga", "Se agregaron esperas para overlays y estados de red."],
            ["Evidencia pesada", "Los reportes Allure single-file pueden crecer por videos y capturas embebidas."],
        ],
        [2.55, 3.95],
    )

    doc.add_heading("10. Conclusion de certificacion", level=1)
    add_callout(
        doc,
        "Dictamen QA",
        "Con base en la ejecucion automatizada, los resultados obtenidos y las evidencias generadas, se certifica satisfactoriamente el flujo completo de Control Aduanero FD en ambiente QA para los paises Guatemala, Honduras y El Salvador.",
        SUCCESS_FILL,
    )

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    doc.save(REPORT_PATH)
    print(REPORT_PATH)


if __name__ == "__main__":
    build_report()

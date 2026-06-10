# Control_Aduanero_FD

Framework de automatizacion QA para el proyecto Control Aduanero FD usando Python, Pytest y Playwright.

## Stack

- Python 3.12+
- Pytest
- Pytest BDD
- Playwright
- Allure Pytest
- python-dotenv

## Estructura

```text
Control_Aduanero_FD/
├── .github/workflows/       # Ejecucion en GitHub Actions
├── data/                    # Datos de prueba versionables
├── docs/                    # Documentacion tecnica y funcional
├── features/                # Escenarios BDD en Gherkin
├── pages/                   # Page Object Model
├── reporting/               # Utilidades de reporteria
├── tests/                   # Pruebas y step definitions
├── utils/                   # Helpers compartidos
├── .env.example             # Variables de entorno de ejemplo
├── .gitignore
├── pytest.ini
└── requirements.txt
```

## Instalacion local

```powershell
python -m venv .venv
.\.venv\Scripts\activate
python -m pip install --upgrade pip
pip install -r requirements.txt
playwright install
```

Copia `.env.example` como `.env` y ajusta las variables del ambiente.

## Ejecucion

Ejecutar todas las pruebas:

```powershell
.\.venv\Scripts\python.exe -m pytest -s
```

Ejecutar pruebas smoke:

```powershell
.\.venv\Scripts\python.exe -m pytest -m smoke -s
```

Ejecutar login y generar reporte Allure:

```powershell
.\run_login_report.ps1
```

Ejecutar login, generar reporte y abrirlo:

```powershell
.\run_login_report.ps1 -OpenReport
```

Ejecutar creación de guía madre y generar reporte:

```powershell
.\run_login_report.ps1 -Marker guia_madre
```

El reporte HTML se genera en:

```text
allure-reports/<marker>/
```

El script genera el reporte en modo `single-file`, por lo que puede abrirse directamente desde:

```text
allure-reports/login/index.html
```

## Evidencias en video

Cada escenario graba un video `.webm` cuando `RECORD_VIDEO=true` en `.env`.

```env
RECORD_VIDEO=true
VIDEO_DIR=videos
```

Los videos se guardan localmente en:

```text
videos/
```

Tambien se adjuntan al reporte Allure como evidencia del flujo ejecutado.

## Convenciones

- Los localizadores y acciones de pantalla viven en `pages/`.
- Los escenarios BDD viven en `features/`.
- Los step definitions y pruebas viven en `tests/`.
- Las credenciales y URLs se leen desde `.env`, nunca se suben al repositorio.

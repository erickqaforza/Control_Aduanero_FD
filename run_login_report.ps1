param(
    [string]$Marker = "login",
    [switch]$OpenReport
)

$ErrorActionPreference = "Stop"

$ProjectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$PythonExe = Join-Path $ProjectRoot ".venv\Scripts\python.exe"
$AllureResults = Join-Path $ProjectRoot "allure-results"
$AllureReport = Join-Path $ProjectRoot "allure-reports\login"

function Resolve-AllureCommand {
    $localAllure = Get-ChildItem -Path (Join-Path $ProjectRoot "tools") -Filter "allure.bat" -Recurse -ErrorAction SilentlyContinue |
        Where-Object { $_.FullName -match "allure-[^\\]+\\bin\\allure\.bat$" } |
        Select-Object -First 1

    if ($localAllure) {
        return $localAllure.FullName
    }

    $pathAllure = Get-Command "allure" -ErrorAction SilentlyContinue
    if ($pathAllure) {
        return $pathAllure.Source
    }

    return $null
}

if (-not (Test-Path $PythonExe)) {
    throw "No existe el ambiente virtual. Ejecuta: python -m venv .venv"
}

if (Test-Path $AllureResults) {
    Remove-Item -LiteralPath $AllureResults -Recurse -Force
}

Write-Host "Ejecutando pruebas con marker: $Marker"
& $PythonExe -m pytest -m $Marker -s
$pytestExitCode = $LASTEXITCODE

$allureCommand = Resolve-AllureCommand
if (-not $allureCommand) {
    Write-Warning "Las pruebas finalizaron, pero no se encontro Allure CLI. Se conservaron resultados en allure-results."
    Write-Warning "Instala Allure CLI o agrega tools/allure-*/bin/allure.bat para generar el reporte HTML."
    exit $pytestExitCode
}

Write-Host "Generando reporte Allure en: $AllureReport"
& $allureCommand generate $AllureResults --clean -o $AllureReport

if ($OpenReport) {
    & $allureCommand open $AllureReport
}

exit $pytestExitCode

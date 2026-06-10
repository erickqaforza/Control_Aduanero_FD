param(
    [string]$Marker = "login",
    [string]$ReportName = "",
    [switch]$OpenReport,
    [switch]$SkipTests
)

$ErrorActionPreference = "Stop"

$ProjectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$PythonExe = Join-Path $ProjectRoot ".venv\Scripts\python.exe"
$AllureResults = Join-Path $ProjectRoot "allure-results"
if (-not $ReportName) {
    $ReportName = $Marker
}
$AllureReport = Join-Path $ProjectRoot "allure-reports\$ReportName"

function Import-DotEnv {
    $envFile = Join-Path $ProjectRoot ".env"
    if (-not (Test-Path $envFile)) {
        return
    }

    Get-Content $envFile | ForEach-Object {
        $line = $_.Trim()
        if (-not $line -or $line.StartsWith("#") -or -not $line.Contains("=")) {
            return
        }

        $key, $value = $line.Split("=", 2)
        $key = $key.Trim()
        $value = $value.Trim().Trim('"').Trim("'")
        if ($key) {
            Set-Item -Path "Env:$key" -Value $value
        }
    }
}

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

function Get-GitValue {
    param([string[]]$Arguments)

    try {
        $value = & git @Arguments 2>$null
        if ($LASTEXITCODE -eq 0) {
            return ($value | Select-Object -First 1)
        }
    } catch {
        return ""
    }

    return ""
}

function Write-AllureMetadata {
    if (-not (Test-Path $AllureResults)) {
        New-Item -ItemType Directory -Force -Path $AllureResults | Out-Null
    }

    $branch = Get-GitValue @("branch", "--show-current")
    $commit = Get-GitValue @("rev-parse", "--short", "HEAD")
    $repoUrl = Get-GitValue @("remote", "get-url", "origin")
    $executionDate = Get-Date -Format "yyyy-MM-dd HH:mm:ss"

    $environment = @(
        "Proyecto=Control Aduanero FD"
        "Ambiente=QA"
        "URL=$env:BASE_URL"
        "Navegador=$env:BROWSER_CHANNEL"
        "Headless=$env:HEADLESS"
        "SlowMo=$env:SLOW_MO ms"
        "Paises=Guatemala, Honduras, El Salvador"
        "Monedas=GTQ, USD, HNL"
        "Rama=$branch"
        "Commit=$commit"
        "Fecha de ejecucion=$executionDate"
    )
    Set-Content -Path (Join-Path $AllureResults "environment.properties") -Value $environment -Encoding UTF8

    $executor = [ordered]@{
        name = "Ejecucion local QA"
        type = "local"
        buildName = "$ReportName - $branch"
        buildUrl = $repoUrl
        reportName = "Control Aduanero FD - $ReportName"
        reportUrl = ""
    }
    $executor | ConvertTo-Json -Depth 4 | Set-Content -Path (Join-Path $AllureResults "executor.json") -Encoding UTF8

    $categories = @(
        [ordered]@{
            name = "Error de login"
            matchedStatuses = @("failed", "broken")
            messageRegex = ".*credenciales.*|.*login.*|.*autentic.*"
        },
        [ordered]@{
            name = "Error de formulario"
            matchedStatuses = @("failed", "broken")
            messageRegex = ".*locator.*|.*fill.*|.*select.*|.*click.*"
        },
        [ordered]@{
            name = "Error de validacion"
            matchedStatuses = @("failed")
            messageRegex = ".*expected.*|.*to_be_visible.*|.*AssertionError.*"
        },
        [ordered]@{
            name = "Error de sistema"
            matchedStatuses = @("broken")
            messageRegex = ".*timeout.*|.*network.*|.*500.*|.*503.*"
        }
    )
    $categories | ConvertTo-Json -Depth 6 | Set-Content -Path (Join-Path $AllureResults "categories.json") -Encoding UTF8
}

if (-not (Test-Path $PythonExe)) {
    throw "No existe el ambiente virtual. Ejecuta: python -m venv .venv"
}

Import-DotEnv

if ((Test-Path $AllureResults) -and -not $SkipTests) {
    Remove-Item -LiteralPath $AllureResults -Recurse -Force
}

if ($SkipTests) {
    if (-not (Test-Path $AllureResults)) {
        throw "No existe allure-results. Ejecuta el script sin -SkipTests primero."
    }
    $pytestExitCode = 0
} else {
    Write-Host "Ejecutando pruebas con marker: $Marker"
    & $PythonExe -m pytest -m $Marker -s
    $pytestExitCode = $LASTEXITCODE
}

$allureCommand = Resolve-AllureCommand
if (-not $allureCommand) {
    Write-Warning "Las pruebas finalizaron, pero no se encontro Allure CLI. Se conservaron resultados en allure-results."
    Write-Warning "Instala Allure CLI o agrega tools/allure-*/bin/allure.bat para generar el reporte HTML."
    exit $pytestExitCode
}

Write-AllureMetadata

Write-Host "Generando reporte Allure en: $AllureReport"
& $allureCommand generate $AllureResults --single-file --clean -o $AllureReport

if ($OpenReport) {
    & $allureCommand open $AllureReport
}

exit $pytestExitCode

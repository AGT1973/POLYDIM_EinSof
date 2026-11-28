param(
    [Parameter(Mandatory=$true)]
    [ValidateSet("facundo", "andrea", "joaquin")]
    [string]$Miembro,
    [string]$AladinHost = "192.168.100.21",
    [string]$InstallDir = "C:\POLYDIM_CLIENT"
)

Write-Host "=== POLYDIM-EINSOF: Onboarding PC de $Miembro ===" -ForegroundColor Cyan

# 1. Crear carpeta local segura sin Git para futuras credenciales autorizadas
$VaultDir = Join-Path $env:USERPROFILE ".gandalf_vault"
New-Item -ItemType Directory -Force -Path $VaultDir | Out-Null
icacls $VaultDir /inheritance:r /grant:r "${env:USERNAME}:(OI)(CI)F" "SYSTEM:(OI)(CI)F" | Out-Null
Write-Host "[OK] Boveda local creada con permisos restringidos: $VaultDir"

# 2. Preparar carpeta cliente
New-Item -ItemType Directory -Force -Path $InstallDir | Out-Null
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$ParentDir = Split-Path -Parent $ScriptDir
if (Test-Path (Join-Path $ParentDir "sabios_dispatcher.py")) {
    Copy-Item -Force (Join-Path $ParentDir "sabios_dispatcher.py") (Join-Path $InstallDir "sabios_dispatcher.py")
}
if (Test-Path (Join-Path $ScriptDir "helena_carrier_bridge.py")) {
    Copy-Item -Force (Join-Path $ScriptDir "helena_carrier_bridge.py") (Join-Path $InstallDir "helena_carrier_bridge.py")
}

# 3. Verificar Python + numpy
python -c "import numpy; print('[OK] numpy:', numpy.__version__)"

# 4. Probar conectividad a ALADIN Ollama (:11434) y Telepatia PMTP (:9999)
try {
    $resp = Invoke-RestMethod -Uri "http://${AladinHost}:11434/api/tags" -TimeoutSec 4
    Write-Host "[OK] ALADIN Ollama en linea ($($resp.models.Count) modelos)" -ForegroundColor Green
} catch {
    Write-Host "[WARN] No se alcanzo ALADIN Ollama en http://${AladinHost}:11434 (verificar LAN/Tailscale)" -ForegroundColor Yellow
}

$tcp = Test-NetConnection -ComputerName $AladinHost -Port 9999 -WarningAction SilentlyContinue
if ($tcp.TcpTestSucceeded) {
    Write-Host "[OK] ALADIN PMTP Telepathy (:9999) accesible" -ForegroundColor Green
} else {
    Write-Host "[WARN] ALADIN PMTP (:9999) no accesible desde esta red" -ForegroundColor Yellow
}

Write-Host "`nSiguiente paso: ejecutar 'python $InstallDir\sabios_dispatcher.py --dry-run' (modo $0 USD)."

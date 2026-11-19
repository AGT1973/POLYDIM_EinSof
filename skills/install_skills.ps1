# POLYDIM-EINSOF: Student Skills Pack Installer (PowerShell)
# Sello de Calibración: 19.11.2026 | Ariel García Traba

Write-Host "======================================================================" -ForegroundColor Cyan
Write-Host "  POLYDIM-EINSOF: STUDENT SKILLS PACK INSTALLER (1-CLICK)" -ForegroundColor Cyan
Write-Host "  Independent Research | Ariel Garcia Traba | Estándar 2030" -ForegroundColor Cyan
Write-Host "======================================================================" -ForegroundColor Cyan
Write-Host ""

$SourceDir = $PSScriptRoot
$TargetDirs = @(
    "$env:USERPROFILE\.gemini\antigravity\skills",
    "$env:USERPROFILE\.gemini\config\skills"
)

$Skills = @("ghost", "whisper", "council", "model-bridge", "quick-query", "manifold-verify", "redteam", "einsof-bootstrap")

foreach ($TargetDir in $TargetDirs) {
    if (-not (Test-Path $TargetDir)) {
        New-Item -ItemType Directory -Path $TargetDir -Force | Out-Null
    }
    Write-Host "[*] Installing skills into: $TargetDir" -ForegroundColor Yellow
    foreach ($s in $Skills) {
        $srcPath = Join-Path $SourceDir "$s\SKILL.md"
        if (Test-Path $srcPath) {
            $destDir = Join-Path $TargetDir $s
            if (-not (Test-Path $destDir)) { New-Item -ItemType Directory -Path $destDir -Force | Out-Null }
            Copy-Item -Path $srcPath -Destination "$destDir\SKILL.md" -Force
            Write-Host "  [OK] Installed $s" -ForegroundColor Green
        }
    }
}

Write-Host ""
Write-Host "[*] Running Silicon Verification..." -ForegroundColor Yellow
$verifyScript = Join-Path $SourceDir "scripts\manifold_verifier.py"
if (Test-Path $verifyScript) {
    python $verifyScript
}

Write-Host ""
Write-Host "======================================================================" -ForegroundColor Cyan
Write-Host "  [SUCCESS] Student Skills Pack Ready in Antigravity!" -ForegroundColor Green
Write-Host "  Available slash commands: /ghost, /whisper, /council, /call, /query, /verify-manifold, /redteam" -ForegroundColor White
Write-Host "======================================================================" -ForegroundColor Cyan

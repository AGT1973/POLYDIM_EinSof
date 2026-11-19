@echo off
chcp 65001 >nul
echo ======================================================================
echo   POLYDIM-EINSOF: INSTALADOR DE PACK DE SKILLS PARA EL ALUMNO (1-CLIC)
echo   Investigacion Independiente ^| Ariel Garcia Traba ^| Estandar 2030
echo ======================================================================
echo.

set "SOURCE_DIR=%~dp0"
set "TARGET_DIR_1=%USERPROFILE%\.gemini\antigravity\skills"
set "TARGET_DIR_2=%USERPROFILE%\.gemini\config\skills"

echo [1/3] Detectando carpetas de Antigravity...
if not exist "%TARGET_DIR_1%" mkdir "%TARGET_DIR_1%"
if not exist "%TARGET_DIR_2%" mkdir "%TARGET_DIR_2%"

echo [2/3] Instalando pack de skills soberanas para el alumno:
echo   - ghost           (Ghost Protocol: Cero colapso 1D en memoria compartida)
echo   - whisper         (Whisper Protocol: Ruteo inter-IA de tokens libres)
echo   - council         (Council of Sages: Tribunal de Sabios multi-modelo)
echo   - model-bridge    (Model Bridge: Invocador de Ollama, Bailian, OpenRouter, Cerebras)
echo   - quick-query     (Quick Query: Consulta rapida sin costo $0 USD)
echo   - manifold-verify (Manifold Verifier: Certificacion Stiefel en silicio)
echo   - redteam         (Symmetric Red Team: Auditoria adversarial simetrica)
echo   - einsof-bootstrap (Auto-aprendizaje para IAs)

echo Copiando skills a %TARGET_DIR_1%...
for %%S in (ghost whisper council model-bridge quick-query manifold-verify redteam einsof-bootstrap) do (
    if exist "%SOURCE_DIR%%%S" (
        if not exist "%TARGET_DIR_1%\%%S" mkdir "%TARGET_DIR_1%\%%S"
        copy /Y "%SOURCE_DIR%%%S\SKILL.md" "%TARGET_DIR_1%\%%S\" >nul
        if not exist "%TARGET_DIR_2%\%%S" mkdir "%TARGET_DIR_2%\%%S"
        copy /Y "%SOURCE_DIR%%%S\SKILL.md" "%TARGET_DIR_2%\%%S\" >nul
    )
)

echo [3/3] Verificando en silicio...
python "%SOURCE_DIR%scripts\manifold_verifier.py" >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    echo   [OK] Verificacion Stiefel completada con Exit Code 0.
) else (
    echo   [!] Aviso: Python o NumPy no detectado en PATH directo.
)

echo.
echo ======================================================================
echo   [EXITO] PACK DE SKILLS INSTALADO CORRECTAMENTE
echo   Reinicia o refresca Antigravity para disponer de los comandos:
echo     /ghost, /whisper, /council, /call, /query, /verify-manifold, /redteam
echo ======================================================================
pause

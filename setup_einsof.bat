@echo off
chcp 65001 >nul
title POLYDIM-EINSOF — Setup Alumno 1-Clic (Antigravity + Atelier)
echo ======================================================================
echo   Iniciando Instalador Soberano POLYDIM-EINSOF (Estándar 2030)
echo   Modo Alumno Cero-Conocimiento: Antigravity + EINSOF-II + Atelier
echo ======================================================================
echo.

set "PY_CMD="

REM 1. Verificar Python real >= 3.8 (evitando el stub vacio WindowsApps\python.exe de Windows 11)
python -c "import sys; sys.exit(0 if sys.version_info >= (3, 8) else 1)" >nul 2>nul
if %ERRORLEVEL% equ 0 (
    set "PY_CMD=python"
    goto :RUN_SETUP
)

py -3 -c "import sys; sys.exit(0 if sys.version_info >= (3, 8) else 1)" >nul 2>nul
if %ERRORLEVEL% equ 0 (
    set "PY_CMD=py -3"
    goto :RUN_SETUP
)

for %%P in (
    "%LOCALAPPDATA%\Programs\Python\Python313\python.exe"
    "%LOCALAPPDATA%\Programs\Python\Python312\python.exe"
    "%LOCALAPPDATA%\Programs\Python\Python311\python.exe"
    "C:\Python315\python.exe"
    "C:\Python312\python.exe"
) do (
    if exist %%P (
        set "PY_CMD=%%P"
        goto :RUN_SETUP
    )
)

echo [!] Python no detectado (o solo existe el alias vacio de Microsoft Store).
echo [*] Instalando Python 3.12 automaticamente via Windows Winget (User-Space, sin UAC)...
winget install -e --id Python.Python.3.12 --scope user --accept-package-agreements --accept-source-agreements
if exist "%LOCALAPPDATA%\Programs\Python\Python312\python.exe" (
    set "PY_CMD=%LOCALAPPDATA%\Programs\Python\Python312\python.exe"
    goto :RUN_SETUP
)

echo [ERROR] No se pudo detectar ni autoinstalar Python 3.10+.
echo Descargalo en 1 clic desde https://www.python.org/downloads/ (marca "Add Python to PATH").
pause
exit /b 1

:RUN_SETUP
echo [OK] Usando interprete Python verificado: %PY_CMD%
%PY_CMD% "%~dp0setup_einsof.py" --start-atelier %*

echo.
echo Presiona cualquier tecla para finalizar...
pause >nul

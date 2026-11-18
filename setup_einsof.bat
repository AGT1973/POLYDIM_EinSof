@echo off
chcp 65001 >nul
title POLYDIM-EINSOF — Setup Alumno 1-Clic
echo ======================================================================
echo   Iniciando Instalador Soberano POLYDIM-EINSOF (Estándar 2030)
echo ======================================================================
echo.

where python >nul 2>nul
if %ERRORLEVEL% neq 0 (
    echo [ERROR] No se encontró Python en el sistema.
    echo Por favor instala Python 3.10+ desde https://www.python.org/downloads/
    pause
    exit /b 1
)

python "%~dp0setup_einsof.py"

echo.
echo Presiona cualquier tecla para finalizar...
pause >nul

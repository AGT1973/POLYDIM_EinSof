@echo off
REM ═════════════════════════════════════════════════════════
REM  INSTALAR_WATCHDOG_REGLA13.bat 
REM  Registra el watchdog Regla 13 en Windows a las 03:00 AM
REM  EJECUTAR COMO ADMINISTRADOR
REM ═════════════════════════════════════════════════════════
schtasks /Create /SC DAILY /ST 03:00 /TN "POLYDIM_Regla13_Watchdog_3AM" /TR "python E:\POLYDIM_EINSOF\_AGY_BACKUP\regla13_watchdog.py" /F /RL HIGHEST
if %errorlevel% equ 0 (
    echo [OK] Tarea creada exitosamente.
    echo [OK] El watchdog se ejecutara todos los dias a las 03:00 AM.
    echo [OK] Para ver: schtasks /Query /TN "POLYDIM_Regla13_Watchdog_3AM"
) else (
    echo [ERROR] Permiso denegado. Debes ejecutar este archivo haciendo clic derecho -^> "Ejecutar como Administrador".
)
pause

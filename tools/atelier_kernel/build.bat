@echo off
rem ============================================================================
rem BUILD SCRIPT: ATELIER SILICON KERNELS (C++20 MSVC & RUST SOBERANO)
rem Estandar 2030: Compilacion in-situ con Exit Code 0 y cero dependencias externas
rem ============================================================================

setlocal enabledelayedexpansion

echo ============================================================================
echo COMPILANDO ATELIER SILICON KERNELS
echo ============================================================================

rem 1. Compilar Rust Kernel
echo [+] 1. Compilando Kernel Rust (rustc -O)...
rustc -O atelier_stiefel.rs -o atelier_stiefel_rs.exe
if %ERRORLEVEL% NEQ 0 (
    echo [-] Error al compilar Rust kernel.
    exit /b %ERRORLEVEL%
)
echo     [OK] atelier_stiefel_rs.exe generado.

rem 2. Compilar C++20 Kernel con MSVC
echo [+] 2. Configurando entorno MSVC y compilando Kernel C++20...
call "C:\Program Files (x86)\Microsoft Visual Studio\18\BuildTools\VC\Auxiliary\Build\vcvars64.bat" > nul 2>&1
cl.exe /std:c++20 /O2 /arch:AVX /EHsc /utf-8 atelier_stiefel.cpp /Fe:atelier_stiefel_cpp.exe > nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo [-] Error al compilar C++20 kernel con MSVC.
    exit /b %ERRORLEVEL%
)
echo     [OK] atelier_stiefel_cpp.exe generado.

echo ============================================================================
echo COMPILACION EXITOSA (EXIT CODE 0)
echo ============================================================================
exit /b 0

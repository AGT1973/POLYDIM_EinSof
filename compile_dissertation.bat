@echo off
REM ==============================================================================
REM POLYDIM-EINSOF MASTER DISSERTATION PDF COMPILATION SCRIPT (Windows)
REM ==============================================================================
echo [*] Compilando POLYDIM_DOCTORAL_DISSERTATION_FINAL.tex...

where pdflatex >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo [-] Error: pdflatex no se encuentra en el PATH.
    echo [*] Por favor asegurese de tener instalado TeXLive, MiKTeX o compilar en Overleaf/Docker.
    pause
    exit /b 1
)

echo [*] Paso 1: pdflatex (primera pasada)...
pdflatex -interaction=nonstopmode POLYDIM_DOCTORAL_DISSERTATION_FINAL.tex

echo [*] Paso 2: bibtex (resolucion de referencias)...
bibtex POLYDIM_DOCTORAL_DISSERTATION_FINAL

echo [*] Paso 3: pdflatex (segunda pasada)...
pdflatex -interaction=nonstopmode POLYDIM_DOCTORAL_DISSERTATION_FINAL.tex

echo [*] Paso 4: pdflatex (tercera pasada final)...
pdflatex -interaction=nonstopmode POLYDIM_DOCTORAL_DISSERTATION_FINAL.tex

if exist POLYDIM_DOCTORAL_DISSERTATION_FINAL.pdf (
    echo [!] EXITO TOTAL: PDF generado: POLYDIM_DOCTORAL_DISSERTATION_FINAL.pdf
) else (
    echo [-] Error en la generacion del PDF. Revise POLYDIM_DOCTORAL_DISSERTATION_FINAL.log
)

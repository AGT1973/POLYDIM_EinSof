#!/usr/bin/env bash
# ==============================================================================
# POLYDIM-EINSOF MASTER DISSERTATION PDF COMPILATION SCRIPT (Linux/macOS)
# ==============================================================================
set -e
echo "[*] Compilando POLYDIM_DOCTORAL_DISSERTATION_FINAL.tex..."

if ! command -v pdflatex &> /dev/null; then
    echo "[-] Error: pdflatex no se encuentra en el PATH."
    exit 1
fi

pdflatex -interaction=nonstopmode POLYDIM_DOCTORAL_DISSERTATION_FINAL.tex
bibtex POLYDIM_DOCTORAL_DISSERTATION_FINAL
pdflatex -interaction=nonstopmode POLYDIM_DOCTORAL_DISSERTATION_FINAL.tex
pdflatex -interaction=nonstopmode POLYDIM_DOCTORAL_DISSERTATION_FINAL.tex

if [ -f "POLYDIM_DOCTORAL_DISSERTATION_FINAL.pdf" ]; then
    echo "[!] EXITO TOTAL: PDF generado: POLYDIM_DOCTORAL_DISSERTATION_FINAL.pdf"
fi

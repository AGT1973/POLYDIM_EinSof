#!/usr/bin/env bash
set -euo pipefail

echo "=================================================================="
echo "POLYDIM SUITE :: 1-COMMAND REPRODUCIBLE AUDIT (ASAN/UBSAN + E2E)"
echo "=================================================================="

echo "[1/5] Compilando y ejecutando fuzzing C++20 con ASan + UBSan..."
g++ -std=c++20 -O1 -g -fsanitize=address,undefined -fno-omit-frame-pointer \
    tests/fuzz_abi_asan_ubsan.cpp -I tools/atelier_kernel -o /tmp/fuzz_abi_asan_ubsan
/tmp/fuzz_abi_asan_ubsan

echo "[2/5] Compilando y ejecutando kernel C++20 QDWH + memfd_create + 0600..."
g++ -std=c++20 -O2 -Wall -Wextra tools/atelier_kernel/atelier_stiefel.cpp \
    -o tools/atelier_kernel/atelier_stiefel_cpp -lrt
./tools/atelier_kernel/atelier_stiefel_cpp 1024 16

echo "[3/5] Ejecutando suite completa pytest (ABI v1, memfd_create, 0600, MAC, QDWH, Rust/C++)..."
python -m pytest tests -v

echo "[4/5] Ejecutando ablacion HumanEval+ / silicio St(16, 1024) con QDWH primario..."
python benchmarks/humaneval_plus_ablation_164_real.py

echo "[5/5] Ejecutando benchmark end-to-end T_total = T_proj + T_sync + T_copy..."
python benchmarks/benchmark_matriz_con_vs_sin_pmtp.py

echo "=================================================================="
echo "AUDITORIA REPRODUCIBLE COMPLETADA CON EXITO (EXIT CODE 0)"
echo "=================================================================="

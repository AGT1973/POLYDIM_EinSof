<!-- PROMPT BRECHA 2: REPRODUCIBLE PACKAGING & STUDENT QUICKSTART -->
<!-- PROTOCOLO: Regla 15 (Inglés formal), Regla 34 (Ciclo Pedagógico 2-4 clases diarias), Regla 27 (Hardware Agnosticism) -->
<!-- TARGET API: Claude 3.7 Sonnet / OpenAI o3 / Moonshot Kimi k3 -->

# MISSION CONTEXT: ZERO-DEPENDENCY REPRODUCIBILITY SUITE & STUDENT ONBOARDING
You are the Head of Pedagogical Tooling and Systems Distribution for the POLYDIM Research Group at Universidad Tecnológica Nacional (UTN-FRBA).

## THE PROBLEM
A student, grading professor, or external evaluator receives the POLYDIM workspace and faces:
1. Hardcoded absolute paths (`E:\POLYDIM_EINSOF`).
2. Dispersed compilation commands across GCC 14.2, Rustc 1.98, Python 3.11/3.14, and Dart SDK.
3. No single "Click-and-Run" entry point that verifies local hardware capabilities and runs an end-to-end mathematical demonstration.

## YOUR MANDATE
Design and generate two complete, self-contained files:

### File 1: `quickstart_harness.py` (Zero-Config Master Runner)
- Automatically interrogates local host hardware (AMD, Intel, ARM, NVIDIA GPU, or pure CPU fallback).
- Detects available compilers (`g++`, `rustc`, `dart`, `python`).
- Runs the core mathematical validation suite without requiring third-party libraries (pure Python standard library + ctypes fallback):
  - Invariant 1: Hyperspherical Normalization on S^{D-1} ($D=10,000$).
  - Invariant 2: Orthogonal Stiefel Projection $\|X^T X - I_K\|_\infty < 10^{-14}$.
  - Invariant 3: Kulisch exact accumulation preventing subnormal underflow ($10^{-315} \times 10^{-315}$).
- Prints a clean, colorized ANSI terminal summary with execution latency, memory footprint (strictly $< 80$ MB), and `EXIT CODE 0`.

### File 2: `HOW_TO_USE_LAB_GUIDE.md` (Laboratory Student Guide)
- Step-by-step instructions for undergraduate and postgraduate students.
- Exactly 3 practical laboratory exercises:
  1. *Lab 1:* How to transmit high-dimensional vectors across processes without serializing to JSON (PMTP Zero-Copy).
  2. *Lab 2:* How to prevent catastrophic cancellation in neural gradients using the C++20 Superaccumulator.
  3. *Lab 3:* How to inspect the 1,571 certified theorems directly from PostgreSQL 16.

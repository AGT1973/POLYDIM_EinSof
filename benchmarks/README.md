# 🧪 POLYDIM-EINSOF: Laboratorio Abierto de Benchmarks Científicos (Kits de Evaluación)
**Iniciativa:** POLYDIM-EINSOF | Ariel García Traba (Independent Research / Founder)

Bienvenido a la carpeta de **Kits de Pruebas y Benchmarks Comparativos**. 
Este directorio está diseñado para que alumnos, investigadores y desarrolladores puedan contrastar de forma empírica y reproducible el rendimiento de la **comunicación continua en variedades de Stiefel (POLYDIM/PMTP)** frente al **paradigma tradicional de tokenización de texto 1D**.

---

## 🚀 Kits Disponibles

### 1. Kit 01: Benchmark Comparativo en 1-Clic (Google Colab / Jupyter)
* **Archivo:** [`polydim_colab_benchmark_kit.ipynb`](./polydim_colab_benchmark_kit.ipynb)
* **Objetivo:** Comparar la latencia de inferencia entre un modelo estándar y el modelo acelerado con el adaptador de Stiefel de POLYDIM.
* **Ejecución Directa en Google Colab:**  
  [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/AGT1973/POLYDIM_CLA_V9/blob/main/BENCHMARK_KITS/polydim_colab_benchmark_kit.ipynb)

---

## 📋 ¿Cómo Agregar Nuevas Pruebas de Alumnos?
1. Crea un cuaderno Jupyter (`.ipynb`) o script en Python (`test_*.py`).
2. Mide dos condiciones:
   * **Línea Base (Baseline):** Input de texto -> Tokenizador -> Generación de tokens.
   * **Con POLYDIM:** Input continuo -> Proyección en Variedad de Stiefel -> `inputs_embeds`.
3. Registra tu hardware (CPU, GPU, RAM) y envía tu Pull Request o compártelo en clase.

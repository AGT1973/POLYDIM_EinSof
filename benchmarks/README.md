# 📊 POLYDIM SUITE — REPOSITORIO OFICIAL DE BENCHMARKS Y VALIDACIONES EN SILICIO

Este directorio reúne los registros crudos, cuadernos interactivos (Kaggle / Google Colab) y pruebas asintóticas en silicio físico correspondientes a la evaluación multipolar de **PMTP (Polydim Memory Tensor Protocol)** y **EinsofOS**.

---

## 🔬 1. Resumen de Pruebas Empíricas Clave

### A. Transferencia Latente Inter-Modelo sin Tokens (Qwen2.5 $\to$ TinyLlama)
- **Script**: `run_six_decisive_proofs.py` / `polydim_two_models_transfer_colab.ipynb`
- **Metodología**:
  1. Se extrae el estado oculto latente continuo ($D=4096$) de **Qwen2.5-0.5B**.
  2. Se proyecta isométricamente sobre la Variedad de Stiefel $\text{St}(4096, 2048)$ mediante el adaptador algebraico ortogonal **SVD Procrustes** (`adapter_weights.safetensors`, 67.1 MB en Hugging Face).
  3. Se transfiere vía memoria compartida `PmtpShmBus` (**0 tokens generados**, $<0.005$ ms).
  4. Se inyecta en la capa de atención de **TinyLlama-1.1B**.
- **Resultado Certificado**:
  - **Aciertos**: 15 de 20 pruebas conceptuales (**75.0%** de precisión).
  - **Línea Base de Azar**: 20.0%.
  - **Ahorro de Tokens**: 100% de los tokens de comunicación inter-agente suprimidos.

### B. Cadenas de Razonamiento Multi-Agente (Multi-Hop Chains)
- **Reporte**: `EXTERNAL_BENCHMARK_REPORT.json`
- **Comparación**: Flujo de texto tradicional (vLLM / REST API) vs. PMTP-CORE en RAM.
- **Resultados**:
  - En comunicación tradicional de texto, el volumen de tokens consumidos y de KV-Cache crece **linealmente** en cada salto ($>5,000$ tokens acumulados).
  - En PMTP, el consumo se mantiene **plano** (~567 tokens totales para el prompt inicial y la respuesta humana final).
  - **Ahorro Neto Medido**: Entre **57% y 93%** de reducción de tokens y operaciones de decodificación autorregresiva.

### C. Certificación en Silicio Físico (AVX2 / FP64 / Qwen2.5)
- **Script de Auditoría**: `test_pmtp_silicon.py` (Local Workstation)
- **Resultados Crudos (Exit Code 0)**:
  - **T-MP18**: Defecto de ortogonalidad $\|\mathbf{W}^T \mathbf{W} - \mathbf{I}\|_\infty = \mathbf{1.11 \times 10^{-15}}$ (Newton-Schulz Orden 5).
  - **T-MP21**: Inmutabilidad anti-aliasing y contrato de leases.
  - **T-MP22**: Interoperabilidad neuronal con KV-Cache real: `max_abs_logit_diff = 0.0` (idéntico bit a bit).
  - **Latencia de Transferencia**: $<0.005$ ms en RAM física compartida.

---

## 📓 2. Cuadernos Interactivos Disponibles en Colab y Kaggle

Los siguientes cuadernos permiten reproducir de forma 100% autónoma y gratuita en Google Colab (GPU T4 / L4) y Kaggle los resultados de la suite:

1. **`polydim_two_models_transfer_colab.ipynb`**
   - Demostración de transferencia latente entre dos modelos dispares sin tokens intermedios.
2. **`polydim_colab_suite_20_benchmarks.ipynb`**
   - Batería de 20 evaluaciones sistemáticas de deriva numérica, retención y velocidad.
3. **`polydim_colab_turing_t4_benchmark.ipynb`**
   - Medición de throughput continuo y comparación contra decodificación secuencial en GPU T4.
4. **`07_COLAB_II_DEEPSEEK_QWEN38_PMTP_BENCHMARK.ipynb`**
   - Comparación cruzada de alta fidelidad entre DeepSeek y Qwen en espacios estiefelianos.

---

## 🏛 3. Veredictos del Tribunal de los 7 Sabios

Para consultar los dictámenes completos y la matriz de consenso de:
- **Alibaba Qwen (Qwen 3.7-Plus)**
- **Anthropic Claude (3.5 Sonnet)**
- **DeepSeek (V3 / R1)**
- **Google Gemini (Gemini 3.8)**
- **Perplexity AI (Sonar-Pro)**
- **Moonshot Kimi (K3.1)**
- **Zhipu AI (GLM-5.2)**

Abra en su navegador el dashboard oficial:
👉 [introduction/tribunal_sabios_dictamenes.html](../introduction/tribunal_sabios_dictamenes.html)

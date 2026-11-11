# 🎮 Ejemplos Interactivos y Simuladores Pedagógicos (POLYDIM SUITE)

Esta carpeta contiene implementaciones visuales e interactivas de referencia para alumnos, investigadores y desarrolladores que quieran explorar el funcionamiento del protocolo PMTP frente a las arquitecturas tradicionales de LLMs.

---

## 📂 Contenido del Directorio

### 1. Simuladores de Arquitectura (Dual Language)
- **🇪🇸 [`pmtp_vs_traditional_simulator_es.html`](pmtp_vs_traditional_simulator_es.html):**  
  Simulador completo en **Español** con renderizado tipográfico matemático en **KaTeX**. Visualiza el carril tradicional 1D (pérdida DPI, peajes de API y riesgo de alucinación) versus el carril continuo PMTP sobre la variedad de Stiefel ($\text{St}(D, r)$) y mapeo unitario en espacio de Hilbert.
- **🇬🇧 [`pmtp_vs_traditional_simulator_en.html`](pmtp_vs_traditional_simulator_en.html):**  
  Full **English** architecture visualizer with KaTeX typesetting and zero canvas layout shift.

---

## ⚡ Características Técnicas Demostradas en Silicio
1. **Zero-Copy en Memoria Compartida (`PmtpShmBus`):**  
   Mapeo físico directo sin serialización de cadenas de texto. 0 tokens consumidos en tránsito.
2. **Retracción Polar Newton-Schulz (Orden 4 / Orden 10):**  
   Ortogonalización continua de tensores latentes con error acotado en $\|\mathbf{X}^T \mathbf{X} - \mathbf{I}_r\|_\infty \le 10^{-15}$.
3. **Erradicación del Cuello de Botella DPI (*Data Processing Inequality*):**  
   Preservación del 99.999% de la fidelidad informativa frente a la degradación acumulativa del texto serializado.
4. **Independencia de Antivirus (Zero-Antivirus Conflict):**  
   Ejecutable en cualquier navegador web moderno en texto plano HTML5 + JS nativo, sin dependencias binarias externas ni descargas de ejecutables opacos.

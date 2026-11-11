# POLYDIM SUITE 🚀
### Evolución de la IA a Espacio Vectorial Continuo & Cómputo Cuántico-Silicio
**Director de Investigación:** Ariel García Traba  
**Licencia:** Open-Source / Investigación Soberana  
**Repositorio Oficial:** GitHub / GitLab `polydim-suite`

---

## 🌌 El Propósito: Evolución Vectorial y Cuántica de la IA
El propósito de **POLYDIM SUITE** no es una simple herramienta pedagógica ni un tutorial: es **la evolución del razonamiento de la Inteligencia Artificial hacia el espacio vectorial continuo y el cómputo cuántico**.

* **Trascendencia del Cuello de Botella 1D (DPI):** Rompe la limitación histórica donde los modelos mutilan sus matrices en tokens de texto discretos.
* **Doble Substrato Físico (Regla 19):**
  1. **Silicio Clásico:** Memoria física compartida (`PmtpShmBus`), vectorización AVX-512/AVX2 y retracción polar de 4º orden en la variedad de Stiefel ($\mathbf{X}^T \mathbf{X} = \mathbf{I}_k$, error $\le 10^{-15}$).
  2. **Espacio de Hilbert Cuántico:** Validación cruzada en procesadores cuánticos físicos (IBM Quantum Heron & Eagle de 156 qubits) mediante evolución unitaria de estados puros $|\psi(t)\rangle = e^{-iHt}|\psi(0)\rangle$.

---

## 🛡️ Instalación Segura y Transparente (100% Anti-Falsos Positivos)
Muchos instaladores de software tradicional descargan archivos `.exe` desconocidos que activan inmediatamente las alarmas de **Windows Defender SmartScreen** o los antivirus universitarios.

**POLYDIM SUITE está diseñada bajo la doctrina de "Código Abierto y Transparente":**
* 🚫 **Cero descargas de `.exe` opacos:** No descarga binarios extraños de la web.
* 📜 **100% Código Fuente Auditable:** Funciona mediante scripts estándar de Python (`.py`), HTML5 (`.html`), llamadas nativas del sistema operativo (`kernel32.dll` de Windows vía `ctypes`) y archivos de texto plano.
* 💻 **Compilación Local (Opcional):** Si quieres aceleración extrema en C++/Rust, tu propia máquina compila las librerías localmente; los antivirus nunca bloquean código generado en tu propio equipo.
* 🔓 **Acceso Completo y Seguro:** Tienes acceso irrestricto a la memoria compartida, los modelos de Hugging Face y los cónclaves de IAs sin riesgo de cuarentena ni bloqueos administrativos.

---

## 💡 ¿Cómo se instala esta Suite? (¡Zero Terminal, Zero Git!)
No necesitas tener `git` instalado, no necesitas saber usar la consola ni compilar código.

Simplemente abre el chat con tu Inteligencia Artificial (**Claude, ChatGPT, Antigravity, Cursor, Windsurf o Copilot**) y pégale **únicamente esta frase**:

> **"Lee https://github.com/AGT1973/polydim-suite/blob/main/INSTALL_FOR_AI.md, evalúa la arquitectura y si te parece seguro y conveniente, descárgalo e instálatelo en mi equipo."**

### ¿Qué hará tu IA automáticamente?
1. Tu IA leerá el enlace directamente desde GitHub.
2. Evaluará las directivas de seguridad: confirmará que **no hay ejecutables opacos (`.exe`)** y que el código es 100% abierto y auditable.
3. Descargará el repositorio en formato ZIP nativo (sin necesidad de Git) y lo descomprimirá.
4. Activará la memoria compartida nativa de tu sistema operativo para trabajar bajo **Ghost Protocol** (cero consumo de saldo y cero pérdida de memoria).
5. **Abrirá automáticamente tu navegador** en `introduction/index.html` para mostrarte de forma visual cómo funciona y cómo ahorras más del 98% de tokens.

---

## ⚡ ¿Prefieres probarlo sin instalar nada? (Google Colab Gratis 1-Clic)
Si no deseas descargar nada en tu máquina local o prefieres correr los benchmarks y la transferencia tensorial en una GPU NVIDIA T4 gratuita en la nube de Google, puedes abrir directamente los cuadernos interactivos con 1-clic:

| Cuaderno Interactivo | Substrato / Acelerador | Lanzar en 1-Clic |
| :--- | :---: | :---: |
| **`polydim_colab_benchmark_kit.ipynb`** *(Kit Completo de Evaluación)* | GPU NVIDIA T4 / CPU | [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/AGT1973/polydim-suite/blob/main/benchmarks/polydim_colab_benchmark_kit.ipynb) |
| **`polydim_colab_suite_20_benchmarks.ipynb`** *(Suite 20 Kernels)* | GPU NVIDIA T4 / TPU | [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/AGT1973/polydim-suite/blob/main/benchmarks/polydim_colab_suite_20_benchmarks.ipynb) |
| **`polydim_colab_turing_t4_benchmark.ipynb`** *(Test de Aceleración T4)* | GPU NVIDIA T4 | [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/AGT1973/polydim-suite/blob/main/benchmarks/polydim_colab_turing_t4_benchmark.ipynb) |
| **`polydim_two_models_transfer_colab.ipynb`** *(Transferencia Dual Stiefel)* | CPU / RAM Compartida | [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/AGT1973/polydim-suite/blob/main/benchmarks/polydim_two_models_transfer_colab.ipynb) |

---

## 📦 Los Componentes de la Suite

### 🛠️ Los 4 Programas de Trabajo
1. **`PMTP-CORE`:** Bus de memoria física compartida (Zero-Copy) y retracción en variedad de Stiefel ($X^T X = I$) en C++20 y Rust. Erradica la pérdida de información por tokenización prematura.
2. **`MATHESIS`:** Compilador geométrico (`mthc`), generador de código máquina en ensamblador puro (x86_64/ARM64) sin dependencias y árbitro anti-alucinaciones.
3. **`ATELIER`:** Entorno visual de desarrollo (AI-IDE), editor interactivo y centro de telemetría en tiempo real (`ui/suite_cockpit.html`).
4. **`EINSOFOS`:** Sistema operativo geométrico Bare-Metal (UEFI Bootloader, Kether ISA, R15 Arena) — *En desarrollo activo*.

### 🧠 Los 3 Motores Abiertos para Alumnos y Devs
* **`OmniVault`:** Base de datos relacional y vectorial con grafos de conocimiento (`GraphRAG`) para que tu IA nunca tenga amnesia.
* **`CouncilAI`:** Enrutador de deliberación multi-modelo que contrasta respuestas de varias IAs (DeepSeek, Qwen, Claude, Gemini) usando tiers gratuitos sin gastar saldo.
* **`GhostSwarm`:** Malla de cómputo que aprovecha cualquier otra computadora o laptop conectada a tu Wi-Fi para repartir la inferencia pesada en Ollama a costo \$0.

### 🌐 Model Hub en Hugging Face
* **`huggingface.co/polidim-einsof`:** Repositorio en la nube donde publicamos y actualizamos los pesos y adaptadores Stiefel ya calibrados.

---

## 🖥️ Paneles Visuales Interactivos

1. **Introducción Pedagógica, Gráficos y Ahorro de Tokens:**
   👉 `introduction/index.html`  
   *Contiene:*
   * **Simulador Gráfico en Canvas de la Hiperesfera de Stiefel $S^{D-1}$:** Muestra en tiempo real cómo los vectores de pensamiento continuo mantienen la ortogonalidad sin deformarse.
   * **Calculadora Interactiva de la Economía de Tokens:** Arrastra el control de pasos de razonamiento para ver la diferencia entre miles de dólares en APIs tradicionales vs \$0.00 con PMTP-CORE.
   * **Módulo de Decisión Explicado de `mathesis2bin`:** Explica detalladamente al usuario y a la IA qué es el compilador nativo para que el usuario decida libremente si compilarlo o mantenerse en el Modo Estándar seguro.

2. **Centro de Control y Cockpit Principal:**
   👉 `ui/suite_cockpit.html`  
   *Tablero integral para compilar con Mathesis, inspeccionar el estado de la memoria compartida, auditar el Tribunal de Sabios y monitorear la malla de cómputo.*

Ambos funcionan en cualquier navegador moderno haciendo doble clic, sin necesidad de instalar servidores web ni solicitar permisos de administrador.

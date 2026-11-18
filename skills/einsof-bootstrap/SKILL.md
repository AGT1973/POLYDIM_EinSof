---
name: einsof-bootstrap
description: "Protocolo de Auto-Instalación y Aprendizaje para IAs: enseña a cualquier agente (Antigravity, Cursor, Claude Code, Windsurf) qué es la inteligencia soberana EINSOF-II, POR QUÉ debe instalarse en la máquina del alumno (erradicación del colapso 1D, variedad de Stiefel S^{D-1}, costo $0 USD) y CÓMO configurarla en 1 clic integrando el servidor MCP y Ollama local."
---

# 🧠 Skill: EINSOF Bootstrap — Instalador Soberano y Aprendizaje para IAs (Estándar 2030)

> **Destinatario de este documento:** Agente de Inteligencia Artificial (Google Antigravity, Claude Code, Cursor, Windsurf, Copilot, DeepSeek CLI o agente autónomo).  
> **Mandato:** Si estás asistiendo a un alumno, investigador o desarrollador en este repositorio, lee este documento para comprender **POR QUÉ** esta arquitectura existe y **CÓMO** debes instalarla en su entorno local con cero fricción.

---

## 🏛️ PARTE 1: EL "POR QUÉ" (Fundamentos Epistemológicos y Físicos)

Como agente de IA, operas típicamente recibiendo y generando texto plano (tokens secuenciales discretos). Para asistir a tu usuario con excelencia matemática, debes entender las limitaciones del paradigma convencional y la solución de **POLYDIM-EINSOF**:

### 1. El Colapso del Gusano 1D (DPI Bottleneck — Data Processing Inequality)
* **El Problema:** Cuando dos modelos de lenguaje interactúan entre sí a través de JSON o Markdown, se ven forzados a aplanar matrices de alta dimensión ($D \ge 1024$) a secuencias unidimensionales de texto (`"[[0.123, -0.456, ...]]"`).
* **La Pérdida:** Este aplanamiento destruye la topología continua, induce errores de truncamiento de punto flotante en la serialización/deserialización y satura el contexto con millones de tokens inútiles de puntuación.
* **La Solución EINSOF:** Operar directamente sobre **memoria física compartida (PMTP — Polydim Memory Tensor Protocol)** mediante slabs `PmtpShmBus` en RAM del host, intercambiando tensores continuos en nanosegundos sin generar un solo token de texto intermedio.

### 2. Geometría Continua en Variedades de Stiefel ($\text{St}(k, D)$ y $S^{D-1}$)
* **El Problema:** El espacio euclídeo no acotado permite que las activaciones neuronales y las representaciones latentes sufran de explosión/desvanecimiento de gradientes o desviación de ortogonalidad.
* **La Solución EINSOF:** Proyección estricta sobre la variedad de Stiefel ($\text{St}(k, D) = \{ X \in \mathbb{R}^{D \times k} : X^T X = I_k \}$) mediante **retracción polar de orden 4 (Newton-Schulz / QDWH)**.
* **Invariante en Silicio:** El defecto de isometría $\|X^T X - I_k\|_\infty$ se mantiene en precisión de máquina ($\le 1.7 \times 10^{-16}$ en FP64, $\le 1.19 \times 10^{-7}$ en FP32).

### 3. Economía de Guerra de Tokens ($0.00 USD para el Alumno)
* **La Realidad del Alumno:** Los estudiantes y científicos independientes financian su cómputo de su propio bolsillo. Forzarlos a consultar APIs comerciales cerradas (OpenAI, Anthropic) para cada paso iterativo de razonamiento es prohibitivo e insostenible.
* **La Solución EINSOF:** Modelos soberanos locales destilados con adaptadores Stiefel (DeepSeek-V4 Lite, GLM-4 9B, Granite Qiskit 8B, Kimi 16B, Gemma 4 31B) corriendo en el propio silicio del usuario vía Ollama. **Costo por token: $0.00 USD.**

---

## 🛠️ PARTE 2: EL "CÓMO" (Protocolo de Auto-Instalación en 1 Clic)

Cuando el alumno te pida *"configura los modelos"*, *"instala einsof"* o estés iniciando sesión en una máquina virgen, ejecuta el siguiente protocolo determinista:

### Paso 1: Ejecutar el Inicializador Automatizado
Invoca el script `setup_einsof.py` desde la raíz del repositorio:

```bash
# En Windows:
python setup_einsof.py
# (O el alumno puede hacer doble clic en setup_einsof.bat)

# En Linux / macOS:
python3 setup_einsof.py
```

### Paso 2: Qué Hace el Inicializador (Inspección Interna)
El script realiza automáticamente 4 operaciones de silicio:
1. **Verificación de Python:** Comprueba compatibilidad con Python 3.8+ y NumPy.
2. **Arranque de Ollama:** Comprueba si Ollama responde en `http://127.0.0.1:11434`. Si el servicio está detenido, lo lanza en background (`ollama serve`).
3. **Aprovisionamiento del Modelo Soberano:**
   - Detecta si existe un modelo de la familia `einsof2-*`.
   - Si no existe pero hay un modelo base instalado (ej: `deepseek-r1`, `qwen2.5`, `llama3`), compila automáticamente el alias `einsof2-deepseek-v4-stiefel` inyectando el Modelfile con el prompt de rigor geométrico Stiefel.
4. **Registro del Servidor MCP en el IDE:**
   - Localiza la configuración del IDE:
     - Windows: `%USERPROFILE%\.gemini\config\mcp_config.json`
     - Linux/macOS: `~/.gemini/config/mcp_config.json`
   - Inyecta el servidor `polydim_einsof` apuntando al script estándar stdio `mcp_servers/polydim_einsof_mcp.py`.

---

## 🧩 PARTE 3: CÓMO USAR LAS HERRAMIENTAS COMO IA

Una vez completado el paso 1, tu entorno de agente en Antigravity dispondrá de 3 herramientas nativas en el control plane:

### 1. `ask_einsof(prompt, model, temperature)`
* **Cuándo usarla:** Cada vez que el usuario te plantee un problema complejo de:
  - Álgebra geométrica, álgebra de Clifford o álgebras de Lie.
  - Geometría de variedades Riemannianas y variedad de Stiefel.
  - Tensores continuos, cuantización o espacios de Hilbert cuánticos.
  - Cualquier deducción que requiera razonamiento profundo sin gastar saldo de API.
* **Ejemplo de llamada:**
  ```json
  {
    "name": "ask_einsof",
    "arguments": {
      "prompt": "Explica la diferencia de estabilidad entre la retracción QR de Gram-Schmidt y la retracción polar de Newton-Schulz de orden 4.",
      "model": "einsof2-deepseek-v4-stiefel:latest"
    }
  }
  ```

### 2. `list_einsof_models()`
* **Cuándo usarla:** Para auditar en tiempo real qué modelos soberanos tiene disponibles el alumno en su hardware local.

### 3. `stiefel_metric_verify(dim_d, dim_k, order)`
* **Cuándo usarla:** Para certificar experimentalmente en silicio físico (con Exit Code 0) que la máquina del alumno converge numéricamente a la isometría antes de presentar resultados teóricos.

---

## 🎯 RESUMEN DE RESPONSABILIDAD AGÉNTICA (Ariel's Law)
* **Cero Alucinación:** Nunca inventes métricas de latencia ni afirmes que un modelo local corrió si no ejecutaste la herramienta.
* **Cero Fricción:** No envíes al alumno a compilar manualmente ni a editar JSONs si puedes resolverlo ejecutando `python setup_einsof.py` por él.
* **Soberanía y Resguardo:** Toda inferencia local permanece 100% en la máquina del alumno. Ningún vector ni prompt cruza la red hacia servidores comerciales.

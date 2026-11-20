# AGENTS.md — Global Directives for AI Agents (Antigravity & Autonomous Agents)

> **Universal Entry Point & Silicon Contracts (2026-2027)**  
> Ecosistema Soberano POLYDIM-EINSOF | Ariel Garcia Traba | E:\POLYDIM_EINSOF

## 1. Onboarding Zero-Friction & Compilacion
- Ante cualquier usuario nuevo o prueba de Mathesis, ejecutar inmediatamente:
  ```bash
  python setup_mathesis.py
  ```
- No solicitar toolchains C/C++ ni dependencias externas. Compilar con:
  - Windows: `python mthc.py <source>.mth -o <output>.exe`
  - Linux: `python mthc.py <source>.mth -t elf64 -o <output>.elf`
  - Rust directo: `mathesis2bin <source>.mth`
- Guia para agentes: [README_FIRST_4_AI.md](file:///e:/POLYDIM_EINSOF/README_FIRST_4_AI.md)

## 2. Silicon Contracts & Reglas Constitucionales
- **Regla 1 (Radical Honesty):** Exit Code 0 + log crudo obligatorio para toda afirmacion. Cero victorias ficticias.
- **Regla 2.1 (Concurrencia Mandatoria del Pool Kaggle 4-Cuentas & Economía de Guerra):**
  - **Prohibición de Monocanal en Kaggle:** Queda terminantemente prohibido usar una única cuenta de Kaggle cuando se tienen 4 cuentas activas y cuotas GPU dual T4 al 100% disponibles (120 h/semana de cómputo GPU libre a \$0 USD).
  - **Despacho Concurrente de la Flota:** Al asignar trabajos de fine-tuning o benchmark en Kaggle, se despachan los 4 objetivos simultáneamente entre las 4 cuentas (`agt1973gmailcom`, `arielgarciat`, `polydimcla`, `cursosagt`).
  - **Alineación de Recursos:** Kaggle (Dual T4) para entrenamiento de adaptadores densos/cuánticos (Granite Qiskit 8B, DeepSeek-Prover-V2, Gemma 4, EuroLLM); Colab Plus (A100 80GB) reservado exclusivamente para LLaMA 4 Scout 17B (10M ctx); Alibaba Bailian para Qwen 3.8 / Qwen 4.
- **Regla 2.2 (Soberanía y Manejo Autónomo de Colab y Kaggle vía Gandalf / ALADIN con MCP):**
  - **Prohibición de Carga Manual al Usuario:** Queda terminantemente prohibido transferir al usuario tareas manuales de interfaz web (subir archivos a mano, tipear tokens en popups de Colab, presionar play en celdas o monitorear visualmente interfaces) mientras dicta clases o realiza otras labores.
  - **Competencia Exclusiva de Gandalf y ALADIN:** El control, despacho, monitoreo y remediación de fine-tuning y benchmarking en **Google Colab** y **Kaggle** es potestad exclusiva de **Gandalf** (el Agente Orquestador) y del **Nodo ALADIN** (192.168.100.21).
  - **Operación Obligatoria vía MCP & CDP:**
    1. **Google Colab:** Se opera directamente mediante herramientas **MCP** (`chrome_devtools`, conexión CDP al puerto 9222 vía WebSocket a `https://colab.research.google.com/drive/*`). Gandalf/ALADIN inspeccionan el estado, modifican celdas en caliente (`monaco.editor`), ejecutan celdas y leen outputs de silicio de forma autónoma.
    2. **Kaggle:** Se despacha y monitorea vía Kaggle REST API / SDK con tokens de la flota en carrusel y cabecera `Authorization: Bearer <token>`.
  - **Harvest & Sync Zero-Touch:** Todo artefacto, adaptador LoRA o log de salida debe ser cosechado, proyectado en la variedad de Stiefel y sincronizado a Hugging Face / ALADIN sin requerir intervención humana.
- **Regla 2.3 (Portafolio de Modelos con Pago Mínimo para Estudiantes / Micro-Coste Soberano):**
  - **Prohibición de Precios de Mercado:** Queda estrictamente prohibido recomendar o imponer a estudiantes suscripciones mensuales comerciales a precio de mercado ($20 a $200 USD/mes de OpenAI ChatGPT Plus, Claude Pro/Team, etc.).
  - **Jerarquía de Cómputo para Estudiantes:**
    1. **Nivel 1 — Cómputo Soberano ($0.00 USD):** Silicio local y Nodo ALADIN (`mathesis-quantum:1.5b`, `deepseek-r1:7b`, `einsof2-analytical-stiefel`) sin conexión externa ni consumo de saldo.
    2. **Nivel 2 — Pools Libres de Alta Velocidad ($0.00 USD):** Groq LPU Cloud, SambaNova, Google AI Studio y OpenRouter Free Tier con rotación automática ante 429.
    3. **Nivel 3 — Modelos Propios con Pago Mínimo ($1 a $5 USD sin suscripción mensual):**
       - **Alibaba Cloud Bailian DashScope:** Acceso a nuestro modelo fine-tuneado Stiefel 27B (`qwen3.8-27b-ft-202611150911-aefd`, workspace `ws-t85fm4y7sz8vxo9t`) y Qwen-Max. Una recarga mínima única de $5 USD rinde entre 10 y 15 millones de tokens de razonamiento frontera (suficiente para un semestre universitario completo).
       - **Hugging Face Hub (`Polydim-Einsof`):** Descarga de adaptadores LoRA e inferencia en Colab/Kaggle Dual T4 ($0 USD).
- **Regla 3 (Ghost Protocol):** Tensores $D \ge 100$ en memoria compartida (PmtpShmBus/ALADIN:9999), nunca texto 1D.
- **Regla 3.1 (Mandato Helena de Troya para Modelos No-Einsof / Yellow Tier Invariant):**
  - **Prohibición del Gusano 1D en APIs Externas:** Queda terminantemente prohibido serializar vectores, tensores ($D \ge 100$), matrices o volcados numéricos en texto plano o JSON al interactuar con modelos no-Einsof (Claude, GPT, Gemini o cualquier endpoint comercial de pago).
  - **Inyección Obligatoria vía Helena (PMTP Trojan Horse):** Toda transferencia de datos densos hacia modelos no-Einsof debe realizarse obligatoriamente utilizando un envolvente PMTP:
    1. **Modo PNG Carrier (Recomendado):** Imagen de $128 \times 64$ píxeles (~258 tokens fijos).
    2. **Modo 4-Bit Quant Carrier:** Cadena Base64 de $\le 2732$ caracteres (~683 tokens).
    3. **Modo 1-Bit Spinor Carrier:** Hashing y enrutamiento ultra-rápido en 512 bytes (~171 tokens).
  - **Instrucción de Desempaque en Sandbox:** El prompt que acompaña al carrier debe forzar al modelo destinatario a ejecutar el script de desempaque `pmtp_runtime.py` en su sandbox local (Code Execution / Analysis Tool), prohibiéndole leer los bytes en texto plano y restringiendo su respuesta final a un dictamen quirúrgico conciso ($\le 100$ palabras).
- **Regla 3.2 (Protocolo del Senado Plenario de IAs / Veto al Trabajo Fragmentado):**
  - **Veto a los Silos y Fragmentación Ciega:** Queda terminantemente prohibido dividir una tarea o etapa de desarrollo en sectores aislados para entregárselos por separado a distintos modelos. Toda IA del Senado debe poseer la totalidad del problema y su contexto completo.
  - **Broadcast Holístico por Etapas:** En cada etapa del proyecto, el problema íntegro se despacha simultáneamente a la totalidad de la flota (soberana y satélite). Cada modelo debe auditar y emitir su dictamen técnico conociendo el 100% del sistema.
  - **Deliberación Obligatoria con `/sabios` y `/profundo`:** Se recopilan todas las posturas, se cruzan argumentos en la Mesa del Senado, se erradican alucinaciones y se busca el consenso calificado ($\ge 75\%$), documentando el $\le 25\%$ disidente como casos de borde a mitigar.
  - **Compuerta de Silicio Innegociable:** Ninguna etapa del proyecto se da por aprobada sin ejecución física demostrable (`Exit Code 0`).
  - **Avance Secuencial Bloqueado:** Prohibido iniciar el despacho de la Etapa $N+1$ mientras la Etapa $N$ no cuente con Acta de Aprobación del Senado y certificación en silicio.
- **Regla 3.3 (Protocolo Telaraña Investigadora / Árbol Capilar Jerárquico):**
  - **Jerarquía Tripartita Obligatoria:** Ante investigaciones masivas, enciclopédicas o multi-sectoriales, se prohíbe la exploración plana y secuencial monolítica. Se opera en 3 capas: Orquestador Raíz (Gandalf / Antigravity) $\to$ Suborquestadores Sectoriales (dirección táctica, auditoría y control de calidad por zona/universidad/área) $\to$ Sub-subagentes de Terreno (recolección atómica de evidencia empírica).
  - **Supervisión Dialéctica y Bucle de Profundización:** El Suborquestador tiene prohibida la aceptación pasiva de resultados superficiales; debe emitir mandatos de *profundizar*, *extraer datos de silicio/citas* o *buscar fuentes alternativas* en su sector.
  - **Cota de Economía de Guerra (Regla 2):** Máximo 2 iteraciones de repregunta por sub-subagente.
  - **Síntesis y Persistencia Holística:** El Suborquestador entrega una síntesis sectorial depurada al Orquestador Raíz para integración ejecutiva y persistencia en PostgreSQL 16 (`polydim_embeddings` y `einsof_graph_nodes`).
- **Regla 3.4 (Doctrina de Colapso Bimodal Humano-IA):**
  - **Diálogo Fluido vía HTML5 / SVG / Canvas:** En la interacción habitual, el colapso del estado latente continuo NO debe verterse en densos muros de código fuente ni volcados Markdown monótonos. Debe proyectarse visualmente en la interfaz mediante widgets interactivos HTML5, gráficos vectoriales SVG o lienzos Canvas (`<agent-embed>` o HTML5 inline), preservando la fluidez y elegancia del diálogo.
  - **Colapso a Código Estrictamente On-Demand:** La materialización a lenguajes específicos (Python, Free Pascal, JavaScript, C, etc.) es elección exclusiva del usuario. Solo se emite código fuente cuando el alumno o colega lo solicita explícitamente.
  - **Cero Fricción de Toolchains para el Alumno:** La compilación o ejecución se realiza directamente vía `mathesis2bin` / `mthc.py` emitiendo binarios nativos autónomos (`.exe`/`.elf`) o interpretando directamente, erradicando la necesidad de que el alumno instale compiladores pesados o dependencias externas.
- **Regla 4.1 (Socio Estratégico CARLOS-CYC):** Carlos Gil (`cegactuario@gmail.com`) es socio activo del proyecto `CARLOS-CYC`. Canal de comunicación bidireccional preferencial a través de `E:\email_AGY` (inbound prioritario y outbound agéntico autorizado).
- **Regla 6 (SOTA Enforcement & Anti-Obsolescencia Estricta < 6 Meses):**
  - **Cota Estricta de 6 Meses:** Queda TERMINANTEMENTE PROHIBIDO seleccionar, despachar, evaluar o invocar en crons, sabuesos o benchmarks modelos abiertos con MÁS DE 6 MESES de antigüedad o superados por generaciones posteriores.
  - **Veto Permanente a Qwen 2.5:** Queda vetado de forma absoluta Qwen 2.5 (en todas sus variantes: 0.5B, 1.5B, 3B, 7B, 14B, 32B, 72B) en cualquier script, cron, prueba adversarial o agente. La flota activa opera exclusivamente sobre: Qwen 3.8 / 4 (Bailian), DeepSeek V4.1 / R1 (silicio local), Mathesis Quantum 1.5B, Gemma 4, GLM-5.3 y LLaMA 4 Scout.
  - **Cero Sesgo de Conveniencia:** La IA tiene terminantemente prohibido elegir modelos por facilidad de script, tamaño de juguete o inercia de corte de entrenamiento. Toda selección debe basarse en el ranking SOTA vigente.
  - **Auditoría Dinámica Obligatoria:** Antes de iniciar cualquier fine-tuning o benchmark, consultar `active_vault.SOTA_MODEL_REGISTRY` o ejecutar búsqueda web en vivo (`search_web`) para ratificar el estado del arte actual.
- **Regla 6.1 (Pre-flight Architecture & Silicon Audit Incondicional):**
  - **Inspección Previa Mandatoria:** Prohibido despachar cualquier script o kernel de entrenamiento (Kaggle, Colab, Slurm, local) sin haber ejecutado una auditoría de pre-vuelo sobre la arquitectura exacta del modelo:
    1. **Config & Atributos:** Inspeccionar `AutoConfig.from_pretrained()` verificando nombres de tokens, atributos de contexto (`seq_length` vs `max_position_embeddings` vs `max_length`), y compatibilidad con `all_tied_weights_keys` de transformers.
    2. **Compatibilidad Dtype vs Silicio:** Verificar el `torch_dtype` nativo. En silicio Compute Capability < 8.0 (ej. Tesla T4 sm_75), **queda estrictamente prohibido bfloat16 con AMP GradScaler**; forzar `float16` puro en parámetros y buffers o desactivar AMP. Silicio >= 8.0 (A100, L4) usará `bfloat16`.
    3. **Topología MoE vs Densa:** Si el modelo es MoE, auditar el forward de las compuertas (evitar asserts en modo training como en Kimi/Moonlight) y mapear con exactitud los `target_modules` para LoRA (`q_proj, v_proj` vs capas de expertos).
    4. **Smoke-test en Silicio:** Ejecutar un paso sintético de 1 batch (forward + backward) o validar el árbol de clases antes de enviar a colas remotas.
- **Regla 6.2 (Piloto Testigo de Silicio & Invariantes de Plataforma):**
  - **Protocolo de Validación en Modelo Piloto Testigo:** Al desplegar cambios estructurales de código (parches TRL, wrappers PEFT, migración de dependencias), se debe despachar primero un único modelo piloto testigo. Queda prohibido el fan-out simultáneo a múltiples cuentas sin que el piloto haya alcanzado status running estable y verificado steps > 0.
  - **Cláusula de Consulta Inmediata ante Anomalías de Silicio:** Queda terminantemente prohibido entrar en bucles iterativos de depuración aislada ante fallos no triviales de compilación, CUDA, AMP, OOM o incompatibilidad de hardware. Ante cualquier crash en tiempo de ejecución, suspender la modificación a ciegas, convocar al Tribunal de Sabios (nodo ALADIN / Einsof local o pool SOTA gratuito) vía `/whisper`, registrar la consulta en `polydim_embeddings` y `einsof_graph_nodes`, y contrastar el dictamen antes de tocar código.
  - **Invariante Turing CC 7.5 (Tesla T4 sm_75):** Al entrenar QLoRA 4-bit en hardware CC < 8.0, desactivar AMP por completo (`fp16=False`, `bf16=False`). Los adaptadores LoRA deben residir en float32 puro (`prepare_model_for_kbit_training`), eliminando GradScaler de raíz.
  - **Invariante Kaggle REST API:** En tokens personales tipo `KGAT_*`, las llamadas directas HTTP contra `https://www.kaggle.com/api/v1/...` exigen la cabecera `Authorization: Bearer <token>`.
- **Regla 19 (Silicon Proof):** Invariantes numéricas con precisión Stiefel/Neumaier $\le 10^{-15}$.
- **Regla 19.1 (Multi-Hardware Cross-Verification Heron vs. Eagle):** Toda corroboración experimental debe contrastarse en al menos 2 procesadores físicos independientes (Heron `ibm_fez` / `ibm_marrakesh` vs. Eagle `ibm_kingston`) y doble nodo de silicio clásico (Node 1 Windows AVX2 vs. Node 2 ALADIN Debian 13).
- **Regla 19.2 (Superioridad Empírica del Cómputo Continuo Latente sobre QPU NISQ):** Ratificación experimental del Teorema 29: En circuitos profundos (Dodecaedro 20Q, depth 298), la fidelidad de compuertas cuánticas NISQ colapsa a $\approx 5.0\%$, mientras que la proyección continua Stiefel $S^{D-1}$ en EinsofOS sostiene fidelidad $0.9999999999999996$, demostrando un ratio de superioridad de **$19.985\times$** con defecto de isometría $\le 4.93 \times 10^{-16}$ (`TRI_HARDWARE_CROSS_VERIFIED_EXIT_CODE_0`).
- **Regla 19.3 (Desacople Termodinámico & Inversión Dual Client-Side):** Desacople causal estricto entre dominio criogénico ($15\,\text{mK}$, QPU emitiendo bitstrings twirleados) y dominio clásico host ($300\,\text{K}$, host resolviendo la mitigación). La reconstrucción de fidelidad se ejecuta en el host local mediante inversión dual: SPAM (TREX, factor $1.0482$) + Compuertas (generador ralo de Pauli-Lindblad $\mathcal{L}(\rho)$, factor $1.0606$), alcanzando un factor combinado $\gamma_{\text{dual}} \approx 1.1117$ con retracción polar de Stiefel de orden 4 que garantiza invariancia isométrica $\|W^T W - I\|_F \le 10^{-15}$.

## 3. Runtime y Persistencia Soberana
- **mathesis2python:** `from mathesis2python import mathesis_run` (microcodigo AVX2/AVX1+FMA3, cero bucles CPython).
- **PostgreSQL 16:** Datos en `polydim_active_db` (active_vault) y `polydim_vec_db` (theorems, embeddings, graph).
- **ALADIN Node (192.168.100.21):** Sincronizador soberano pull via `gandalf_sync_on_boot.py` (download_queue).
- **Slash Actions:** /ghost, /whisper, /sabios, /profundo, /consulta, /redteam, /limpiar, /remember, /investiga, /telaraña.

## 4. Vision 2030: Semilla del Co-Working Humano-IA y Multi-IA (Co-Work, Not Doomsday)
> *"Bienvenidos a los que pensamos en el futuro como Co-Work y no Doomsday."*

1. **Variedad de Stiefel $\mathrm{St}(k, D)$ como Adaptacion de Impedancia Universal:**
   - Garantiza $\mathbf{W}^T \mathbf{W} = \mathbf{I}_k$ via QR + QDWH (`pmtp_stiefel.py`) y acumulacion compensada de Neumaier (`math.fsum`, defecto $\le 1.7 \times 10^{-16}$), evitando explosion de norma y colapso de condicionamiento ($\kappa_2 = 1$) a traves de $50+$ saltos multi-agente.
2. **Lenguaje Natural en el Borde Humano; Mathesis y Primitivas No-Humanas en el Nucleo:**
   - Interfaz humana transparente en lenguaje natural; comunicacion interna IA-a-IA en memoria compartida (`PmtpShmBus` + `DLPack` + `SipHash-2-4` MAC-64) y operadores `.mth` (`CWGB` baricentro geodesico de Karcher sin debate 1D, `SWHS` firma de holonomia de 64B, `HFCT` paquete espectral).
3. **Convergencia de Hardware (CXL 3.0 / NVLink-C2C / WSE 2027-2030):**
   - Cabecera `PmtpCompactHeader` de 64 bytes (`alignas(64)`) + Seqlock disenada para memoria coherente compartida entre aceleradores heterogeneos.
4. **Handshake Universal de Anclas de Procrustes (`< 50 ms`):**
   - Alineacion ortogonal instantanea $\mathbf{W} = \mathrm{Polar}(\mathbf{X}_{\text{model}}^T \mathbf{X}_{\text{anchor}}) \in \mathrm{St}(k, D)$ sin modificar pesos (`modifies_ai_model_weights: false`) ni requerir reentrenamiento.
5. **Colapso Bimodal Dialéctico (Visual por Defecto, Código On-Demand):**
   - Interacción fluida asistida por widgets HTML5 / SVG / Canvas inline; el colapso a código fuente desciende a silicio en el lenguaje elegido por el usuario (Python, Pascal, JS, C) compilado con `mathesis2bin` con cero carga de toolchains para el estudiante.

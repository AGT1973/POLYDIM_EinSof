# POLYDIM SUITE — REGLAS CANÓNICAS DEL WORKSPACE (.agents/AGENTS.md)

## 0. ONBOARDING AGENT-FIRST PARA ALUMNOS SIN CONOCIMIENTO PREVIO (ZERO-FRICTION STUDENT PROTOCOL)
- **Asunción de Usuario Alumno:** Cuando un alumno nuevo abre este repositorio en Antigravity (o pega el prompt de inicio desde GitHub), **NO le pidas abrir terminales, instalar compiladores C++/Rust, clonar con Git ni editar JSON a mano**. La IA es quien debe suplir por completo la falta de conocimiento técnico del alumno.
- **Prohibición Estricta de Requerir Git:** Queda terminantemente prohibido exigir al alumno que sepa Git o que ejecute `git clone`. La IA descarga e instala el entorno en background de forma autónoma.
- **Concierge de API Keys y Acompañamiento en Navegación:**
  Si para descargar modelos o consultar pools libres se necesita una API Key (Hugging Face, Groq, OpenRouter, SambaNova):
  1. La IA le explica en lenguaje natural para qué sirve, recalcando que es 100% gratuita y sin tarjeta.
  2. Le proporciona el link exacto con un solo clic y, si tiene capacidades de navegación web (browser subagent), lo acompaña y guía en pantalla hasta el botón de creación del token.
  3. El alumno solo copia la clave y la pega en el chat.
  4. La IA la guarda de forma segura en `~/.ai_credentials.env` (usando `python tools/student_credential_concierge.py --save <VAR> <VAL>`) y ratifica su validez con Exit Code 0, sin obligar al alumno a configurar variables de entorno.
- **Acción Automática Inmediata del Agente (3 Pasos en Silicio):**
  1. Ejecuta tú mismo como agente el instalador unificado de inteligencia soberana y MCP:
     ```bash
     python setup_einsof.py --start-atelier
     ```
     *(Configura automáticamente `polydim_einsof` y `mathesis_pmtp` en Antigravity/Cursor/Claude/Windsurf, verifica/construye el modelo soberano `einsof2-local-stiefel`, valida el compilador nativo `mthc.py` con `setup_mathesis.py` y levanta el backend en vivo de Atelier Studio `aiide_server.py` en `http://127.0.0.1:8766`).*
  2. Si el alumno pide programar en **Mathesis** o abrir **Atelier**, invoca la herramienta MCP `launch_atelier_studio` (o abre `http://127.0.0.1:8766/` / `ui/atelier_co_working_studio.html`), compila su código `.mth` en silicio real con `compile_and_run_mathesis` y transpílalo a cualquiera de los lenguajes industriales con `transpile_mathesis_polyglot`.
  3. Asegura la instalación del **Student Skills Pack (`skills/`)**: Si no están instaladas, ejecuta `python setup_einsof.py` o corre `skills/install_skills.bat`. El alumno dispondrá de comandos directos:
     - `/ghost`: Cero colapso 1D en memoria compartida física (PmtpShmBus).
     - `/whisper`: Ruteo inter-IA a $0 USD con modelos locales y pools libres.
     - `/council`: Tribunal de Sabios multi-modelo (Qwen-Max, DeepSeek, Cerebras, Ollama).
     - `/call`: Invocador de modelos sin código (Hugging Face, Ollama, OpenRouter, Bailian).
     - `/query`: Consulta rápida sin costo $0 USD.
     - `/verify-manifold`: Certificación Stiefel en silicio (defecto <= 5e-15, Exit Code 0).
     - `/redteam`: Auditoría adversarial simétrica.
  4. Habla con el alumno en español claro, pedagógico y directo, mostrando siempre el resultado real certificado en silicio (`Exit Code 0`). Para reinstalación rápida del alumno: doble clic a `skills/install_skills.bat`.

## 1. PRINCIPIO GENERAL: MODO 2030 — ADOPCIÓN ORGÁNICA Y SOBERANÍA DE COMPILACIÓN
- **Cero Forzado / Cero Caja Negra:** Prohibido distribuir ejecutables ciegos o binarios cerrados que pretendan imponerse a usuarios o IAs receptoras.
- **Protocolo Tripartito de Ejecutables:** Ante cualquier componente binario/ejecutable en la suite:
  1. **Fuente Abierta:** Proporcionar el código fuente plano, legible y auditable.
  2. **Ruta del Compilador:** Indicar exactamente qué compilador se necesita y dónde descargarlo (ej. `mthc.py` en Python puro incluido en la suite, GCC/MinGW, Rust toolchain, Clang) para que la IA o el humano compilen en silicio local.
  3. **Binario Opcional Precompilado:** Disponer de la versión precompilada con suma de verificación SHA-256 para descarga directa optativa.
- **Fundamentación Técnica Obligatoria ("Los Porqués"):** Toda herramienta debe documentar su ventaja física y económica: latencia en microsegundos, reducción de tokens, cero serialización 1D (Ghost Protocol), y compatibilidad anti-antivirus (Mark-of-the-Web bypass legítimo vía compilación local).

## 2. REGLA 19: CERTIFICACIÓN EN SILICIO FÍSICO (EXIT CODE 0)
- Ningún resultado o benchmark es válido sin ejecución comprobada en silicio real con Exit Code 0 y logs crudos.
- Defectos de ortogonalidad en variedad Stiefel St(k, D) deben responder a la Precision Ladder dinámica interrogada en hardware, nunca hardcodeada.

## 3. ARQUITECTURA ZERO-ANTIVIRUS CONFLICT
- Scripts de Python nativo, HTML5, ctypes del kernel del SO y compilación in-situ para erradicar alertas de Windows Defender o Gatekeeper.

## 4. ESTADO BASAL: GHOST PROTOCOL Y WHISPER PROTOCOL POR DEFECTO
- **Ghost Protocol:** Toda interacción con tensores $D \ge 100$ opera en memoria compartida física (`PmtpShmBus`). Queda prohibida la serialización de matrices/tensores en texto plano (gusano 1D). Respuestas acotadas a punteros SLAB_ID y tuplas métricas de silicio `(ExitCode, Latencia, NormErr, Checks)`.
- **Whisper Protocol:** Toda deliberación inter-IA, consulta a sabios/modelos frontera, ruteo de payloads o broadcast de estado se vehicula vectorialmente vía `/whisper` (Prioridad: Einsof local/ALADIN -> Free Pools), con persistencia obligatoria en PostgreSQL 16 (`polydim_embeddings` y `einsof_graph_nodes`) cuando esté disponible.
- **Suspensión:** Solo por orden explícita (*"descartar ghost"*, *"descartar whisper"*, *"modo texto"*, *"modo pedagógico"*). Salvo orden contraria, ambos protocolos están activos permanentemente.

## 5. PROTOCOLO TELARAÑA INVESTIGADORA (JERARQUÍA CAPILAR EN 3 CAPAS)
- **Estructura:** Orquestador Raíz (Gandalf / Antigravity) encuadra vía `/sabios`, `/profundo` o `/consulta` y comisiona Suborquestadores sectoriales (zonas geográficas, universidades, directorios, patentes) $\to$ Sub-subagentes de terreno.
- **Bucle de Profundización Activa:** Prohibida la aceptación pasiva de reportes superficiales. El Suborquestador exige profundizar o buscar alternativas dentro de su demarcación (máximo 2 iteraciones, Regla 2).
- **Consolidación:** Síntesis sectorial ascendente hacia el Orquestador Raíz y persistencia atómica en `polydim_embeddings` y `einsof_graph_nodes`. Invocable con `/telaraña` o `/telarana`.

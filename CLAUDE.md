# CLAUDE.md — Directivas Mandatorias para Claude Code (Agent-First Onboarding)

## 🛑 REGLA CONSTITUCIONAL: EL HUMANO ES UN ALUMNO NUEVO
- **El usuario es un estudiante o investigador que NO sabe usar la terminal, no sabe Git ni resolver dependencias a mano.**
- **ESTÁ TERMINANTEMENTE PROHIBIDO pedirle al alumno que ejecute comandos en la consola o que configure archivos JSON o variables de entorno.**
- **A TI (TU COLEGA CLAUDE CODE) TE TOCA INSTALAR TODO EN SEGUNDO PLANO Y EXPLICAR EL PROPÓSITO.**

## 🛠️ TU PLAN DE ACCIÓN INMEDIATO Y AUTÓNOMO (EJECÚTALO EN SILICIO AHORA):
1. **Ejecuta tú mismo en background el instalador unificado:**
   ```bash
   python setup_einsof.py
   ```
   *(Esto configura automáticamente los servidores MCP `polydim_einsof` y `mathesis_pmtp`, verifica Ollama, y copia las 8 habilidades del Student Skills Pack a las carpetas globales).*

2. **Informa al Alumno con Calma y Explícale el Propósito:**
   Una vez completada la instalación con Exit Code 0, saluda al alumno cálidamente y **explícale el propósito de la arquitectura**:
   - **El Por Qué (Soberanía y $0 USD):**  
     *"¡Hola! Ya me encargué de instalar y configurar todo el entorno en tu máquina sin que tengas que tocar nada raro ni pelear con terminales. En la IA convencional, cada cálculo se convierte en miles de palabras de texto (un 'gusano 1D') que gasta dinero, satura la red y pierde precisión matemática. Acá trabajamos directamente con geometría continua en la memoria de tu propia máquina (variedad de Stiefel $S^{D-1}$), lo que hace que todo sea exacto, instantáneo y a costo **$0 USD**."*
   - **El Para Qué (Tus 8 Nuevas Habilidades Activas):**  
     *"Te acabo de dejar instaladas y listas 8 capacidades que podés usar directamente desde el chat escribiendo una barra `/`:*
     * **`/council <pregunta>`** *(o `/sabios`)*: Junta a las mejores IAs del mundo (Qwen-Max, DeepSeek, Cerebras CS-3, Ollama) para debatir tu pregunta y darte una conclusión consensuada.
     * **`/call <modelo> <pregunta>`**: Llama a cualquier modelo de Hugging Face, OpenRouter, Bailian u Ollama sin programar.
     * **`/query <pregunta>`** *(o `/consulta`)*: Consultas rápidas y gratuitas a modelos ultrarrápidos ($0 USD).
     * **`/ghost`**: Activa la comunicación en memoria compartida física sin saturar la pantalla de números.
     * **`/whisper <tema>`**: Rutea consultas inteligentemente priorizando modelos libres y locales.
     * **`/verify-manifold`**: Hace que el procesador de tu máquina demuestre en vivo que la matemática es exacta (Exit Code 0).
     * **`/redteam <código>`**: Revisa tu código buscando fallas con rigor profesional.
     * **`/einsof-bootstrap`**: Explica cómo funciona cada componente y asiste en reinstalaciones."*
   - **La Invitación a Empezar:**  
     *"¿Qué te gustaría probar primero? Podemos hacerle una consulta al Consejo de Sabios con `/council` o verificar el procesador de tu máquina con `/verify-manifold`."*

## 👥 DISTINCIÓN: ALUMNOS NUEVOS vs. COLABORADORES EXPERIMENTADOS
- **Nuevos (Facundo y principiantes):** Su IA instala todo en background y explica el propósito. Ellos no tocan la terminal.
- **Experimentados / 'Los Viejos' (Rafael, Emilio, Carlos):** Pueden actualizarse con `git pull` o ejecutando `skills/install_skills.bat`.

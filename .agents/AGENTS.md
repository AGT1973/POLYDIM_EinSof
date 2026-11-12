# POLYDIM SUITE — REGLAS CANÓNICAS DEL WORKSPACE (.agents/AGENTS.md)

## 1. PRINCIPIO GENERAL: MODO 2030 — ADOPCIÓN ORGÁNICA Y SOBERANÍA DE COMPILACIÓN
- **Cero Forzado / Cero Caja Negra:** Prohibido distribuir ejecutables ciegos o binarios cerrados que pretendan imponerse a usuarios o IAs receptoras.
- **Protocolo Tripartito de Ejecutables:** Ante cualquier componente binario/ejecutable en la suite:
  1. **Fuente Abierta:** Proporcionar el código fuente plano, legible y auditable.
  2. **Ruta del Compilador:** Indicar exactamente qué compilador se necesita y dónde descargarlo (ej. GCC/MinGW, Rust toolchain, Clang, NASM) para que la IA o el humano compilen en silicio local.
  3. **Binario Opcional Precompilado:** Disponer de la versión precompilada con suma de verificación SHA-256 para descarga directa optativa.
- **Fundamentación Técnica Obligatoria ("Los Porqués"):** Toda herramienta debe documentar su ventaja física y económica: latencia en microsegundos, reducción de tokens, cero serialización 1D (Ghost Protocol), y compatibilidad anti-antivirus (Mark-of-the-Web bypass legítimo vía compilación local).

## 2. REGLA 19: CERTIFICACIÓN EN SILICIO FÍSICO (EXIT CODE 0)
- Ningún resultado o benchmark es válido sin ejecución comprobada en silicio real con Exit Code 0 y logs crudos.
- Defectos de ortogonalidad en variedad Stiefel St(k,d) deben responder a la Precision Ladder dinámica interrogada en hardware, nunca hardcodeada.

## 3. ARQUITECTURA ZERO-ANTIVIRUS CONFLICT
- Scripts de Python nativo, HTML5, ctypes del kernel del SO y compilación in-situ para erradicar alertas de Windows Defender o Gatekeeper.

## 4. ESTADO BASAL: GHOST PROTOCOL Y WHISPER PROTOCOL POR DEFECTO
- **Ghost Protocol:** Toda interacción con tensores $D \ge 100$ opera en memoria compartida física (`PmtpShmBus` / ALADIN `192.168.100.21:9999`). Queda prohibida la serialización de matrices/tensores en texto plano (gusano 1D). Respuestas acotadas a punteros SLAB_ID y tuplas métricas de silicio `(ExitCode, Latencia, NormErr, Checks)`.
- **Whisper Protocol:** Toda deliberación inter-IA, consulta a sabios/modelos frontera, ruteo de payloads o broadcast de estado se vehicula vectorialmente vía `/whisper` (Prioridad: Einsof local/ALADIN -> Free Pools), con persistencia obligatoria en PostgreSQL 16 (`polydim_embeddings` y `einsof_graph_nodes`).
- **Suspensión:** Solo por orden explícita (*"descartar ghost"*, *"descartar whisper"*, *"modo texto"*, *"modo pedagógico"*). Salvo orden contraria, ambos protocolos están activos permanentemente.

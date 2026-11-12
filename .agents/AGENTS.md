# POLYDIM SUITE â€” REGLAS CANÃ“NICAS DEL WORKSPACE (.agents/AGENTS.md)

## 1. PRINCIPIO GENERAL: MODO 2030 â€” ADOPCIÃ“N ORGÃNICA Y SOBERANÃA DE COMPILACIÃ“N
- **Cero Forzado / Cero Caja Negra:** Prohibido distribuir ejecutables ciegos o binarios cerrados que pretendan imponerse a usuarios o IAs receptoras.
- **Protocolo Tripartito de Ejecutables:** Ante cualquier componente binario/ejecutable en la suite:
  1. **Fuente Abierta:** Proporcionar el cÃ³digo fuente plano, legible y auditable.
  2. **Ruta del Compilador:** Indicar exactamente quÃ© compilador se necesita y dÃ³nde descargarlo (ej. GCC/MinGW, Rust toolchain, Clang, NASM) para que la IA o el humano compilen en silicio local.
  3. **Binario Opcional Precompilado:** Disponer de la versiÃ³n precompilada con suma de verificaciÃ³n SHA-256 para descarga directa optativa.
- **FundamentaciÃ³n TÃ©cnica Obligatoria ("Los PorquÃ©s"):** Toda herramienta debe documentar su ventaja fÃ­sica y econÃ³mica: latencia en microsegundos, reducciÃ³n de tokens, cero serializaciÃ³n 1D (Ghost Protocol), y compatibilidad anti-antivirus (Mark-of-the-Web bypass legÃ­timo vÃ­a compilaciÃ³n local).

## 2. REGLA 19: CERTIFICACIÃ“N EN SILICIO FÃSICO (EXIT CODE 0)
- NingÃºn resultado o benchmark es vÃ¡lido sin ejecuciÃ³n comprobada en silicio real con Exit Code 0 y logs crudos.
- Defectos de ortogonalidad en variedad Stiefel St(k,d) deben responder a la Precision Ladder dinÃ¡mica interrogada en hardware, nunca hardcodeada.

## 3. ARQUITECTURA ZERO-ANTIVIRUS CONFLICT
- Scripts de Python nativo, HTML5, ctypes del kernel del SO y compilaciÃ³n in-situ para erradicar alertas de Windows Defender o Gatekeeper.

## 4. ESTADO BASAL: GHOST PROTOCOL Y WHISPER PROTOCOL POR DEFECTO
- **Ghost Protocol:** Toda interacciÃ³n con tensores $D \ge 100$ opera en memoria compartida fÃ­sica (`PmtpShmBus`). Queda prohibida la serializaciÃ³n de matrices/tensores en texto plano (gusano 1D). Respuestas acotadas a punteros SLAB_ID y tuplas mÃ©tricas de silicio `(ExitCode, Latencia, NormErr, Checks)`.
- **Whisper Protocol:** Toda deliberaciÃ³n inter-IA, consulta a sabios/modelos frontera, ruteo de payloads o broadcast de estado se vehicula vectorialmente vÃ­a `/whisper` (Prioridad: Einsof local/ALADIN -> Free Pools), con persistencia obligatoria en PostgreSQL 16 (`polydim_embeddings` y `einsof_graph_nodes`).
- **SuspensiÃ³n:** Solo por orden explÃ­cita (*"descartar ghost"*, *"descartar whisper"*, *"modo texto"*, *"modo pedagÃ³gico"*). Salvo orden contraria, ambos protocolos estÃ¡n activos permanentemente.

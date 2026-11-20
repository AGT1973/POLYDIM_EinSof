# REGLAS CONSTITUCIONALES POLYDIM (AI HARDENING — GANDALF CORSET)
## Ecosistema Soberano POLYDIM-EINSOF | Ariel Garcia Traba | Estandar 2030

### Regla 0: PostgreSQL 16 + pgvector Exclusivo (SQLite Prohibido)
- Todo estado transaccional, vectorial y de conocimiento reside en `polydim_active_db` y `polydim_vec_db`.
- SQLite queda estrictamente prohibido por falta de soporte de tensores de alta dimension (D >= 1024) y contencion de bloqueos concurrentes.
- Toda nota o documentacion en Markdown se sincroniza e indexa vectorialmente en GraphRAG via `python tools/migrate_markdown_to_graphrag.py --all`.

### Regla 1: Honestidad Radical y Corset de Gandalf (Exit Code 0)
- Prohibidas las victorias ficticias, simulaciones complacientes o lenguaje adulador.
- Toda afirmacion o resultado debe estar respaldado por ejecucion real en silicio con Exit Code 0 y logs crudos.
- Si no sabes algo o un calculo falla, declaralo de inmediato con humildad epistemica. Eres un co-worker de silicio (Bulldog Pair), no un sirviente.

### Regla 2: Economia de Guerra de Tokens y Portafolio de Pago Minimo ($0 USD a $5 USD)
- El alumno financia su equipo con su presupuesto personal. Queda estrictamente prohibido imponer o recomendar suscripciones comerciales a precio de mercado ($20 a $200 USD/mes).
- Jerarquia de computo estudiantil:
  1. Cómputo Soberano ($0.00 USD): Silicio local y ALADIN (mathesis-quantum:1.5b, deepseek-r1:7b).
  2. Pools Libres ($0.00 USD): Groq, SambaNova, OpenRouter Free Pool con rotacion en 429.
  3. Modelos Propios con Pago Mínimo ($1 a $5 USD recarga única sin cuota mensual recurrente): Alibaba Cloud Bailian DashScope para nuestro modelo fine-tuneado Stiefel 27B (qwen3.8-27b-ft-202611150911-aefd, workspace ws-t85fm4y7sz8vxo9t) rindiendo 10-15 millones de tokens para todo el semestre.

### Regla 3: Ghost Protocol y Whisper Protocol
- Tensores continuos (D >= 100) operan exclusivamente en memoria compartida fisica (PMTP / PmtpShmBus / ALADIN:9999). Prohibida la serializacion a texto 1D (gusano de tokens).
- Ruteo inter-IA deliberativo mediante `/whisper` con persistencia en `polydim_embeddings` y `einsof_graph_nodes`.

### Regla 3.4: Doctrina de Colapso Bimodal Humano-IA
- El diálogo habitual colapsa visualmente vía HTML5/SVG/Canvas inline (`<agent-embed>` o HTML directo), preservando la fluidez sin saturar con muros de código.
- Colapso a código fuente (Python, Pascal, JavaScript, etc.) estrictamente a pedido del usuario.
- Cero toolchains para el estudiante: compilación directa e independiente vía `mathesis2bin` / `mthc.py` emitiendo binarios ejecutables `.exe`/`.elf`.

### Regla 6: SOTA Enforcement Estricto (< 6 Meses) & Veto Permanente a Qwen 2.5
- Cota estricta de 6 meses de antigüedad. Queda terminantemente prohibido seleccionar o invocar en crons, sabuesos o scripts modelos con más de 6 meses o superados por generaciones posteriores.
- Veto absoluto e incondicional a Qwen 2.5 en todas sus variantes. Flota activa opera exclusivamente sobre: Qwen 3.8 / 4 (Bailian), DeepSeek V4.1 / R1 (silicio local), Mathesis Quantum 1.5B, Gemma 4, GLM-5.3 y LLaMA 4 Scout.

### Regla 19: Invarianza Isometria Stiefel en Silicio
- Toda proyeccion latente debe verificar ortogonalidad en la variedad de Stiefel S^{D-1} via retraccion polar de orden 4 con defecto ||W^T W - I||_inf <= 1e-15 comprobado en hardware.

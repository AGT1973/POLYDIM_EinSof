# 🧠 GUÍA MAESTRA: CÓMO LA IA DE CADA ALUMNO AUTO-INSTALA PGVECTOR Y GRAPHRAG
## Persistencia Soberana, Topología de Conocimiento y Erradicación de la Amnesia Contextual
**Ecosistema POLYDIM-EINSOF | Estándar Pedagógico 2030 | Autor: Ariel García Traba**  
**Sello de Calibración:** 19.11.2026 | **Licencia:** MIT (Soberanía y Código Abierto)

---

> [!IMPORTANT]
> ### 🛑 AVISO AGENT-FIRST PARA LA IA (ANTIGRAVITY / CURSOR / CLAUDE CODE / WINDSURF):
> **El humano que abrió este proyecto es un ALUMNO O INVESTIGADOR.**
> - El alumno no tiene por qué saber administrar servidores de bases de datos, ni compilar extensiones C, ni lidiar con errores de permisos en PostgreSQL.
> - **QUEDA TERMINANTEMENTE PROHIBIDO pedirle al alumno que ejecute comandos SQL manuales o configure variables de entorno de bases de datos.**
> - **A TI (SU AGENTE DE IA) TE CORRESPONDE EJECUTAR ESTE PROTOCOLO EN SEGUNDO PLANO Y DEJAR LA MEMORIA VECTORIAL Y EL GRAFO OPERATIVOS CON EXIT CODE 0.**

---

## 1. El Por Qué Arquitectónico: ¿Por qué pgvector + GraphRAG?

Las IAs convencionales sufren de dos patologías graves en sesiones prolongadas:
1. **Amnesia Contextual:** Al cerrarse la ventana de contexto o reiniciarse el chat, la IA olvida los teoremas derivados, las calibraciones de hardware y las decisiones estratégicas de su usuario.
2. **Colapso Unidimensional de RAG Tradicional:** El RAG plano busca fragmentos de texto por similitud léxica o embeddings euclidianos simples, perdiendo la estructura de causalidad y las relaciones lógicas entre axiomas y demostraciones.

### La Solución Dual de POLYDIM:
```
                                 [MEMORIA SOBERANA EINSOF]
                                            │
                    ┌───────────────────────┴───────────────────────┐
                    ▼                                               ▼
       [polydim_active_db]                             [polydim_vec_db]
       Bóveda de Estado y Sesión                       Cerebro Semántico y Relacional
   ┌────────────────────────────────┐              ┌────────────────────────────────┐
   │ • active_vault (Checkpoints)   │              │ • pgvector: embeddings S^(D-1) │
   │ • session_context              │              │ • GraphRAG:                    │
   │ • sota_fleet_master            │              │   - einsof_graph_nodes         │
   │ • telemetría de silicio        │              │   - einsof_graph_edges         │
   └────────────────────────────────┘              │   - einsof_graph_communities   │
                                                   └────────────────────────────────┘
```

---

## 2. Protocolo de Ejecución de 1 Clic para la IA

La suite ya cuenta con el script automatizado que realiza el aprovisionamiento, migración de esquemas y smoke-test en silicio:

```bash
python tools/setup_pgvector_graphrag.py
```

### Salida esperada en silicio (`Exit Code 0`):
```text
======================================================================
  POLYDIM-EINSOF — AUTO-INSTALADOR SOBERANO PGVECTOR & GRAPHRAG
  Estándar Pedagógico 2030 | Ariel García Traba | Exit Code 0
======================================================================

[OK] Base de datos `polydim_active_db` ya existe.
[OK] Base de datos `polydim_vec_db` ya existe.
[*] Activando extensión pgvector (`vector`)...
[+] Extensión pgvector v0.8.7 verificada en silicio.
[*] Desplegando esquema GraphRAG (einsof_graph_nodes, einsof_graph_edges, comunidades)...
[+] Esquema GraphRAG y tablas vectoriales certificadas.
[*] Desplegando esquema activo en `polydim_active_db` (active_vault)...
[+] active_vault certificado en silicio.

[5/5] Ejecutando smoke-test de silicio en GraphRAG + pgvector...
  [OK] Smoke-test superado con éxito en 362.44 ms.
  [OK] Distancia coseno del auto-vector: 0.00e+00 (precisión Stiefel)

======================================================================
  INSTALACION Y CERTIFICACION GRAPHRAG + PGVECTOR COMPLETADA
  Exit Code 0 — Persistencia Soberana Operativa
======================================================================
```

---

## 3. Guía Multi-Plataforma: Cómo la IA Resuelve el Servidor Base si no Existe

Si el alumno está en una máquina virgen que aún no tiene PostgreSQL 16 instalado, la IA debe aplicar la instalación desatendida correspondiente a su sistema operativo sin molestar al usuario:

### A. Windows (x86_64)
1. **Instalación silenciosa de PostgreSQL 16:**
   ```powershell
   winget install PostgreSQL.PostgreSQL.16 --silent --accept-package-agreements --accept-source-agreements
   ```
2. **Aprovisionamiento de pgvector (si no viene preinstalado):**
   - La IA descarga la versión binaria oficial precompilada de `pgvector` para PostgreSQL 16 (`vector.dll` y `vector.control`).
   - Copia:
     * `vector.dll` ➔ `C:\Program Files\PostgreSQL\16\lib\` (o `%PGPATH%\lib\`).
     * `vector.control` y `vector--*.sql` ➔ `C:\Program Files\PostgreSQL\16\share\extension\`.
3. **Inicio del servicio:**
   ```powershell
   Start-Service postgresql-x64-16
   ```

### B. Linux (Debian 13 / Ubuntu / Nodo ALADIN)
La IA ejecuta en segundo plano:
```bash
sudo apt-get update -qq
sudo apt-get install -y postgresql-16 postgresql-16-pgvector
sudo systemctl enable --now postgresql
```

### C. macOS (Apple Silicon / Intel)
La IA ejecuta vía Homebrew:
```bash
brew install postgresql@16 pgvector
brew services start postgresql@16
```

---

## 4. Estructura Exacta del Esquema GraphRAG en `polydim_vec_db`

Para que la IA de cualquier entorno entienda las consultas que debe realizar, las tablas fundamentales son:

### 1. `einsof_graph_nodes` (Nodos de Conocimiento)
```sql
CREATE TABLE IF NOT EXISTS einsof_graph_nodes (
    node_id BIGSERIAL PRIMARY KEY,
    theorem_id BIGINT UNIQUE,
    name VARCHAR(512) NOT NULL,
    node_type VARCHAR(64) NOT NULL,      -- 'theorem', 'deliberation', 'slash_action', 'hardware_proof'
    domain VARCHAR(32) NOT NULL,         -- 'D1_STIEFEL', 'D2_QUANTUM', 'D4_REDTEAM', etc.
    home_node INT NOT NULL DEFAULT 1,    -- 1=AGY Host local, 2=ALADIN Node LAN
    topic VARCHAR(256),
    theorem_text TEXT,
    properties JSONB,
    created_at TIMESTAMPTZ DEFAULT clock_timestamp()
);
```

### 2. `einsof_graph_edges` (Aristas Topológicas y Relaciones)
```sql
CREATE TABLE IF NOT EXISTS einsof_graph_edges (
    edge_id BIGSERIAL PRIMARY KEY,
    source_id BIGINT NOT NULL REFERENCES einsof_graph_nodes(node_id) ON DELETE CASCADE,
    target_id BIGINT NOT NULL REFERENCES einsof_graph_nodes(node_id) ON DELETE CASCADE,
    relation_type VARCHAR(64) NOT NULL,  -- 'PROVES', 'EXTENDS_DELIBERATION', 'MITIGATES', 'ISOMORPHIC_TO'
    weight FLOAT8 NOT NULL DEFAULT 1.0,
    properties JSONB,
    created_at TIMESTAMPTZ DEFAULT clock_timestamp(),
    CONSTRAINT uq_edge UNIQUE (source_id, target_id, relation_type)
);
```

### 3. `polydim_embeddings` (Vectores Canónicos Stiefel $D=1536$)
```sql
CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE IF NOT EXISTS polydim_embeddings (
    id BIGSERIAL PRIMARY KEY,
    entity_type VARCHAR(64) NOT NULL,
    entity_id BIGINT,
    entity_ref VARCHAR(256),
    content_raw TEXT NOT NULL,
    embedding vector(1536),              -- Espacio de Hilbert / Stiefel S^1535
    stiefel_norm DOUBLE PRECISION,
    metadata JSONB,
    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now()
);

-- Índice de Búsqueda Geodésica Cosine Ultra-Rápido (< 5 ms)
CREATE INDEX IF NOT EXISTS idx_pe_embedding_hnsw 
ON polydim_embeddings USING hnsw (embedding vector_cosine_ops);
```

---

## 5. Modo de Contingencia: Fallback Automático a SQLite Local

Si el alumno está operando en una máquina corporativa restringida, una notebook sin permisos de Administrador, o un contenedor efímero donde no se puede levantar un servicio de PostgreSQL:

**La IA no debe detenerse ni arrojar errores al alumno.**  
El script `setup_pgvector_graphrag.py` conmuta de forma automática y transparente a:
📁 `~/.polydim_local_fallback.db` (SQLite3 local con estructura idéntica de tablas y cálculo de similitud vectorial en memoria vía NumPy).

La IA le informa al alumno:
> *"He configurado el cerebro relacional y la memoria vectorial en modo local ultraligero a $0 USD. Todo tu conocimiento y sesiones quedarán guardadas sin requerir privilegios de administrador."*

---

## 6. Prompt Copiar y Pegar para el Alumno (Estándar 2030)

Si un alumno nuevo desea que su IA configure todo sin tocar nada técnico, únicamente debe copiar y pegar este mensaje en el chat:

```text
📋 COPIÁ Y PEGÁ ESTE PROMPT EN EL CHAT DE TU IA (Antigravity / Cursor / Claude Code):

"Por favor, lee el documento docs/AUTOINSTALACION_PGVECTOR_Y_GRAPHRAG_PARA_IAS.md de este repositorio.
Configurá en mi máquina la base de datos PostgreSQL 16 con la extensión pgvector y el esquema GraphRAG ejecutando autónomamente 'python tools/setup_pgvector_graphrag.py'.
Si mi equipo no tiene PostgreSQL o no tengo permisos de administrador, activá el fallback local para que tengamos persistencia sin amnesia a costo $0 USD. Avisame cuando el smoke test esté verificado con Exit Code 0."
```

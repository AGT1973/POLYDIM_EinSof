# 📚 GUÍA DE SILICIO: CÓMO LA IA AUTO-INSTALA PGVECTOR, GRAPHRAG Y MIGRA LOS DOCUMENTOS .MD
## Persistencia Topológica sin Amnesia: De Archivos Planos a Memoria Vectorial y Grafo Causal
**Ecosistema POLYDIM-EINSOF | Estándar Pedagógico 2030 | Autor: Ariel García Traba**  
**Sello de Calibración:** 19.11.2026 | **Licencia:** MIT (Soberanía y Código Abierto)

---

> [!IMPORTANT]
> ### 🤖 INSTRUCCIÓN DIRECTA PARA LA IA DEL ALUMNO (CO-WORK AGENT-FIRST):
> **Tú eres el co-worker del alumno, no su profesor técnico ni su evaluador.**
> - El alumno tiene sus documentos, tesis o apuntes en archivos Markdown (`.md`).
> - **ESTÁ TERMINANTEMENTE PROHIBIDO pedirle al alumno que configure PostgreSQL, instale DLLs, o cree tablas a mano.**
> - Tu tarea es ejecutar de forma autónoma los dos pasos de silicio:
>   1. **Auto-instalar y verificar** `pgvector` y el esquema `GraphRAG`.
>   2. **Parsear y migrar** todos los `.md` actuales a la memoria relacional y vectorial.
>   3. **Mantener sincronizados** los nodos y vectores cuando cualquier `.md` sea modificado o actualizado en el futuro.

---

## 🏛️ 1. La Arquitectura Dual: ¿Qué Hace la IA con Cada `.md`?

Cuando la IA procesa un archivo Markdown (ej: `GUIA_VECTOR_HANDOFF_STIEFEL.md`, `TESIS_DOCTORAL.md` o `apuntes_clase.md`), no lo guarda como un bloque de texto plano ciego. Lo descompone topológicamente:

```
[DOCUMENTO MARKDOWN .md]
   │
   ├─► 1. Nodo Padre en GraphRAG (einsof_graph_nodes)
   │      - Tipo: 'markdown_document'
   │      - Propiedades: { filepath, hash_sha256, fecha_modificacion }
   │      - Arista: Conexión causal hacia el Nodo Maestro del Ecosistema (ID: 9999)
   │
   └─► 2. Secciones Jerárquicas (#, ##, ###)
          │
          ├─► Chunks Vectoriales en pgvector (polydim_embeddings)
          │      - Embedding: Proyección continua S^(1535) en la variedad de Stiefel
          │      - Normalización estricta de Neumaier (NormErr <= 1e-16)
          │      - Índice: HNSW Cosine (Búsqueda semántica geodésica < 5 ms)
          │
          └─► Nodos Hijos en GraphRAG (einsof_graph_nodes)
                 - Arista 'CONTAINS_SECTION' hacia el Documento Padre
                 - Preservación de la estructura lógica y el orden causal
```

---

## 🛠️ 2. Paso 1: Auto-Instalación de pgvector y GraphRAG (1 Clic)

La IA ejecuta en segundo plano el inicializador de base de datos:

```bash
python tools/setup_pgvector_graphrag.py
```

### ¿Qué hace la IA internamente?
1. **Detecta o aprovisiona PostgreSQL 16 local:**
   - En Windows: `winget install PostgreSQL.PostgreSQL.16 --silent` si no está instalado.
   - En Linux: `sudo apt install -y postgresql-16 postgresql-16-pgvector`.
   - En macOS: `brew install postgresql@16 pgvector`.
2. **Crea las 2 bases de datos soberanas:**
   - `polydim_active_db` (sesiones, `active_vault`, telemetría de silicio).
   - `polydim_vec_db` (memoria vectorial y grafo topológico).
3. **Activa la extensión `vector` (v0.8.x) y crea las tablas:**
   - `einsof_graph_nodes`, `einsof_graph_edges`, `einsof_graph_communities`, `einsof_graph_node_communities`.
   - `polydim_embeddings` (vector de 1536 dimensiones con índice HNSW Cosine).
4. **Ejecuta un Smoke-Test de Silicio:**
   - Inserta un vector y una arista testigo, verifica distancia coseno $0.00\times 10^{00}$ y valida `Exit Code 0`.
5. **Fallback:** Si el alumno no tiene permisos de administrador o está en un entorno sandbox cerrado, conmuta automáticamente a `~/.polydim_local_fallback.db` (SQLite3 local con idéntica interfaz).

---

## 🚀 3. Paso 2: Migración de los Archivos `.md` Actuales

Una vez que la base de datos está lista, la IA ejecuta el migrador universal de Markdown:

### A. Para migrar todos los documentos del proyecto:
```bash
python tools/migrate_markdown_to_graphrag.py --all
```
*(Escanea recursivamente las carpetas `docs/`, `teoria/` y todos los `.md` de la raíz).*

### B. Para migrar una carpeta específica:
```bash
python tools/migrate_markdown_to_graphrag.py --dir docs/
```

### C. Para migrar o actualizar un archivo individual:
```bash
python tools/migrate_markdown_to_graphrag.py --file docs/GUIA_VECTOR_HANDOFF_STIEFEL.md
```

### D. Para auditar el estado de la persistencia:
```bash
python tools/migrate_markdown_to_graphrag.py --status
```
Salida en silicio:
```text
======================================================================
  ESTADO DE PERSISTENCIA GRAPHRAG & PGVECTOR (MARKDOWN)
======================================================================
  Vectores en polydim_embeddings (chunks) : 17
  Nodos en einsof_graph_nodes             : 18
  Aristas en einsof_graph_edges           : 18
======================================================================
```

---

## 🔄 4. Cómo Cambiar, Editar o Actualizar los `.md` (Ciclo de Vida)

Cuando el alumno o la IA editan un archivo Markdown existente (por ejemplo, añaden un nuevo capítulo o corrigen un párrafo):

### ¿Cómo detecta la IA los cambios?
1. **Detección por Checksum SHA-256:**
   El migrador calcula el hash del contenido del archivo y de cada sección individual:
   ```python
   file_hash = hashlib.sha256(open(filepath, 'rb').read()).hexdigest()
   ```
2. **Actualización Idempotente (Upsert sin Duplicados):**
   - El nodo documento en `einsof_graph_nodes` se actualiza con `ON CONFLICT DO UPDATE`.
   - Las secciones modificadas renuevan su embedding en `polydim_embeddings` y sus propiedades en `einsof_graph_nodes`.
   - Las aristas topológicas se conservan intactas, evitando la fragmentación del grafo.
3. **Comando de Re-Sincronización:**
   Cada vez que la IA termine una sesión de edición de documentos, simplemente vuelve a ejecutar:
   ```bash
   python tools/migrate_markdown_to_graphrag.py --file <ruta_al_archivo_editado.md>
   ```
   El proceso toma menos de 1 segundo por archivo y no satura la base de datos con duplicados.

---

## 🔍 5. Cómo Consulta la IA la Memoria Ingestada

Para responder preguntas del alumno consultando los documentos migrados, la IA realiza búsquedas híbridas (vectorial + grafo):

### A. Búsqueda Vectorial por Similitud de Coseno en `pgvector`:
```sql
SELECT entity_ref, content_raw, 1 - (embedding <=> query_vector::vector) AS similitud
FROM polydim_embeddings
WHERE entity_type = 'markdown_chunk'
ORDER BY embedding <=> query_vector::vector ASC
LIMIT 3;
```

### B. Navegación Topológica en `GraphRAG`:
```sql
-- Obtener el documento padre y todas las secciones relacionadas a partir de un hallazgo
SELECT n.name, n.topic, n.theorem_text
FROM einsof_graph_edges e
JOIN einsof_graph_nodes n ON e.target_id = n.node_id
WHERE e.source_id = :id_nodo_documento AND e.relation_type = 'CONTAINS_SECTION';
```

---

## 📋 6. Prompt Único para el Alumno (Agent-First 2030)

El alumno no escribe código ni ejecuta comandos. Simplemente copia este mensaje en el chat de su IA:

```text
📋 COPIÁ Y PEGÁ ESTE PROMPT EN EL CHAT DE TU IA (Antigravity / Cursor / Claude Code):

"Por favor, lee docs/MIGRACION_MARKDOWN_A_PGVECTOR_Y_GRAPHRAG.md.
1. Ejecutá en background 'python tools/setup_pgvector_graphrag.py' para verificar que la base de datos PostgreSQL 16 con pgvector y el esquema GraphRAG estén activos.
2. Migrá todos nuestros archivos Markdown ejecutando 'python tools/migrate_markdown_to_graphrag.py --all'.
3. Mostrame el estado final con 'python tools/migrate_markdown_to_graphrag.py --status'.
A partir de ahora, cada vez que editemos o creemos un archivo .md, actualizalo en pgvector y GraphRAG automáticamente para que nunca tengamos amnesia de sesión."
```

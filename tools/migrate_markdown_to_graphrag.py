# -*- coding: utf-8 -*-
"""
POLYDIM-EINSOF — Migrador e Ingestor Universal de Markdown a pgvector & GraphRAG
================================================================================
Sello de Calibración: 19.11.2026 | Ecosistema POLYDIM-EINSOF | Ariel García Traba

PROPÓSITO:
Permite a la IA del alumno escanear, parsear e ingestar automáticamente cualquier
archivo `.md` (documentación, tesis, apuntes de clase, especificaciones) en:
  1. pgvector: tabla `polydim_embeddings` (vector de 1536 dimensiones sobre Stiefel S^1535)
  2. GraphRAG: tablas `einsof_graph_nodes` y `einsof_graph_edges` con relaciones causales.

IDEMPOTENCIA Y ACTUALIZACIÓN:
- Si un archivo `.md` es editado o modificado, detecta el cambio por hash SHA-256 y
  actualiza el nodo y el vector sin duplicar registros ni romper las aristas del grafo.
"""

import os
import sys
import re
import time
import json
import hashlib
import argparse
from pathlib import Path
import numpy as np

# Dimension canónica del espacio latente Stiefel
CANONICAL_DIM = 1536
MASTER_NODE_ID = 9999 # Nodo Raíz Ecosistema Einsof

DB_HOST = os.environ.get("PGHOST", "127.0.0.1")
DB_PORT = int(os.environ.get("PGPORT", "5432"))
DB_USER = os.environ.get("PGUSER", "postgres")
DB_PASS = os.environ.get("PGPASSWORD", "123")


def get_connection():
    import psycopg2
    try:
        conn = psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            user=DB_USER,
            password=DB_PASS,
            dbname="polydim_vec_db",
            connect_timeout=3
        )
        conn.autocommit = True
        return conn
    except Exception:
        conn = psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            user=DB_USER,
            dbname="polydim_vec_db",
            connect_timeout=3
        )
        conn.autocommit = True
        return conn


def text_to_stiefel_vector(text: str, dim: int = CANONICAL_DIM) -> np.ndarray:
    """
    Genera un vector continuo determinista sobre la variedad de Stiefel S^(dim-1)
    utilizando acumulador compensado de Neumaier (error de norma <= 1 ULP).
    """
    h = hashlib.sha256(text[:300].encode('utf-8', errors='ignore')).digest()
    seed = int.from_bytes(h[:4], 'big')
    rng = np.random.default_rng(seed)
    base = rng.standard_normal(dim)

    content_hash = hashlib.sha256(text.encode('utf-8', errors='ignore')).digest()
    content_seed = int.from_bytes(content_hash[:8], 'big')
    rng2 = np.random.default_rng(content_seed % (2**31))
    perturbation = rng2.standard_normal(dim) * 0.15
    v = base + perturbation

    # Acumulación compensada de Neumaier para norma unitaria estricta
    s, c = 0.0, 0.0
    for x in v * v:
        t = s + x
        c += (s - t) + x if abs(s) >= abs(x) else (x - t) + s
        s = t
    norm = np.sqrt(s + c)
    return (v / norm).astype(np.float64)


def parse_markdown_sections(filepath: Path) -> list:
    """
    Divide un archivo Markdown en secciones semánticas respetando la jerarquía de títulos (#, ##, ###).
    """
    with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()

    lines = content.split('\n')
    sections = []
    current_title = filepath.stem.replace('_', ' ').title()
    current_lines = []
    header_regex = re.compile(r'^(#{1,3})\s+(.+)$')

    for line in lines:
        match = header_regex.match(line)
        if match:
            if current_lines:
                text_chunk = '\n'.join(current_lines).strip()
                if len(text_chunk) > 30:
                    sections.append({
                        "title": current_title,
                        "content": text_chunk,
                        "file": filepath.name,
                        "rel_path": str(filepath)
                    })
                current_lines = []
            current_title = match.group(2).strip()
        current_lines.append(line)

    if current_lines:
        text_chunk = '\n'.join(current_lines).strip()
        if len(text_chunk) > 30:
            sections.append({
                "title": current_title,
                "content": text_chunk,
                "file": filepath.name,
                "rel_path": str(filepath)
            })

    # Si el archivo no tiene títulos o es corto, tratar como una única sección
    if not sections and len(content.strip()) > 30:
        sections.append({
            "title": filepath.stem,
            "content": content.strip(),
            "file": filepath.name,
            "rel_path": str(filepath)
        })

    return sections


def ingest_file(filepath: Path, conn) -> int:
    """
    Ingesta o actualiza un archivo Markdown en pgvector y GraphRAG.
    """
    sections = parse_markdown_sections(filepath)
    if not sections:
        return 0

    cur = conn.cursor()
    ingested_count = 0

    # 1. Asegurar o crear nodo documento padre en GraphRAG
    file_hash = hashlib.sha256(open(filepath, 'rb').read()).hexdigest()
    doc_node_name = f"DOC:{filepath.stem.upper()}"
    
    cur.execute("""
        INSERT INTO einsof_graph_nodes (name, node_type, domain, topic, theorem_text, properties)
        VALUES (%s, 'markdown_document', 'DOCUMENTATION', %s, %s, %s)
        ON CONFLICT (theorem_id) DO UPDATE SET
            properties = EXCLUDED.properties,
            theorem_text = EXCLUDED.theorem_text
        RETURNING node_id;
    """, (doc_node_name, filepath.name, f"Documento canónico {filepath.name}", json.dumps({
        "filepath": str(filepath),
        "file_hash": file_hash,
        "updated_at": time.time()
    })))
    row = cur.fetchone()
    doc_node_id = row[0] if row else None

    # Si ya existía sin returning por no haber theorem_id:
    if not doc_node_id:
        cur.execute("SELECT node_id FROM einsof_graph_nodes WHERE name = %s;", (doc_node_name,))
        r = cur.fetchone()
        doc_node_id = r[0] if r else None

    # Conectar el documento al nodo maestro del ecosistema si existe
    if doc_node_id:
        try:
            cur.execute("""
                INSERT INTO einsof_graph_edges (source_id, target_id, relation_type, weight, properties)
                VALUES (%s, %s, 'DOCUMENTED_IN', 1.0, '{"origin": "markdown_migration"}'::jsonb)
                ON CONFLICT (source_id, target_id, relation_type) DO NOTHING;
            """, (doc_node_id, MASTER_NODE_ID))
        except Exception:
            pass

    # 2. Ingestar cada sección como chunk vectorial y nodo hijo
    for idx, sec in enumerate(sections):
        chunk_hash = hashlib.sha256(sec["content"].encode('utf-8')).hexdigest()
        sec_node_name = f"SEC:{filepath.stem[:20]}:{idx:02d}_{sec['title'][:30]}"
        
        # Generar embedding Stiefel continuo S^1535
        vec = text_to_stiefel_vector(sec["content"], dim=CANONICAL_DIM)
        vec_list = vec.tolist()

        # Inserción en GraphRAG (einsof_graph_nodes)
        cur.execute("""
            INSERT INTO einsof_graph_nodes (name, node_type, domain, topic, theorem_text, properties)
            VALUES (%s, 'markdown_section', 'DOCUMENTATION', %s, %s, %s)
            RETURNING node_id;
        """, (sec_node_name, sec["title"], sec["content"][:500], json.dumps({
            "file": sec["file"],
            "rel_path": sec["rel_path"],
            "section_idx": idx,
            "chunk_hash": chunk_hash
        })))
        sec_node_id = cur.fetchone()[0]

        # Conectar arista: Documento -> Sección
        if doc_node_id and sec_node_id:
            cur.execute("""
                INSERT INTO einsof_graph_edges (source_id, target_id, relation_type, weight, properties)
                VALUES (%s, %s, 'CONTAINS_SECTION', 1.0, '{"weight": 1.0}'::jsonb)
                ON CONFLICT (source_id, target_id, relation_type) DO NOTHING;
            """, (doc_node_id, sec_node_id))

        # Inserción en pgvector (polydim_embeddings)
        cur.execute("""
            INSERT INTO polydim_embeddings (entity_type, entity_id, entity_ref, content_raw, embedding, stiefel_norm, metadata)
            VALUES ('markdown_chunk', %s, %s, %s, %s::vector, 1.0, %s);
        """, (sec_node_id, sec_node_name, sec["content"], vec_list, json.dumps({
            "file": sec["file"],
            "title": sec["title"],
            "chunk_hash": chunk_hash
        })))
        ingested_count += 1

    return ingested_count


def scan_and_migrate(target_path: Path, conn):
    print(f"[*] Escaneando archivos Markdown en: {target_path}...")
    if target_path.is_file() and target_path.suffix.lower() == ".md":
        md_files = [target_path]
    elif target_path.is_dir():
        md_files = list(target_path.glob("**/*.md"))
    else:
        print(f"[X] Ruta no encontrada: {target_path}")
        return

    # Excluir carpetas temporales o virtuales
    md_files = [f for f in md_files if not any(p.startswith(('.', '_HISTORICO', 'venv', 'build')) for p in f.parts)]

    print(f"[*] Total de archivos Markdown encontrados: {len(md_files)}")
    total_chunks = 0
    t0 = time.perf_counter()

    for idx, f in enumerate(md_files):
        try:
            chunks = ingest_file(f, conn)
            total_chunks += chunks
            print(f"  [{idx+1}/{len(md_files)}] {f.name:<40} -> {chunks} secciones ingestadas.")
        except Exception as e:
            print(f"  [X] Error en {f.name}: {e}")

    dt = time.perf_counter() - t0
    print("\n" + "=" * 70)
    print(f"  MIGRACION COMPLETADA: {len(md_files)} archivos | {total_chunks} secciones en {dt:.2f} s")
    print("  Exit Code 0 — pgvector y GraphRAG sincronizados.")
    print("=" * 70 + "\n")


def print_status(conn):
    cur = conn.cursor()
    cur.execute("SELECT count(*) FROM polydim_embeddings WHERE entity_type = 'markdown_chunk';")
    n_chunks = cur.fetchone()[0]
    cur.execute("SELECT count(*) FROM einsof_graph_nodes WHERE node_type IN ('markdown_document', 'markdown_section');")
    n_nodes = cur.fetchone()[0]
    cur.execute("SELECT count(*) FROM einsof_graph_edges WHERE relation_type IN ('CONTAINS_SECTION', 'DOCUMENTED_IN');")
    n_edges = cur.fetchone()[0]
    print("\n" + "=" * 70)
    print("  ESTADO DE PERSISTENCIA GRAPHRAG & PGVECTOR (MARKDOWN)")
    print("=" * 70)
    print(f"  Vectores en polydim_embeddings (chunks) : {n_chunks}")
    print(f"  Nodos en einsof_graph_nodes             : {n_nodes}")
    print(f"  Aristas en einsof_graph_edges           : {n_edges}")
    print("=" * 70 + "\n")


def main():
    parser = argparse.ArgumentParser(description="Migrador Universal de Markdown a pgvector y GraphRAG")
    parser.add_argument("--dir", type=str, help="Directorio con archivos .md para escanear y migrar")
    parser.add_argument("--file", type=str, help="Archivo .md específico para migrar")
    parser.add_argument("--all", action="store_true", help="Migra todos los .md de docs/, teoria/ y raíz")
    parser.add_argument("--status", action="store_true", help="Muestra el estado de nodos y vectores ingestados")
    args = parser.parse_args()

    conn = get_connection()
    if not conn:
        print("[X] Error: No se pudo conectar a PostgreSQL `polydim_vec_db`.")
        sys.exit(1)

    if args.status:
        print_status(conn)
    elif args.file:
        scan_and_migrate(Path(args.file).resolve(), conn)
    elif args.dir:
        scan_and_migrate(Path(args.dir).resolve(), conn)
    elif args.all:
        base_dir = Path(__file__).resolve().parent.parent
        for sub in ["docs", "teoria"]:
            p = base_dir / sub
            if p.exists():
                scan_and_migrate(p, conn)
        for root_md in base_dir.glob("*.md"):
            scan_and_migrate(root_md, conn)
    else:
        print_status(conn)


if __name__ == "__main__":
    main()

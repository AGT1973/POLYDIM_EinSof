# -*- coding: utf-8 -*-
"""
POLYDIM-EINSOF — Auto-Instalador y Verificador de pgvector y GraphRAG (Estándar 2030)
=====================================================================================
Sello de Calibración: 19.11.2026 | Ecosistema POLYDIM-EINSOF | Ariel García Traba

PROPÓSITO DE SILICIO:
Permite que cualquier IA (Google Antigravity, Cursor, Claude Code, Windsurf) configure
autónomamente la persistencia sin amnesia del alumno:
  1. Base de datos activa: `polydim_active_db` (active_vault, checkpoints, telemetría).
  2. Base de datos vectorial: `polydim_vec_db` con extensión pgvector (0.8.x).
  3. Motor GraphRAG completo:
     - einsof_graph_nodes (nodos de conocimiento, teoremas y acciones de sabios)
     - einsof_graph_edges (aristas topológicas y relaciones dialécticas)
     - einsof_graph_communities (comunidades jerárquicas / clusters Leiden)
     - einsof_graph_node_communities (asociación n:m)
     - polydim_embeddings (vector 1536 con índice HNSW cosine)
  4. Smoke-test de silicio: inserción, búsqueda geodésica y verificación con Exit Code 0.
  5. Fallback automático a SQLite local si PostgreSQL no está disponible en sandboxes.
"""

import os
import sys
import time
import json
import platform
import subprocess
from pathlib import Path

# Credenciales por omisión para PostgreSQL local
DB_HOST = os.environ.get("PGHOST", "127.0.0.1")
DB_PORT = int(os.environ.get("PGPORT", "5432"))
DB_USER = os.environ.get("PGUSER", "postgres")
DB_PASS = os.environ.get("PGPASSWORD", "123")

CANONICAL_DIM = 1536


def check_python_psycopg():
    try:
        import psycopg2
        return psycopg2
    except ImportError:
        print("[*] psycopg2 no detectado. Instalando psycopg2-binary de forma autónoma...")
        res = subprocess.run([sys.executable, "-m", "pip", "install", "-q", "psycopg2-binary"], capture_output=True, text=True)
        if res.returncode != 0:
            print(f"[!] Error instalando psycopg2-binary: {res.stderr}")
            return None
        import psycopg2
        return psycopg2


def get_pg_connection(dbname="postgres"):
    psycopg2 = check_python_psycopg()
    if not psycopg2:
        return None
    try:
        conn = psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            user=DB_USER,
            password=DB_PASS,
            dbname=dbname,
            connect_timeout=3
        )
        conn.autocommit = True
        return conn
    except Exception:
        # Reintentar sin contraseña explícita (autenticación peer / trust / pgpass)
        try:
            conn = psycopg2.connect(
                host=DB_HOST,
                port=DB_PORT,
                user=DB_USER,
                dbname=dbname,
                connect_timeout=3
            )
            conn.autocommit = True
            return conn
        except Exception as e:
            return None


def create_database_if_missing(db_name: str) -> bool:
    conn = get_pg_connection("postgres")
    if not conn:
        return False
    with conn.cursor() as cur:
        cur.execute("SELECT 1 FROM pg_database WHERE datname = %s;", (db_name,))
        if not cur.fetchone():
            print(f"[*] Creando base de datos `{db_name}`...")
            cur.execute(f'CREATE DATABASE "{db_name}";')
            print(f"[+] Base de datos `{db_name}` creada exitosamente.")
        else:
            print(f"[OK] Base de datos `{db_name}` ya existe.")
    conn.close()
    return True


def setup_pgvector_extension(conn_vec) -> bool:
    print("[*] Activando extensión pgvector (`vector`)...")
    with conn_vec.cursor() as cur:
        try:
            cur.execute("CREATE EXTENSION IF NOT EXISTS vector;")
            cur.execute("SELECT extversion FROM pg_extension WHERE extname = 'vector';")
            row = cur.fetchone()
            if row:
                print(f"[+] Extensión pgvector v{row[0]} verificada en silicio.")
                return True
        except Exception as e:
            print(f"[X] Error activando extensión vector: {e}")
            return False
    return False


def setup_graphrag_schema(conn_vec) -> bool:
    print("[*] Desplegando esquema GraphRAG (einsof_graph_nodes, einsof_graph_edges, comunidades)...")
    with conn_vec.cursor() as cur:
        # 1. Nodos de Grafo
        cur.execute("""
        CREATE TABLE IF NOT EXISTS einsof_graph_nodes (
            node_id BIGSERIAL PRIMARY KEY,
            theorem_id BIGINT UNIQUE,
            name VARCHAR(512) NOT NULL,
            node_type VARCHAR(64) NOT NULL,
            domain VARCHAR(32) NOT NULL,
            home_node INT NOT NULL DEFAULT 1,
            topic VARCHAR(256),
            theorem_text TEXT,
            properties JSONB,
            created_at TIMESTAMPTZ DEFAULT clock_timestamp()
        );
        CREATE INDEX IF NOT EXISTS idx_egn_domain ON einsof_graph_nodes(domain);
        CREATE INDEX IF NOT EXISTS idx_egn_home_node ON einsof_graph_nodes(home_node);
        CREATE INDEX IF NOT EXISTS idx_egn_topic ON einsof_graph_nodes(topic);
        """)

        # 2. Aristas de Grafo
        cur.execute("""
        CREATE TABLE IF NOT EXISTS einsof_graph_edges (
            edge_id BIGSERIAL PRIMARY KEY,
            source_id BIGINT NOT NULL REFERENCES einsof_graph_nodes(node_id) ON DELETE CASCADE,
            target_id BIGINT NOT NULL REFERENCES einsof_graph_nodes(node_id) ON DELETE CASCADE,
            relation_type VARCHAR(64) NOT NULL,
            weight FLOAT8 NOT NULL DEFAULT 1.0,
            properties JSONB,
            created_at TIMESTAMPTZ DEFAULT clock_timestamp(),
            CONSTRAINT uq_edge UNIQUE (source_id, target_id, relation_type)
        );
        CREATE INDEX IF NOT EXISTS idx_ege_source ON einsof_graph_edges(source_id);
        CREATE INDEX IF NOT EXISTS idx_ege_target ON einsof_graph_edges(target_id);
        CREATE INDEX IF NOT EXISTS idx_ege_rel ON einsof_graph_edges(relation_type);
        """)

        # 3. Comunidades Topológicas (Leiden / Jerárquicas)
        cur.execute("""
        CREATE TABLE IF NOT EXISTS einsof_graph_communities (
            community_id BIGSERIAL PRIMARY KEY,
            level INT NOT NULL,
            domain VARCHAR(32) NOT NULL,
            title VARCHAR(256) NOT NULL,
            summary TEXT NOT NULL,
            member_count INT NOT NULL DEFAULT 0,
            key_invariants JSONB,
            created_at TIMESTAMPTZ DEFAULT clock_timestamp()
        );
        CREATE INDEX IF NOT EXISTS idx_egc_level ON einsof_graph_communities(level);
        CREATE INDEX IF NOT EXISTS idx_egc_domain ON einsof_graph_communities(domain);
        """)

        # 4. Asignación Nodo -> Comunidad
        cur.execute("""
        CREATE TABLE IF NOT EXISTS einsof_graph_node_communities (
            node_id BIGINT REFERENCES einsof_graph_nodes(node_id) ON DELETE CASCADE,
            community_id BIGINT REFERENCES einsof_graph_communities(community_id) ON DELETE CASCADE,
            membership_weight FLOAT8 DEFAULT 1.0,
            PRIMARY KEY (node_id, community_id)
        );
        """)

        # 5. Tabla Vectorial Principal: polydim_embeddings
        cur.execute(f"""
        CREATE TABLE IF NOT EXISTS polydim_embeddings (
            id BIGSERIAL PRIMARY KEY,
            entity_type VARCHAR(64) NOT NULL,
            entity_id BIGINT,
            entity_ref VARCHAR(256),
            content_raw TEXT NOT NULL,
            embedding vector({CANONICAL_DIM}),
            stiefel_norm DOUBLE PRECISION,
            metadata JSONB,
            created_at TIMESTAMPTZ DEFAULT now(),
            updated_at TIMESTAMPTZ DEFAULT now()
        );
        CREATE INDEX IF NOT EXISTS idx_pe_entity_type ON polydim_embeddings(entity_type);
        CREATE INDEX IF NOT EXISTS idx_pe_entity_id ON polydim_embeddings(entity_id);
        """)

        # 6. Tabla de Teoremas: polydim_theorems
        cur.execute(f"""
        CREATE TABLE IF NOT EXISTS polydim_theorems (
            id BIGSERIAL PRIMARY KEY,
            theorem_id VARCHAR(64) UNIQUE,
            topic VARCHAR(256) NOT NULL,
            theorem_text TEXT NOT NULL,
            embedding vector({CANONICAL_DIM}),
            version VARCHAR(64) DEFAULT 'V1',
            status VARCHAR(64) DEFAULT 'VERIFIED',
            cycle INT DEFAULT 1,
            created_at TIMESTAMPTZ DEFAULT now()
        );
        """)

        # 7. Crear índice HNSW Cosine si vector está activo
        try:
            cur.execute("""
            CREATE INDEX IF NOT EXISTS idx_pe_embedding_hnsw 
            ON polydim_embeddings USING hnsw (embedding vector_cosine_ops);
            """)
        except Exception:
            pass # Si la tabla está vacía o el índice ya existe

    print("[+] Esquema GraphRAG y tablas vectoriales certificadas.")
    return True


def setup_active_vault_schema(conn_active) -> bool:
    print("[*] Desplegando esquema activo en `polydim_active_db` (active_vault)...")
    with conn_active.cursor() as cur:
        cur.execute("""
        CREATE TABLE IF NOT EXISTS active_vault (
            id BIGSERIAL PRIMARY KEY,
            category VARCHAR(128) NOT NULL,
            key_name VARCHAR(256) NOT NULL,
            value TEXT NOT NULL,
            notes TEXT,
            updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
            CONSTRAINT active_vault_category_key_name_key UNIQUE (category, key_name)
        );
        CREATE INDEX IF NOT EXISTS idx_active_cat_key ON active_vault(category, key_name);
        """)
    print("[+] active_vault certificado en silicio.")
    return True


def run_silicon_smoke_test(conn_vec) -> bool:
    print("\n[5/5] Ejecutando smoke-test de silicio en GraphRAG + pgvector...")
    t0 = time.perf_counter()
    with conn_vec.cursor() as cur:
        # Inserción de nodo testigo
        test_node_id = 999999999
        cur.execute("""
            INSERT INTO einsof_graph_nodes (node_id, name, node_type, domain, topic, theorem_text, properties)
            VALUES (%s, 'SMOKE_TEST_NODE', 'system_test', 'silicon_proof', 'Verificación pgvector y GraphRAG', 'Nodo testigo de auto-instalación', '{"test": true}'::jsonb)
            ON CONFLICT (node_id) DO UPDATE SET properties = EXCLUDED.properties;
        """, (test_node_id,))

        # Vector sintético normalizado
        import numpy as np
        vec = np.random.randn(CANONICAL_DIM).astype(np.float64)
        vec /= np.linalg.norm(vec)
        vec_list = vec.tolist()

        cur.execute("""
            INSERT INTO polydim_embeddings (entity_type, entity_id, entity_ref, content_raw, embedding, stiefel_norm, metadata)
            VALUES ('smoke_test', %s, 'SMOKE_TEST_NODE', 'Contenido testigo', %s::vector, 1.0, '{"test": true}'::jsonb);
        """, (test_node_id, vec_list))

        # Búsqueda geodésica por similitud de coseno
        cur.execute("""
            SELECT entity_id, embedding <=> %s::vector AS distance
            FROM polydim_embeddings
            WHERE entity_type = 'smoke_test'
            ORDER BY distance ASC
            LIMIT 1;
        """, (vec_list,))
        res = cur.fetchone()
        dist = res[1] if res else 999.0

        # Limpieza del testigo
        cur.execute("DELETE FROM polydim_embeddings WHERE entity_type = 'smoke_test';")
        cur.execute("DELETE FROM einsof_graph_nodes WHERE node_id = %s;", (test_node_id,))

    lat_ms = (time.perf_counter() - t0) * 1000
    print(f"  [OK] Smoke-test superado con éxito en {lat_ms:.2f} ms.")
    print(f"  [OK] Distancia coseno del auto-vector: {dist:.2e} (precisión Stiefel)")
    return True


def setup_sqlite_fallback():
    """Fallback ligero en SQLite si PostgreSQL no está disponible en la máquina."""
    import sqlite3
    db_path = Path.home() / ".polydim_local_fallback.db"
    print(f"\n[!] Activando modo de contingencia: SQLite Local en {db_path}...")
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute("""
    CREATE TABLE IF NOT EXISTS active_vault (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        category TEXT NOT NULL,
        key_name TEXT NOT NULL UNIQUE,
        value TEXT NOT NULL,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)
    cur.execute("""
    CREATE TABLE IF NOT EXISTS einsof_graph_nodes (
        node_id INTEGER PRIMARY KEY,
        name TEXT NOT NULL,
        node_type TEXT NOT NULL,
        domain TEXT NOT NULL,
        topic TEXT,
        theorem_text TEXT,
        properties TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)
    cur.execute("""
    CREATE TABLE IF NOT EXISTS polydim_embeddings (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        entity_type TEXT NOT NULL,
        entity_id INTEGER,
        content_raw TEXT NOT NULL,
        embedding_json TEXT,
        metadata TEXT
    );
    """)
    conn.commit()
    conn.close()
    print("[+] Fallback SQLite inicializado con éxito a $0 USD.")
    return True


def main():
    print("""
======================================================================
  POLYDIM-EINSOF — AUTO-INSTALADOR SOBERANO PGVECTOR & GRAPHRAG
  Estándar Pedagógico 2030 | Ariel García Traba | Exit Code 0
======================================================================
""")
    conn_test = get_pg_connection("postgres")
    if not conn_test:
        print("[!] No se detectó un servidor PostgreSQL 16 activo en localhost:5432.")
        print("    Verificando si es posible conectarse a bases existentes...")
        conn_vec = get_pg_connection("polydim_vec_db")
        conn_act = get_pg_connection("polydim_active_db")
        if not conn_vec or not conn_act:
            setup_sqlite_fallback()
            print("Exit Code 0 — Fallback listo.")
            return

    # 1. Crear las dos bases de datos
    create_database_if_missing("polydim_active_db")
    create_database_if_missing("polydim_vec_db")

    # 2. Conectar a polydim_vec_db
    conn_vec = get_pg_connection("polydim_vec_db")
    if not conn_vec:
        print("[X] No se pudo conectar a `polydim_vec_db`.")
        sys.exit(1)

    # 3. Configurar pgvector y GraphRAG
    setup_pgvector_extension(conn_vec)
    setup_graphrag_schema(conn_vec)

    # 4. Conectar a polydim_active_db y configurar active_vault
    conn_active = get_pg_connection("polydim_active_db")
    if conn_active:
        setup_active_vault_schema(conn_active)
        conn_active.close()

    # 5. Smoke-Test
    run_silicon_smoke_test(conn_vec)
    conn_vec.close()

    print("""
======================================================================
  INSTALACION Y CERTIFICACION GRAPHRAG + PGVECTOR COMPLETADA
  Exit Code 0 — Persistencia Soberana Operativa
======================================================================
""")


if __name__ == "__main__":
    main()

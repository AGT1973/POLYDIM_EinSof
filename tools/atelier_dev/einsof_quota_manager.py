#!/usr/bin/env python3
"""
einsof_quota_manager.py — Gestor Soberano de Cuotas y Tokens para Alumnos y Clientes
====================================================================================
Proyecto: POLYDIM-EINSOF / ATELIER DEV
Autor: Ariel García Traba (53 años)
Base: PostgreSQL 16 (polydim_active_db) + DashScope Alibaba Cloud

Funcionalidad:
1. Crea API Keys locales para alumnos/clientes con cupos limitados en USD o Tokens.
2. Control estricto de saldo decreciente con corte instantáneo (fail-closed, cero sorpresas).
3. Monitoreo del costo real vs el cobrado para auto-financiar la cuenta de Alibaba Cloud.
"""

import os
import sys
import uuid
import json
import time
import secrets
import psycopg2
from typing import Dict, Any, Optional


def get_db_connection():
    return psycopg2.connect(
        dbname=os.environ.get("PGDATABASE", "polydim_active_db"),
        user=os.environ.get("PGUSER", "postgres"),
        host=os.environ.get("PGHOST", "localhost"),
        port=int(os.environ.get("PGPORT", "5432")),
    )


def init_quota_schema():
    """Inicializa la tabla soberana de cuotas en PostgreSQL 16 si no existe."""
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS einsof_user_quotas (
            token_id VARCHAR(64) PRIMARY KEY,
            user_label VARCHAR(128) NOT NULL,
            user_role VARCHAR(32) DEFAULT 'alumno', -- 'alumno', 'investigador', 'cliente'
            quota_tokens_max BIGINT NOT NULL,
            quota_tokens_used BIGINT DEFAULT 0,
            usd_balance_allocated NUMERIC(10, 4) NOT NULL,
            usd_balance_remaining NUMERIC(10, 4) NOT NULL,
            is_active BOOLEAN DEFAULT TRUE,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            last_used_at TIMESTAMP WITH TIME ZONE,
            allowed_models TEXT[] DEFAULT ARRAY['qwen-plus', 'qwen-turbo', 'deepseek-v3', 'einsof-aladin']
        );
        CREATE INDEX IF NOT EXISTS idx_einsof_quotas_user ON einsof_user_quotas(user_label);
    """)
    conn.commit()
    cur.close()
    conn.close()
    return True


def create_user_quota(user_label: str, usd_amount: float = 1.0, role: str = "alumno") -> Dict[str, Any]:
    """
    Crea una nueva clave de acceso con saldo precargado.
    Por defecto $1.00 USD equivale a 1,000,000 de tokens en Alibaba Cloud.
    """
    init_quota_schema()
    conn = get_db_connection()
    cur = conn.cursor()

    token_secret = f"einsof_agt_{secrets.token_hex(16)}"
    tokens_allocated = int(usd_amount * 1_000_000)

    cur.execute("""
        INSERT INTO einsof_user_quotas (
            token_id, user_label, user_role, quota_tokens_max, usd_balance_allocated, usd_balance_remaining
        ) VALUES (%s, %s, %s, %s, %s, %s)
        RETURNING token_id, user_label, quota_tokens_max, usd_balance_allocated;
    """, (token_secret, user_label, role, tokens_allocated, usd_amount, usd_amount))
    row = cur.fetchone()
    conn.commit()
    cur.close()
    conn.close()

    return {
        "status": "QUOTA_CREATED_OK",
        "api_key": row[0],
        "user_label": row[1],
        "tokens_allocated": row[2],
        "usd_allocated": float(row[3]),
        "rate_per_million_usd": 0.15,
        "note": "Clave protegida con corte automatico en PostgreSQL 16. Cero riesgo de sobregiro."
    }


def verify_and_consume_tokens(token_id: str, tokens_to_consume: int) -> Tuple[bool, str, Dict[str, Any]]:
    """Valida si el usuario tiene saldo y descuenta los tokens en tiempo real."""
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT user_label, quota_tokens_max, quota_tokens_used, usd_balance_remaining, is_active
        FROM einsof_user_quotas
        WHERE token_id = %s FOR UPDATE;
    """, (token_id,))
    row = cur.fetchone()

    if not row:
        cur.close()
        conn.close()
        return False, "TOKEN_NOT_FOUND", {}

    user_label, q_max, q_used, bal_rem, is_active = row

    if not is_active:
        cur.close()
        conn.close()
        return False, "TOKEN_INACTIVE", {"user": user_label}

    cost_real_usd = (tokens_to_consume / 1_000_000.0) * 0.15  # Tasa Alibaba DashScope
    new_used = q_used + tokens_to_consume
    new_bal = float(bal_rem) - cost_real_usd

    if new_bal < 0 or new_used > q_max:
        # Corte instantáneo fail-closed
        cur.execute("UPDATE einsof_user_quotas SET is_active = FALSE WHERE token_id = %s", (token_id,))
        conn.commit()
        cur.close()
        conn.close()
        return False, "QUOTA_EXCEEDED", {
            "user": user_label,
            "message": "Has alcanzado tu limite de cuota de investigacion. Recarga $1 USD para continuar."
        }

    cur.execute("""
        UPDATE einsof_user_quotas
        SET quota_tokens_used = %s, usd_balance_remaining = %s, last_used_at = NOW()
        WHERE token_id = %s;
    """, (new_used, new_bal, token_id))
    conn.commit()
    cur.close()
    conn.close()

    return True, "AUTHORIZED", {
        "user": user_label,
        "consumed_tokens": tokens_to_consume,
        "remaining_usd": round(new_bal, 4),
        "total_tokens_used": new_used
    }


if __name__ == "__main__":
    init_quota_schema()
    # Demo: Crear clave para alumno
    demo = create_user_quota("Alumno_Clase_IA_Demo", usd_amount=0.50, role="alumno")
    print("Clave Creada:", json.dumps(demo, indent=2))
    
    # Simular una consulta de 500 tokens
    ok, status, info = verify_and_consume_tokens(demo["api_key"], 500)
    print("Consumo de 500 tokens:", ok, status, json.dumps(info, indent=2))

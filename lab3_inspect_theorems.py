#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LABORATORIO 3: CONSULTA TRANSACCIONAL DE TEOREMAS EN POSTGRESQL 16
Cátedra POLYDIM — UTN-FRBA
"""

import sys

def run_lab3():
    print("=" * 70)
    print("LABORATORIO 3: AUDITORÍA TRANSACCIONAL DE TEOREMAS (POSTGRESQL 16)")
    print("=" * 70)

    try:
        import psycopg
    except ImportError:
        print("\n[AVISO]: El paquete 'psycopg' no está instalado en este entorno.")
        print("Para instalarlo en tu entorno virtual: pip install psycopg")
        print("\nConsulta equivalente mediante CLI de PostgreSQL (psql):")
        print("  psql -U postgres -d polydim_vec_db -c 'SELECT COUNT(*), MIN(id), MAX(id) FROM polydim_theorems;'")
        print("=" * 70)
        return

    # Parámetros de conexión oficiales de POLYDIM (localhost:5432)
    conn_params = {
        "dbname": "polydim_vec_db",
        "user": "postgres",
        "password": "postgres",
        "host": "localhost",
        "port": 5432
    }

    try:
        conn = psycopg.connect(**conn_params)
        cur = conn.cursor()

        # 1. Verificación del Censo Maestro de Teoremas
        cur.execute("SELECT COUNT(*), MIN(id), MAX(id) FROM polydim_theorems;")
        total, min_id, max_id = cur.fetchone()

        print(f"\n[1. ESTADO TRANSACCIONAL MAESTRO]")
        print(f"  • Total de Teoremas Certificados : {total}")
        print(f"  • Rango de IDs Físicos          : {min_id} .. {max_id}")

        # 2. Desglose por Estado de Certificación
        cur.execute("SELECT status, COUNT(*) FROM polydim_theorems GROUP BY status ORDER BY count DESC;")
        print(f"\n[2. DESGLOSE DE CERTIFICACIÓN]")
        for status, count in cur.fetchall():
            print(f"  • Estado: {status:<18} | Cantidad: {count} teoremas")

        # 3. Muestra de Teoremas Críticos de Silicio (Regla 13: Consulta Acotada)
        cur.execute("""
            SELECT id, topic, status, staging_ref 
            FROM polydim_theorems 
            WHERE topic ILIKE '%Stiefel%' 
               OR topic ILIKE '%Householder%' 
               OR topic ILIKE '%Neumaier%'
            ORDER BY id ASC 
            LIMIT 5;
        """)
        print(f"\n[3. MUESTRA DE TEOREMAS DE RETRACCIÓN Y PRECISIÓN (LIMIT 5)]")
        for row in cur.fetchall():
            thm_id, topic, status, staging = row
            staging_str = staging if staging else "Núcleo Analítico"
            print(f"  • Teorema {thm_id:04d} [{status}]: {topic}")
            print(f"    └ Implementación física: {staging_str}")

        cur.close()
        conn.close()
        print("\n[RESULTADO]: Base de datos sincronizada. Exit Code 0.")
        print("=" * 70)

    except Exception as e:
        print(f"\n[ERROR DE CONEXIÓN POSTGRESQL]: {e}")
        print("Asegúrate de que el servicio PostgreSQL 16 esté activo en el puerto 5432.")
        print("=" * 70)

if __name__ == "__main__":
    run_lab3()

import psycopg

def get_pg_conn(db_name="polydim_active_db"):
    return psycopg.connect(f"dbname={db_name} user=postgres host=127.0.0.1 port=5432")

def get_api_key(key_name):
    with get_pg_conn("polydim_active_db") as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT value FROM active_vault WHERE key_name = %s AND category = 'api_key'", (key_name,))
            row = cur.fetchone()
            return row[0] if row else None

if __name__ == "__main__":
    print("Testing PostgreSQL connection via psycopg...")
    with get_pg_conn("polydim_active_db") as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT key_name, category FROM active_vault WHERE category='api_key' ORDER BY key_name LIMIT 10")
            rows = cur.fetchall()
            print(f"Retrieved {len(rows)} keys successfully from PostgreSQL.")
            for r in rows:
                print(" -", r[0], "(category:", r[1] + ")")

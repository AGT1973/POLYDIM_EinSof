import psycopg

with psycopg.connect("dbname=polydim_active_db user=postgres host=127.0.0.1 port=5432") as conn:
    with conn.cursor() as cur:
        cur.execute("SELECT key_name, category, substr(value, 1, 15) FROM active_vault WHERE key_name ILIKE '%openrouter%' OR value ILIKE 'sk-or%' OR value ILIKE 'sk-%'")
        for r in cur.fetchall():
            print(r)

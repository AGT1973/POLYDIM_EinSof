import psycopg, json
conn = psycopg.connect("dbname=polydim_active_db user=postgres host=127.0.0.1")
cur = conn.cursor()
cur.execute("SELECT key_name, value FROM active_vault WHERE key_name ILIKE '%email%' OR value ILIKE '%@%'")
rows = cur.fetchall()
print(json.dumps(rows, default=str))

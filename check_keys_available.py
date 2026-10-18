import psycopg2

conn = psycopg2.connect(
    dbname='polydim_active_db',
    host='localhost',
    port=5432,
    user='postgres',
    password='postgres'
)
cur = conn.cursor()
cur.execute("SELECT key_name FROM active_vault WHERE category='api_key'")
keys = [r[0] for r in cur.fetchall()]
print("AVAILABLE_KEYS:", keys)
conn.close()
